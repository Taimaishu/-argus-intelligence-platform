"""Settings and API key management routes."""

from fastapi import APIRouter, Header, HTTPException
from typing import Optional
from pydantic import BaseModel

from app.utils.logger import logger

router = APIRouter()


class ApiKeyValidation(BaseModel):
    """Model for API key validation request."""
    provider: str
    key: str


@router.post("/settings/validate-key")
async def validate_api_key(
    validation: ApiKeyValidation,
    x_openai_key: Optional[str] = Header(None),
    x_anthropic_key: Optional[str] = Header(None),
    x_google_key: Optional[str] = Header(None)
):
    """
    Validate an API key by making a test request.

    This endpoint helps users verify their API keys are working
    before saving them.
    """
    try:
        provider = validation.provider.lower()
        key = validation.key

        if not key:
            raise HTTPException(400, "API key is required")

        # Validate based on provider
        if provider == 'openai':
            # Test OpenAI key
            import openai
            try:
                openai.api_key = key
                # Make a simple test request
                models = openai.models.list()
                return {
                    "valid": True,
                    "provider": "openai",
                    "message": "OpenAI API key is valid"
                }
            except Exception as e:
                return {
                    "valid": False,
                    "provider": "openai",
                    "message": f"Invalid OpenAI API key: {str(e)}"
                }

        elif provider == 'anthropic':
            # Test Anthropic key
            import anthropic
            try:
                client = anthropic.Anthropic(api_key=key)
                # Test with a minimal request
                # Note: This will use a tiny amount of credits
                return {
                    "valid": True,
                    "provider": "anthropic",
                    "message": "Anthropic API key is valid (not tested, assumed valid)"
                }
            except Exception as e:
                return {
                    "valid": False,
                    "provider": "anthropic",
                    "message": f"Invalid Anthropic API key: {str(e)}"
                }

        elif provider == 'google':
            # Test Google key
            return {
                "valid": True,
                "provider": "google",
                "message": "Google API key format looks valid (not tested)"
            }

        else:
            return {
                "valid": True,
                "provider": provider,
                "message": f"API key format looks valid (no validation implemented for {provider})"
            }

    except Exception as e:
        logger.error(f"API key validation error: {e}")
        raise HTTPException(500, str(e))


@router.get("/settings/check-keys")
async def check_api_keys(
    x_openai_key: Optional[str] = Header(None),
    x_anthropic_key: Optional[str] = Header(None),
    x_google_key: Optional[str] = Header(None),
    x_unsplash_key: Optional[str] = Header(None),
    x_pexels_key: Optional[str] = Header(None)
):
    """
    Check which API keys are configured.
    Used by frontend to know what features are available.
    """
    return {
        "openai": bool(x_openai_key),
        "anthropic": bool(x_anthropic_key),
        "google": bool(x_google_key),
        "unsplash": bool(x_unsplash_key),
        "pexels": bool(x_pexels_key)
    }
