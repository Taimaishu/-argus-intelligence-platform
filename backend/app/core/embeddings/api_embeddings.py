"""API-based embedding services (OpenAI, Anthropic)."""

from typing import List
from openai import OpenAI
from .base import BaseEmbedding, EmbeddingResult
from app.config import settings
from app.utils.logger import logger


class OpenAIEmbeddingService(BaseEmbedding):
    """OpenAI embedding service using text-embedding-3-small."""

    def __init__(self, model_name: str = "text-embedding-3-small", api_key: str = None):
        """
        Initialize OpenAI embedding service.

        Args:
            model_name: OpenAI embedding model
            api_key: OpenAI API key (default from settings)
        """
        self.model_name = model_name
        self.dimension = 1536  # text-embedding-3-small dimension

        api_key = api_key or settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OpenAI API key not configured")

        self.client = OpenAI(api_key=api_key)
        logger.info(f"OpenAI embeddings initialized with model: {model_name}")

    def embed_text(self, text: str) -> EmbeddingResult:
        """Generate embedding for a single text."""
        try:
            response = self.client.embeddings.create(
                model=self.model_name,
                input=text
            )

            embedding = response.data[0].embedding

            return EmbeddingResult(
                embedding=embedding,
                model=self.model_name,
                dimension=len(embedding)
            )
        except Exception as e:
            logger.error(f"Failed to generate OpenAI embedding: {str(e)}")
            raise

    def embed_batch(self, texts: List[str]) -> List[EmbeddingResult]:
        """Generate embeddings for multiple texts."""
        try:
            # OpenAI supports batch embeddings
            response = self.client.embeddings.create(
                model=self.model_name,
                input=texts
            )

            return [
                EmbeddingResult(
                    embedding=item.embedding,
                    model=self.model_name,
                    dimension=len(item.embedding)
                )
                for item in response.data
            ]
        except Exception as e:
            logger.error(f"Failed to generate OpenAI batch embeddings: {str(e)}")
            raise

    def get_dimension(self) -> int:
        """Get the dimension of embeddings."""
        return self.dimension

    def get_model_name(self) -> str:
        """Get the name of the model."""
        return self.model_name


class AnthropicEmbeddingService(BaseEmbedding):
    """
    Anthropic doesn't provide native embeddings yet.
    This is a placeholder that uses Voyage AI (Anthropic's recommended provider).
    For now, falls back to local embeddings.
    """

    def __init__(self):
        """Initialize Anthropic embedding service."""
        logger.warning("Anthropic doesn't provide native embeddings. Using local fallback.")
        from .local_embeddings import LocalEmbeddingService
        self.fallback = LocalEmbeddingService()

    def embed_text(self, text: str) -> EmbeddingResult:
        """Generate embedding using fallback."""
        return self.fallback.embed_text(text)

    def embed_batch(self, texts: List[str]) -> List[EmbeddingResult]:
        """Generate embeddings using fallback."""
        return self.fallback.embed_batch(texts)

    def get_dimension(self) -> int:
        """Get the dimension of embeddings."""
        return self.fallback.get_dimension()

    def get_model_name(self) -> str:
        """Get the name of the model."""
        return f"local-fallback-{self.fallback.get_model_name()}"
