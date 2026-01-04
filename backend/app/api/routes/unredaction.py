"""Unredaction API routes."""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional
from pathlib import Path
import shutil

from app.core.unredaction_service import UnredactionService
from app.utils.file_utils import (
    validate_file_size,
    get_file_extension,
    generate_unique_filename,
    ensure_upload_dir,
)
from app.utils.logger import logger

router = APIRouter(prefix="/unredaction", tags=["unredaction"])
unredaction_service = UnredactionService()


@router.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    use_ai: bool = True,
    use_ocr: bool = False
):
    """
    Analyze a document for redacted content and attempt recovery.

    Args:
        file: Document file (PDF or image)
        use_ai: Whether to use AI for prediction
        use_ocr: Whether to use OCR (requires Tesseract)

    Returns:
        Analysis results with detected redactions and predictions
    """
    temp_path = None

    try:
        # Validate file
        file_extension = get_file_extension(file.filename)
        supported_types = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']

        if file_extension.lower() not in supported_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_extension}. Supported: {', '.join(supported_types)}"
            )

        # Read and validate file size
        content = await file.read()
        file_size = len(content)

        if not validate_file_size(file_size):
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: 50 MB"
            )

        # Save temporarily
        upload_dir = ensure_upload_dir()
        unique_filename = generate_unique_filename(file.filename)
        temp_path = upload_dir / unique_filename

        with open(temp_path, 'wb') as f:
            f.write(content)

        logger.info(f"Analyzing document for redactions: {file.filename}")

        # Analyze document
        results = await unredaction_service.analyze_document(
            file_path=str(temp_path),
            use_ai=use_ai,
            use_ocr=use_ocr
        )

        # Format results for JSON response
        formatted_results = {
            "filename": file.filename,
            "file_type": file_extension,
            "total_pages": results.get("total_pages", 1),
            "summary": results.get("summary", {}),
            "redacted_regions": [
                {
                    "page": r.page if hasattr(r, 'page') else 1,
                    "bbox": r.bbox if hasattr(r, 'bbox') else r.get('bbox'),
                    "type": r.region_type if hasattr(r, 'region_type') else r.get('type'),
                    "context_before": r.context_before if hasattr(r, 'context_before') else "",
                    "context_after": r.context_after if hasattr(r, 'context_after') else "",
                }
                for r in results.get("redacted_regions", [])
            ],
            "predictions": [
                {
                    "original": p.original_text,
                    "predicted": p.predicted_text,
                    "confidence": round(p.confidence * 100, 1),
                    "method": p.method,
                    "context": p.context[:200] if len(p.context) > 200 else p.context
                }
                for p in results.get("predictions", [])
            ],
            "analysis_complete": True
        }

        logger.info(f"Analysis complete: {formatted_results['summary']}")

        return formatted_results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unredaction analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )
    finally:
        # Cleanup temporary file
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {str(e)}")


@router.get("/capabilities")
def get_capabilities():
    """
    Get current unredaction capabilities.

    Returns:
        Dictionary of available features and their status
    """
    capabilities = {
        "ai_inference": True,
        "pattern_matching": True,
        "ocr": False,  # Will be True once Tesseract is installed
        "supported_formats": {
            "pdf": True,
            "images": True
        },
        "confidence_levels": {
            "high": "≥80%",
            "medium": "50-79%",
            "low": "<50%"
        }
    }

    # Check if Tesseract is available
    try:
        import subprocess
        result = subprocess.run(['tesseract', '--version'], capture_output=True)
        if result.returncode == 0:
            capabilities["ocr"] = True
    except (FileNotFoundError, subprocess.SubprocessError):
        pass

    return capabilities
