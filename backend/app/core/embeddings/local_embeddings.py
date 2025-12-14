"""Local embedding service using sentence-transformers."""

from typing import List
from sentence_transformers import SentenceTransformer
from .base import BaseEmbedding, EmbeddingResult
from app.utils.logger import logger


class LocalEmbeddingService(BaseEmbedding):
    """
    Local embedding service using sentence-transformers.
    Privacy-first, runs entirely offline on CPU/GPU.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize local embedding service.

        Args:
            model_name: Name of sentence-transformers model
                       Default: all-MiniLM-L6-v2 (80MB, fast, good quality)
                       Alternatives:
                       - all-mpnet-base-v2 (420MB, better quality)
                       - all-MiniLM-L12-v2 (120MB, balanced)
        """
        self.model_name = model_name
        logger.info(f"Loading sentence-transformers model: {model_name}")

        try:
            self.model = SentenceTransformer(model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"Model loaded successfully. Dimension: {self.dimension}")
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {str(e)}")
            raise

    def embed_text(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            EmbeddingResult with vector
        """
        try:
            # Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True)

            return EmbeddingResult(
                embedding=embedding.tolist(),
                model=self.model_name,
                dimension=self.dimension
            )
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise

    def embed_batch(self, texts: List[str]) -> List[EmbeddingResult]:
        """
        Generate embeddings for multiple texts (batch processing).

        Args:
            texts: List of texts to embed

        Returns:
            List of EmbeddingResult
        """
        try:
            # Batch encode for efficiency
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=len(texts) > 10
            )

            return [
                EmbeddingResult(
                    embedding=emb.tolist(),
                    model=self.model_name,
                    dimension=self.dimension
                )
                for emb in embeddings
            ]
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {str(e)}")
            raise

    def get_dimension(self) -> int:
        """Get the dimension of embeddings."""
        return self.dimension

    def get_model_name(self) -> str:
        """Get the name of the model."""
        return self.model_name
