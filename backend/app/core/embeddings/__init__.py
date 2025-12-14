"""Embedding services package."""

from .base import BaseEmbedding, EmbeddingResult
from .local_embeddings import LocalEmbeddingService
from .ollama_embeddings import OllamaEmbeddingService
from .api_embeddings import OpenAIEmbeddingService, AnthropicEmbeddingService
from .factory import EmbeddingFactory

__all__ = [
    "BaseEmbedding",
    "EmbeddingResult",
    "LocalEmbeddingService",
    "OllamaEmbeddingService",
    "OpenAIEmbeddingService",
    "AnthropicEmbeddingService",
    "EmbeddingFactory",
]
