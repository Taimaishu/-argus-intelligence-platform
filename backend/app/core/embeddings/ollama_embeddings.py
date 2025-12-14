"""Ollama embedding service for local LLMs."""

from typing import List
import ollama
from .base import BaseEmbedding, EmbeddingResult
from app.config import settings
from app.utils.logger import logger


class OllamaEmbeddingService(BaseEmbedding):
    """
    Ollama embedding service using local models.
    Privacy-first, uses your local Ollama installation.
    """

    def __init__(self, model_name: str = None, base_url: str = None):
        """
        Initialize Ollama embedding service.

        Args:
            model_name: Ollama model to use (default from settings)
            base_url: Ollama base URL (default from settings)
        """
        self.model_name = model_name or settings.OLLAMA_EMBEDDING_MODEL
        self.base_url = base_url or settings.OLLAMA_BASE_URL

        logger.info(f"Initializing Ollama embeddings with model: {self.model_name}")
        logger.info(f"Ollama URL: {self.base_url}")

        # Test connection and get model info
        try:
            # Generate a test embedding to verify model works
            test_result = ollama.embeddings(model=self.model_name, prompt="test")
            self.dimension = len(test_result["embedding"])
            logger.info(f"Ollama model ready. Dimension: {self.dimension}")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {str(e)}")
            logger.error(
                f"Make sure Ollama is running and model '{self.model_name}' is available"
            )
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
            response = ollama.embeddings(model=self.model_name, prompt=text)

            embedding = response["embedding"]

            return EmbeddingResult(
                embedding=embedding, model=self.model_name, dimension=len(embedding)
            )
        except Exception as e:
            logger.error(f"Failed to generate Ollama embedding: {str(e)}")
            raise

    def embed_batch(self, texts: List[str]) -> List[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of EmbeddingResult
        """
        results = []

        for i, text in enumerate(texts):
            if i > 0 and i % 10 == 0:
                logger.info(f"Processed {i}/{len(texts)} embeddings")

            result = self.embed_text(text)
            results.append(result)

        return results

    def get_dimension(self) -> int:
        """Get the dimension of embeddings."""
        return self.dimension

    def get_model_name(self) -> str:
        """Get the name of the model."""
        return self.model_name
