"""Semantic search engine."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from app.core.embeddings.factory import EmbeddingFactory
from app.core.vector_store import VectorStore
from app.models.database_models import Document, DocumentChunk
from app.utils.text_utils import extract_snippet
from app.utils.logger import logger
from sqlalchemy.orm import Session


@dataclass
class SearchResult:
    """Search result data structure."""

    document_id: int
    document_title: str
    document_filename: str
    chunk_text: str
    snippet: str
    relevance_score: float
    chunk_index: int


class SearchEngine:
    """
    Semantic search engine for querying documents.
    Uses vector similarity to find relevant content.
    """

    def __init__(self):
        """Initialize search engine."""
        self.embedding_service = None
        self.vector_store = None

    def search(
        self,
        query: str,
        db: Session,
        top_k: int = 20,
        document_ids: Optional[List[int]] = None,
    ) -> List[SearchResult]:
        """
        Perform semantic search across documents.

        Args:
            query: Natural language search query
            db: Database session
            top_k: Number of results to return
            document_ids: Optional list of document IDs to filter by

        Returns:
            List of SearchResult objects ranked by relevance
        """
        logger.info(f"Searching for: '{query}' (top_k={top_k})")

        # Lazy load services
        if self.embedding_service is None:
            self.embedding_service = EmbeddingFactory.get_singleton()

        if self.vector_store is None:
            self.vector_store = VectorStore()

        # Generate query embedding
        query_result = self.embedding_service.embed_text(query)
        query_embedding = query_result.embedding

        # Build metadata filter if document_ids provided
        where_filter = None
        if document_ids:
            # ChromaDB uses $in operator for list filtering
            where_filter = {"document_id": {"$in": document_ids}}

        # Query vector store
        results = self.vector_store.query(
            query_embeddings=[query_embedding], n_results=top_k, where=where_filter
        )

        # Process results
        search_results = []

        if not results["ids"] or not results["ids"][0]:
            logger.info("No results found")
            return []

        for i in range(len(results["ids"][0])):
            chunk_id = results["ids"][0][i]
            distance = results["distances"][0][i]
            metadata = results["metadatas"][0][i]
            chunk_text = results["documents"][0][i]

            # Convert distance to similarity score (cosine similarity)
            # ChromaDB cosine distance: 0 = identical, 2 = opposite
            # Convert to similarity: 1 = identical, 0 = opposite
            relevance_score = 1 - (distance / 2)

            # Get document info from database
            document_id = metadata.get("document_id")
            chunk_index = metadata.get("chunk_index", 0)

            document = db.query(Document).filter(Document.id == document_id).first()

            if not document:
                logger.warning(f"Document {document_id} not found in database")
                continue

            # Extract snippet around query terms
            snippet = extract_snippet(chunk_text, query, context_length=150)

            search_results.append(
                SearchResult(
                    document_id=document_id,
                    document_title=document.title or document.filename,
                    document_filename=document.filename,
                    chunk_text=chunk_text,
                    snippet=snippet,
                    relevance_score=round(relevance_score, 4),
                    chunk_index=chunk_index,
                )
            )

        logger.info(f"Found {len(search_results)} results")
        return search_results

    def get_similar_chunks(
        self, document_id: int, chunk_index: int, db: Session, top_k: int = 5
    ) -> List[SearchResult]:
        """
        Find similar chunks to a given chunk (for "related documents" feature).

        Args:
            document_id: ID of the document
            chunk_index: Index of the chunk
            db: Database session
            top_k: Number of similar chunks to return

        Returns:
            List of similar SearchResult objects
        """
        # Get the chunk from database
        chunk = (
            db.query(DocumentChunk)
            .filter(
                DocumentChunk.document_id == document_id,
                DocumentChunk.chunk_index == chunk_index,
            )
            .first()
        )

        if not chunk or not chunk.embedding_id:
            logger.warning(
                f"Chunk not found or no embedding: doc={document_id}, idx={chunk_index}"
            )
            return []

        # Use the chunk text as the query
        return self.search(
            query=chunk.chunk_text,
            db=db,
            top_k=top_k + 5,  # Get extra to filter out same document
        )

    def get_document_summary(self, document_id: int, db: Session) -> Dict[str, Any]:
        """
        Get summary statistics for a document's searchability.

        Args:
            document_id: ID of the document
            db: Database session

        Returns:
            Dictionary with summary info
        """
        document = db.query(Document).filter(Document.id == document_id).first()

        if not document:
            return {}

        chunk_count = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .count()
        )

        embedded_count = (
            db.query(DocumentChunk)
            .filter(
                DocumentChunk.document_id == document_id,
                DocumentChunk.embedding_id.isnot(None),
            )
            .count()
        )

        return {
            "document_id": document_id,
            "filename": document.filename,
            "title": document.title,
            "total_chunks": chunk_count,
            "embedded_chunks": embedded_count,
            "embedding_coverage": (
                round(embedded_count / chunk_count * 100, 2) if chunk_count > 0 else 0
            ),
        }
