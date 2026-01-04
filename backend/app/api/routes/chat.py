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
    ErrorResponse,
)

router = APIRouter(tags=["chat"])
chat_service = ChatService()


@router.post(
    "/chat/sessions",
    response_model=ChatSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_chat_session(request: ChatSessionCreate, db: Session = Depends(get_db)):
    """Create a new chat session."""
    session = chat_service.create_session(
        db, title=request.title, system_prompt=request.system_prompt
    )
    return session


@router.get("/chat/sessions", response_model=ChatSessionListResponse)
def list_chat_sessions(limit: int = 50, db: Session = Depends(get_db)):
    """List all chat sessions."""
    sessions = chat_service.list_sessions(db, limit=limit)
    return {"sessions": sessions, "total": len(sessions)}


@router.get("/chat/sessions/{session_id}", response_model=ChatSessionResponse)
def get_chat_session(session_id: int, db: Session = Depends(get_db)):
    """Get a specific chat session with message history."""
    session = chat_service.get_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )
    return session


@router.patch("/chat/sessions/{session_id}", response_model=ChatSessionResponse)
def update_chat_session(
    session_id: int, request: ChatSessionCreate, db: Session = Depends(get_db)
):
    """Update a chat session title and/or system prompt."""
    session = chat_service.update_session(
        db, session_id, title=request.title, system_prompt=request.system_prompt
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )
    return session


@router.delete("/chat/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat_session(session_id: int, db: Session = Depends(get_db)):
    """Delete a chat session."""
    success = chat_service.delete_session(db, session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )
    return None


@router.post("/chat/sessions/{session_id}/messages")
async def send_chat_message(
    session_id: int, request: ChatMessageRequest, db: Session = Depends(get_db)
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
            detail=f"Session {session_id} not found",
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
                include_document_context=request.include_context,
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
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/chat/canvas-stream")
async def canvas_chat_stream(request: dict, db: Session = Depends(get_db)):
    """
    Canvas-specific chat with canvas manipulation capabilities.

    Expects:
    - message: str
    - canvas_context: dict with nodes and edges
    - provider: str
    - model: str (optional)
    - session_id: str (optional, defaults to 'canvas-session')

    Returns SSE stream with text chunks and action commands.
    """
    message = request.get("message", "")
    canvas_context = request.get("canvas_context", {})
    provider = request.get("provider", "ollama")
    model = request.get("model")
    session_id_str = request.get("session_id", "canvas-session")

    # Get or create canvas session (use ID 9999 for canvas chat)
    canvas_session_id = 9999
    session = chat_service.get_session(db, canvas_session_id)
    if not session:
        # Create canvas session if it doesn't exist
        session = chat_service.create_session(
            db,
            title="Canvas Assistant",
            system_prompt="You are a canvas assistant that helps manipulate investigation canvases."
        )
        canvas_session_id = session.id
    session_id = canvas_session_id

    async def event_stream():
        """Generate SSE events with canvas actions."""
        try:
            async for chunk in chat_service.chat_with_canvas_control(
                db=db,
                session_id=session_id,
                message=message,
                canvas_context=canvas_context,
                provider=provider,
                model=model,
            ):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            print(f"Canvas chat error: {e}")
            import traceback
            traceback.print_exc()
            yield f"data: [ERROR] {str(e)}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
