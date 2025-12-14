"""Chat service with Ollama integration."""

from typing import AsyncGenerator, List, Optional
import ollama
from sqlalchemy.orm import Session

from ..config import settings
from ..models.database_models import ChatSession, ChatMessage, Document, DocumentChunk
from ..utils.logger import logger


class ChatService:
    """Service for managing chat interactions with Ollama."""

    def __init__(self):
        self.model_name = settings.OLLAMA_LLM_MODEL
        self.base_url = settings.OLLAMA_BASE_URL

    def create_session(self, db: Session, title: str = "New Chat") -> ChatSession:
        """Create a new chat session."""
        session = ChatSession(title=title)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def get_session(self, db: Session, session_id: int) -> Optional[ChatSession]:
        """Get a chat session by ID."""
        return db.query(ChatSession).filter(ChatSession.id == session_id).first()

    def list_sessions(self, db: Session, limit: int = 50) -> List[ChatSession]:
        """List all chat sessions."""
        return db.query(ChatSession).order_by(ChatSession.updated_at.desc()).limit(limit).all()

    def delete_session(self, db: Session, session_id: int) -> bool:
        """Delete a chat session."""
        session = self.get_session(db, session_id)
        if not session:
            return False
        db.delete(session)
        db.commit()
        return True

    def get_document_context(self, db: Session, num_docs: int = 5) -> str:
        """Get recent document context for chat."""
        documents = db.query(Document).order_by(Document.upload_date.desc()).limit(num_docs).all()

        if not documents:
            return "No documents uploaded yet."

        context = "Recent documents in the research library:\n\n"
        for doc in documents:
            context += f"- {doc.title or doc.filename} ({doc.file_type.value})\n"

        return context

    async def chat_stream(
        self,
        db: Session,
        session_id: int,
        message: str,
        include_document_context: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat responses from Ollama.

        Args:
            db: Database session
            session_id: Chat session ID
            message: User message
            include_document_context: Whether to include document context in system prompt

        Yields:
            Response chunks as they arrive from Ollama
        """
        # Get chat session
        session = self.get_session(db, session_id)
        if not session:
            yield "Error: Session not found"
            return

        # Save user message
        user_msg = ChatMessage(
            session_id=session_id,
            role="user",
            content=message
        )
        db.add(user_msg)
        db.commit()

        try:
            # Build message history
            messages = []

            # System message with context
            system_prompt = """You are a research assistant helping with document analysis and investigation.
You help users brainstorm theories, find connections between documents, and explore research topics.
Be concise, insightful, and focused on helping the user discover patterns and insights."""

            if include_document_context:
                doc_context = self.get_document_context(db, num_docs=10)
                system_prompt += f"\n\n{doc_context}"

            messages.append({
                "role": "system",
                "content": system_prompt
            })

            # Add conversation history (last 10 messages)
            for msg in session.messages[-10:]:
                if msg.role in ['user', 'assistant']:
                    messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })

            logger.info(f"Streaming chat with Ollama model: {self.model_name}")

            # Stream response from Ollama
            full_response = ""
            stream = ollama.chat(
                model=self.model_name,
                messages=messages,
                stream=True
            )

            for chunk in stream:
                content = chunk['message']['content']
                full_response += content
                yield content

            # Save assistant response
            assistant_msg = ChatMessage(
                session_id=session_id,
                role="assistant",
                content=full_response,
                model=self.model_name
            )
            db.add(assistant_msg)
            db.commit()

        except Exception as e:
            error_msg = f"Error in chat: {str(e)}"
            logger.error(error_msg)
            yield f"\n\nError: {error_msg}"
