"""Document management API routes."""

import os
from typing import List
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.database_models import Document
from app.models.schemas import DocumentResponse, DocumentListResponse, UploadResponse
from app.models.enums import DocumentType, ProcessingStatus
from app.core.document_processor import DocumentProcessor
from app.utils.file_utils import (
    validate_file_size,
    get_file_extension,
    generate_unique_filename,
    ensure_upload_dir,
    get_file_type_from_extension,
)
from app.utils.logger import logger

router = APIRouter(prefix="/documents", tags=["documents"])
document_processor = DocumentProcessor()


def process_document_background(file_path: str, document_id: int):
    """Background task to process document."""
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document_processor.process_document(file_path, document, db)
    except Exception as e:
        logger.error(f"Background processing failed: {str(e)}")
    finally:
        db.close()


@router.post("/upload", response_model=UploadResponse, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a document for processing.

    Args:
        file: Uploaded file
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        Upload response with document info

    Raises:
        HTTPException: If upload fails or file is invalid
    """
    try:
        # Get file extension and validate
        file_extension = get_file_extension(file.filename)

        if not document_processor.is_supported_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_extension}. Supported types: {', '.join(document_processor.get_supported_extensions())}",
            )

        # Read file content to validate size
        content = await file.read()
        file_size = len(content)

        if not validate_file_size(file_size):
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {file_size / (1024*1024):.2f} MB",
            )

        # Generate unique filename and save
        upload_dir = ensure_upload_dir()
        unique_filename = generate_unique_filename(file.filename)
        file_path = upload_dir / unique_filename

        # Write file to disk
        with open(file_path, "wb") as f:
            f.write(content)

        logger.info(f"Saved file: {file_path}")

        # Determine document type
        doc_type = get_file_type_from_extension(file_extension)

        # Create document record
        document = Document(
            filename=file.filename,
            file_path=str(file_path),
            file_type=DocumentType(doc_type),
            file_size=file_size,
            processing_status=ProcessingStatus.PENDING,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        # Add background task to process document
        background_tasks.add_task(
            process_document_background, str(file_path), document.id
        )

        return UploadResponse(
            message="File uploaded successfully. Processing started.",
            document=DocumentResponse.model_validate(document),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("", response_model=DocumentListResponse)
def list_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    List all documents.

    Args:
        skip: Number of documents to skip
        limit: Maximum number of documents to return
        db: Database session

    Returns:
        List of documents
    """
    documents = (
        db.query(Document)
        .order_by(Document.upload_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    total = db.query(Document).count()

    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(doc) for doc in documents],
        total=total,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    """
    Get a specific document by ID.

    Args:
        document_id: Document ID
        db: Database session

    Returns:
        Document details

    Raises:
        HTTPException: If document not found
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentResponse.model_validate(document)


@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """
    Delete a document.

    Args:
        document_id: Document ID
        db: Database session

    Raises:
        HTTPException: If document not found
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file from disk
    try:
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
    except Exception as e:
        logger.error(f"Failed to delete file {document.file_path}: {str(e)}")

    # Delete from database (cascades to chunks)
    db.delete(document)
    db.commit()

    return None
