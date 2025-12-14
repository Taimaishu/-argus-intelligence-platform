"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from .enums import DocumentType, ProcessingStatus


# Document Schemas
class DocumentBase(BaseModel):
    """Base document schema."""
    filename: str
    file_type: DocumentType


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""
    file_path: str
    file_size: int


class DocumentResponse(DocumentBase):
    """Schema for document response."""
    id: int
    file_size: int
    title: Optional[str] = None
    author: Optional[str] = None
    processing_status: ProcessingStatus
    error_message: Optional[str] = None
    upload_date: datetime
    processed_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Schema for list of documents."""
    documents: List[DocumentResponse]
    total: int


# Upload Response
class UploadResponse(BaseModel):
    """Schema for file upload response."""
    message: str
    document: DocumentResponse


# Error Response
class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str


# Health Check
class HealthCheck(BaseModel):
    """Schema for health check response."""
    status: str
    version: str
    supported_file_types: List[str]


# Search Schemas
class SearchRequest(BaseModel):
    """Schema for search request."""
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=20, ge=1, le=100)
    document_ids: Optional[List[int]] = None


class SearchResultItem(BaseModel):
    """Schema for a single search result."""
    document_id: int
    document_title: str
    document_filename: str
    chunk_text: str
    snippet: str
    relevance_score: float
    chunk_index: int


class SearchResponse(BaseModel):
    """Schema for search response."""
    query: str
    results: List[SearchResultItem]
    total_results: int
    embedding_model: str


# Chat Schemas
class ChatMessageResponse(BaseModel):
    """Schema for chat message response."""
    id: int
    role: str
    content: str
    created_at: datetime
    model: Optional[str] = None

    class Config:
        from_attributes = True


class ChatSessionResponse(BaseModel):
    """Schema for chat session response."""
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageResponse] = []

    class Config:
        from_attributes = True


class ChatSessionCreate(BaseModel):
    """Schema for creating a chat session."""
    title: str = "New Chat"


class ChatMessageRequest(BaseModel):
    """Schema for sending a chat message."""
    message: str = Field(..., min_length=1, max_length=5000)
    include_context: bool = True


class ChatSessionListResponse(BaseModel):
    """Schema for list of chat sessions."""
    sessions: List[ChatSessionResponse]
    total: int
