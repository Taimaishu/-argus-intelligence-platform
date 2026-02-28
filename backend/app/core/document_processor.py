"""Document processing orchestrator."""

from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime

from app.core.parsers import ParserFactory, ParsedDocument
from app.core.embeddings.factory import EmbeddingFactory
from app.core.vector_store import VectorStore
from app.utils.text_utils import chunk_text_by_paragraphs
from app.utils.logger import logger
from app.models.database_models import Document, DocumentChunk
from app.models.enums import DocumentType, ProcessingStatus
from sqlalchemy.orm import Session


class DocumentProcessor:
    """Orchestrates document parsing, chunking, and embedding."""

    def __init__(self):
        """Initialize document processor."""
        self.parser_factory = ParserFactory()
        self.embedding_service = None
        self.vector_store = None

    def process_document(
        self, file_path: str, document: Document, db: Session
    ) -> List[DocumentChunk]:
        """
        Process document: parse, chunk, and create database entries.

        Args:
            file_path: Path to document file
            document: Document model instance
            db: Database session

        Returns:
            List of created DocumentChunk instances

        Raises:
            Exception: If processing fails
        """
        try:
            logger.info(f"Processing document: {document.filename}")

            # Convert relative path to absolute if needed
            file_path_obj = Path(file_path)
            if not file_path_obj.is_absolute():
                file_path_obj = file_path_obj.resolve()
                file_path = str(file_path_obj)
                logger.info(f"Converted relative path to absolute: {file_path}")

            # Update status to processing
            document.processing_status = ProcessingStatus.PROCESSING
            db.commit()

            # Parse document
            parser = self.parser_factory.get_parser(file_path)
            if not parser:
                raise ValueError(f"No parser available for {file_path}")

            parsed_doc: ParsedDocument = parser.parse(file_path)

            # Update document with extracted metadata
            if parsed_doc.title:
                document.title = parsed_doc.title
            if parsed_doc.author:
                document.author = parsed_doc.author

            # Chunk the text
            chunks_text = chunk_text_by_paragraphs(parsed_doc.text)

            logger.info(f"Created {len(chunks_text)} chunks from document")

            # Create DocumentChunk entries
            document_chunks = []
            for idx, chunk_text in enumerate(chunks_text):
                chunk = DocumentChunk(
                    document_id=document.id,
                    chunk_index=idx,
                    chunk_text=chunk_text,
                    # embedding_id will be set later by embedding service
                )
                document_chunks.append(chunk)
                db.add(chunk)

            # CRITICAL: Flush to assign chunk.id before generating embeddings
            db.flush()
            logger.info("Chunks flushed to database, IDs assigned")

            # Mark parsing as completed
            document.processing_status = ProcessingStatus.COMPLETED
            document.processed_date = datetime.utcnow()

            # Generate embeddings for chunks (separate status tracking)
            try:
                document.embedding_status = ProcessingStatus.PROCESSING
                self._generate_embeddings(document_chunks, db)
                document.embedding_status = ProcessingStatus.COMPLETED
                document.embedding_error_message = None
                logger.info("Embeddings generated successfully")
            except Exception as e:
                logger.error(f"Failed to generate embeddings: {str(e)}")
                document.embedding_status = ProcessingStatus.FAILED
                document.embedding_error_message = str(e)
                logger.warning("Document processed but embeddings failed")

            db.commit()

            logger.info(f"Successfully processed document: {document.filename}")

            return document_chunks

        except Exception as e:
            logger.error(f"Failed to process document {document.filename}: {str(e)}")

            # Mark as failed
            document.processing_status = ProcessingStatus.FAILED
            document.error_message = str(e)
            db.commit()

            raise

    def is_supported_file(self, file_path: str) -> bool:
        """
        Check if file type is supported.

        Args:
            file_path: Path to file

        Returns:
            True if supported, False otherwise
        """
        return self.parser_factory.is_supported(file_path)

    def get_supported_extensions(self) -> set[str]:
        """
        Get all supported file extensions.

        Returns:
            Set of supported extensions
        """
        return self.parser_factory.get_supported_extensions()

    def _generate_embeddings(self, document_chunks: List[DocumentChunk], db: Session):
        """
        Generate embeddings for document chunks and store in vector database.

        Args:
            document_chunks: List of DocumentChunk instances
            db: Database session
        """
        if not document_chunks:
            return

        logger.info(f"Generating embeddings for {len(document_chunks)} chunks")

        # Lazy load embedding service and vector store
        if self.embedding_service is None:
            self.embedding_service = EmbeddingFactory.get_singleton()

        if self.vector_store is None:
            self.vector_store = VectorStore()

        # Extract texts to embed
        texts = [chunk.chunk_text for chunk in document_chunks]

        # Generate embeddings in batch
        embedding_results = self.embedding_service.embed_batch(texts)

        # Prepare data for ChromaDB
        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for chunk, emb_result in zip(document_chunks, embedding_results):
            # Deterministic ID format: doc_{document_id}_chunk_{chunk_index}
            chunk_id = f"doc_{chunk.document_id}_chunk_{chunk.chunk_index}"

            # CRITICAL: chunk.id must exist after db.flush()
            if not chunk.id:
                raise ValueError(f"Chunk ID not assigned for chunk {chunk.chunk_index}. DB flush may have failed.")

            ids.append(chunk_id)
            embeddings.append(emb_result.embedding)
            documents.append(chunk.chunk_text)
            metadatas.append(
                {
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                    "chunk_db_id": chunk.id,  # Never 0 - will raise error if missing
                }
            )

            # Store embedding ID in database
            chunk.embedding_id = chunk_id

        # Add to vector store (will upsert if IDs exist)
        self.vector_store.add(
            ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas
        )

        db.commit()

        logger.info(f"Successfully generated and stored {len(embeddings)} embeddings")
