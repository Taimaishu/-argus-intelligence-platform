"""
Application configuration module.
Loads settings from environment variables using pydantic-settings.
"""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="allow"
    )

    # Application Settings
    APP_NAME: str = "Argus Intelligence Platform"
    DEBUG: bool = Field(default=False)  # Secure default: False (must explicitly enable for dev)
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "sqlite:///./storage/database/research_tool.db"

    # Vector Database
    CHROMA_PERSIST_DIRECTORY: str = "./storage/chromadb"

    # File Storage
    UPLOAD_DIR: str = "./storage/uploads"
    MAX_UPLOAD_SIZE_MB: int = 50

    # AI Provider Selection
    DEFAULT_EMBEDDING_PROVIDER: str = "local"  # local, openai, anthropic, ollama
    DEFAULT_LLM_PROVIDER: str = "ollama"  # ollama, openai, anthropic, groq, deepseek

    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_EMBEDDING_MODEL: str = "llama3.2:1b"
    OLLAMA_LLM_MODEL: str = "gurubot/llama3-guru-uncensored:latest"

    # OpenAI API
    OPENAI_API_KEY: str = Field(default="")

    # Anthropic API
    ANTHROPIC_API_KEY: str = Field(default="")

    # Alternative AI APIs
    OPENROUTER_API_KEY: str = Field(default="")
    DEEPSEEK_API_KEY: str = Field(default="")
    GROQ_API_KEY: str = Field(default="")
    GOOGLE_API_KEY: str = Field(default="")
    GROK_API_KEY: str = Field(default="")

    # OSINT/Security APIs
    SHODAN_API_KEY: str = Field(default="")
    VT_API_KEY: str = Field(default="")
    HIBP_API_KEY: str = Field(default="")  # Have I Been Pwned

    # CORS Settings (secure default: empty list, fails closed)
    # Set CORS_ORIGINS in .env for development, e.g.:
    # CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
    CORS_ORIGINS: List[str] = Field(default_factory=list)

    # Logging
    LOG_LEVEL: str = "INFO"

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    API_KEY: str = Field(default="")  # Required for special endpoints when FEATURE_* flags are enabled

    # Rate Limiting (requests per minute)
    RATE_LIMIT: str = Field(default="100/minute")  # Production-safe default

    # Feature Flags (require explicit enablement)
    FEATURE_EPSTEIN_MODE: bool = Field(default=False)  # Enable Epstein-specific automation endpoints
    FEATURE_URL_EXTRACTION: bool = Field(default=False)  # Enable URL extraction in chat (SSRF risk)

    # Chunking Strategy
    CHUNK_SIZE: int = 1000  # tokens
    CHUNK_OVERLAP: int = 100  # tokens

    # Search Settings
    SEARCH_TOP_K: int = 20
    SIMILARITY_THRESHOLD: float = 0.7

    @property
    def max_upload_size_bytes(self) -> int:
        """Convert MB to bytes for file upload limit."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


# Global settings instance
settings = Settings()
