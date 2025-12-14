"""Chat API routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ...database import get_db
from ...core.chat_service import ChatService
from ...models.schemas import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatSessionListResponse,
    ChatMessageRequest,
    ErrorResponse
)

router = APIRouter(tags=["chat"])
chat_service = ChatService()


@router.post("/chat/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
def create_chat_session(
    request: ChatSessionCreate,
    db: Session = Depends(get_db)
):
    """Create a new chat session."""
    session = chat_service.create_session(db, title=request.title)
    return session


@router.get("/chat/sessions", response_model=ChatSessionListResponse)
def list_chat_sessions(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List all chat sessions."""
    sessions = chat_service.list_sessions(db, limit=limit)
    return {
        "sessions": sessions,
        "total": len(sessions)
    }


@router.get("/chat/sessions/{session_id}", response_model=ChatSessionResponse)
def get_chat_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific chat session with message history."""
    session = chat_service.get_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    return session


@router.delete("/chat/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Delete a chat session."""
    success = chat_service.delete_session(db, session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    return None


@router.post("/chat/sessions/{session_id}/messages")
async def send_chat_message(
    session_id: int,
    request: ChatMessageRequest,
    db: Session = Depends(get_db)
):
    """
    Send a message and stream the response.

    Returns a Server-Sent Events (SSE) stream of the response.
    """
    # Verify session exists
    session = chat_service.get_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    async def event_stream():
        """Generate SSE events."""
        try:
            async for chunk in chat_service.chat_stream(
                db=db,
                session_id=session_id,
                message=request.message,
                provider=request.provider,
                model=request.model,
                include_document_context=request.include_context
            ):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
