"""AI Model management API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import requests
import ollama

from app.config import settings
from app.utils.logger import logger

router = APIRouter(tags=["models"])


class ModelInfo(BaseModel):
    """Model information."""

    name: str
    provider: str
    size: str = "unknown"
    modified: str = ""


class PullModelRequest(BaseModel):
    """Request to pull an Ollama model."""

    model_name: str


class ChatModelRequest(BaseModel):
    """Request to set chat model."""

    provider: str  # ollama, openai, anthropic
    model_name: str


# Recommended models for different tasks
RECOMMENDED_MODELS = {
    "chat": {
        "ollama": [
            "llama3.1:8b",
            "qwen2.5:14b",
            "deepseek-r1:7b",
            "mistral:7b",
            "gemma2:9b",
        ],
        "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
        "anthropic": [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
        ],
    },
    "embeddings": {
        "ollama": ["nomic-embed-text", "mxbai-embed-large", "all-minilm"],
        "openai": ["text-embedding-3-large", "text-embedding-3-small"],
    },
    "code": {"ollama": ["deepseek-coder:6.7b", "codellama:13b", "qwen2.5-coder:7b"]},
}


@router.get("/models/ollama/list")
def list_ollama_models():
    """List all available Ollama models."""
    try:
        models_list = ollama.list()

        models = []
        for model in models_list.get("models", []):
            models.append(
                {
                    "name": model.get("model", model.get("name", "unknown")),
                    "provider": "ollama",
                    "size": model.get("size", "unknown"),
                    "modified": model.get("modified_at", ""),
                    "details": model.get("details", {}),
                }
            )

        return {
            "models": models,
            "count": len(models),
            "ollama_url": settings.OLLAMA_BASE_URL,
        }
    except Exception as e:
        logger.error(f"Error listing Ollama models: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to list Ollama models: {str(e)}"
        )


@router.post("/models/ollama/pull")
async def pull_ollama_model(request: PullModelRequest):
    """
    Pull/download an Ollama model.

    This streams the download progress.
    """
    try:
        logger.info(f"Pulling Ollama model: {request.model_name}")

        # Pull the model (this will stream the download)
        stream = ollama.pull(request.model_name, stream=True)

        # Collect progress information
        progress_info = []
        for chunk in stream:
            progress_info.append(chunk)
            if "status" in chunk and chunk["status"] == "success":
                break

        return {
            "success": True,
            "model": request.model_name,
            "message": f"Successfully pulled {request.model_name}",
            "progress": progress_info[-1] if progress_info else {},
        }
    except Exception as e:
        logger.error(f"Error pulling Ollama model {request.model_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to pull model {request.model_name}: {str(e)}",
        )


@router.delete("/models/ollama/{model_name}")
def delete_ollama_model(model_name: str):
    """Delete an Ollama model."""
    try:
        ollama.delete(model_name)
        logger.info(f"Deleted Ollama model: {model_name}")
        return {"success": True, "message": f"Successfully deleted {model_name}"}
    except Exception as e:
        logger.error(f"Error deleting Ollama model {model_name}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete model {model_name}: {str(e)}"
        )


@router.get("/models/recommendations")
def get_model_recommendations():
    """Get recommended models for different tasks."""
    return {
        "recommendations": RECOMMENDED_MODELS,
        "current_settings": {
            "embedding_provider": settings.DEFAULT_EMBEDDING_PROVIDER,
            "llm_provider": settings.DEFAULT_LLM_PROVIDER,
            "ollama_url": settings.OLLAMA_BASE_URL,
        },
    }


@router.get("/models/available")
def get_available_models():
    """
    Get all available models across providers.

    Returns models from Ollama (local) and lists recommended API models.
    """
    available = {"ollama": [], "openai": [], "anthropic": []}

    # Get Ollama models
    try:
        models_list = ollama.list()
        for model in models_list.get("models", []):
            available["ollama"].append(
                {
                    "name": model.get("model", model.get("name", "unknown")),
                    "size": model.get("size", "unknown"),
                    "available": True,
                }
            )
    except Exception as e:
        logger.warning(f"Could not fetch Ollama models: {e}")

    # OpenAI models (if API key is configured)
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your_key_here":
        available["openai"] = [
            {"name": model, "available": True}
            for model in RECOMMENDED_MODELS["chat"]["openai"]
        ]

    # Anthropic models (if API key is configured)
    if settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY != "your_key_here":
        available["anthropic"] = [
            {"name": model, "available": True}
            for model in RECOMMENDED_MODELS["chat"]["anthropic"]
        ]

    return available


@router.get("/models/ollama/running")
def get_running_models():
    """Get currently running Ollama models."""
    try:
        response = requests.get(f"{settings.OLLAMA_BASE_URL}/api/ps", timeout=5)
        if response.ok:
            return response.json()
        return {"models": []}
    except Exception as e:
        logger.error(f"Error getting running models: {e}")
        return {"models": [], "error": str(e)}


@router.post("/models/ollama/unload/{model_name}")
def unload_ollama_model(model_name: str):
    """Unload a running Ollama model from memory."""
    try:
        # Send empty request to unload
        response = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={"model": model_name, "keep_alive": 0},
            timeout=5,
        )
        return {"success": True, "message": f"Unloaded {model_name} from memory"}
    except Exception as e:
        logger.error(f"Error unloading model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/providers/status")
def get_providers_status():
    """Check which AI providers are available/configured."""
    status = {
        "ollama": {
            "available": False,
            "configured": True,
            "url": settings.OLLAMA_BASE_URL,
        },
        "openai": {
            "available": bool(
                settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your_key_here"
            ),
            "configured": bool(settings.OPENAI_API_KEY),
        },
        "anthropic": {
            "available": bool(
                settings.ANTHROPIC_API_KEY
                and settings.ANTHROPIC_API_KEY != "your_key_here"
            ),
            "configured": bool(settings.ANTHROPIC_API_KEY),
        },
    }

    # Check if Ollama is actually running
    try:
        response = requests.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=2)
        status["ollama"]["available"] = response.ok
    except:
        status["ollama"]["available"] = False

    return status
