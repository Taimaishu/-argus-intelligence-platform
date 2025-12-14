"""ChromaDB vector store wrapper."""

from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from pathlib import Path

from app.config import settings
from app.utils.logger import logger


class VectorStore:
    """
    Wrapper for ChromaDB vector database.
    Handles storage and retrieval of document embeddings.
    """

    def __init__(self, collection_name: str = "documents"):
        """
        Initialize ChromaDB vector store.

        Args:
            collection_name: Name of the collection to use
        """
        self.collection_name = collection_name

        # Ensure ChromaDB directory exists
        chroma_path = Path(settings.CHROMA_PERSIST_DIRECTORY)
        chroma_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initializing ChromaDB at: {chroma_path}")

        # Initialize ChromaDB client in persistent mode
        self.client = chromadb.PersistentClient(
            path=str(chroma_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Get or create collection
        try:
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
            logger.info(f"Collection '{collection_name}' ready. Count: {self.collection.count()}")
        except Exception as e:
            logger.error(f"Failed to initialize collection: {str(e)}")
            raise

    def add(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Add embeddings to the vector store.

        Args:
            ids: Unique IDs for each embedding
            embeddings: List of embedding vectors
            documents: List of text documents
            metadatas: Optional list of metadata dicts
        """
        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            logger.info(f"Added {len(ids)} embeddings to collection")
        except Exception as e:
            logger.error(f"Failed to add embeddings: {str(e)}")
            raise

    def query(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Query the vector store for similar documents.

        Args:
            query_embeddings: Query embedding vectors
            n_results: Number of results to return
            where: Metadata filter (e.g., {"document_id": 123})
            where_document: Document content filter

        Returns:
            Query results with ids, documents, distances, and metadatas
        """
        try:
            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where,
                where_document=where_document
            )
            return results
        except Exception as e:
            logger.error(f"Failed to query vector store: {str(e)}")
            raise

    def get(
        self,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get embeddings by ID or filter.

        Args:
            ids: List of IDs to retrieve
            where: Metadata filter
            limit: Maximum number of results

        Returns:
            Retrieved embeddings and metadata
        """
        try:
            return self.collection.get(
                ids=ids,
                where=where,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Failed to get from vector store: {str(e)}")
            raise

    def delete(
        self,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None
    ):
        """
        Delete embeddings by ID or filter.

        Args:
            ids: List of IDs to delete
            where: Metadata filter
        """
        try:
            self.collection.delete(
                ids=ids,
                where=where
            )
            logger.info(f"Deleted embeddings from collection")
        except Exception as e:
            logger.error(f"Failed to delete from vector store: {str(e)}")
            raise

    def count(self) -> int:
        """
        Get the number of embeddings in the collection.

        Returns:
            Count of embeddings
        """
        return self.collection.count()

    def reset(self):
        """Reset the collection (delete all data)."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.warning(f"Collection '{self.collection_name}' has been reset")
        except Exception as e:
            logger.error(f"Failed to reset collection: {str(e)}")
            raise
