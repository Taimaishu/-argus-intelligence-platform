"""Health check API route."""

from fastapi import APIRouter
from app.models.schemas import HealthCheck
from app.core.document_processor import DocumentProcessor

router = APIRouter(tags=["health"])
document_processor = DocumentProcessor()


@router.get("/health", response_model=HealthCheck)
def health_check():
    """
    Health check endpoint.

    Returns:
        Health status and application info
    """
    return HealthCheck(
        status="healthy",
        version="0.1.0",
        supported_file_types=sorted(list(document_processor.get_supported_extensions()))
    )
