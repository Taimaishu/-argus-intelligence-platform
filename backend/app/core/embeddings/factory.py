"""Embedding service factory."""

from .base import BaseEmbedding
from .local_embeddings import LocalEmbeddingService
from .ollama_embeddings import OllamaEmbeddingService
from .api_embeddings import OpenAIEmbeddingService, AnthropicEmbeddingService
from app.config import settings
from app.utils.logger import logger


class EmbeddingFactory:
    """Factory for creating embedding services."""

    _instance = None

    @staticmethod
    def get_embedding_service(provider: str = None) -> BaseEmbedding:
        """
        Get embedding service based on provider.

        Args:
            provider: Embedding provider name (local, ollama, openai, anthropic)
                     If None, uses DEFAULT_EMBEDDING_PROVIDER from settings

        Returns:
            BaseEmbedding instance

        Raises:
            ValueError: If provider is not supported
        """
        provider = provider or settings.DEFAULT_EMBEDDING_PROVIDER
        provider = provider.lower()

        logger.info(f"Creating embedding service: {provider}")

        if provider == "local":
            return LocalEmbeddingService(model_name="all-MiniLM-L6-v2")

        elif provider == "ollama":
            return OllamaEmbeddingService()

        elif provider == "openai":
            return OpenAIEmbeddingService()

        elif provider == "anthropic":
            return AnthropicEmbeddingService()

        else:
            raise ValueError(
                f"Unsupported embedding provider: {provider}. "
                f"Supported: local, ollama, openai, anthropic"
            )

    @classmethod
    def get_singleton(cls, provider: str = None) -> BaseEmbedding:
        """
        Get singleton instance of embedding service.
        Reuses the same instance for efficiency.

        Args:
            provider: Embedding provider name

        Returns:
            BaseEmbedding instance
        """
        if cls._instance is None:
            cls._instance = cls.get_embedding_service(provider)

        return cls._instance

    @classmethod
    def reset_singleton(cls):
        """Reset singleton instance (useful for testing)."""
        cls._instance = None
