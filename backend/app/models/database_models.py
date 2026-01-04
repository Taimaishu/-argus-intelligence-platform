"""SQLAlchemy database models."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from .enums import (
    DocumentType,
    ProcessingStatus,
    NodeType,
    ArtifactType,
    AnalysisStatus,
    ThreatLevel,
)

Base = declarative_base()


class Document(Base):
    """Document metadata model."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False, unique=True)
    file_type = Column(SQLEnum(DocumentType), nullable=False)
    file_size = Column(Integer, nullable=False)  # bytes

    # Extracted metadata
    title = Column(String(512), nullable=True)
    author = Column(String(255), nullable=True)

    # Processing info
    processing_status = Column(
        SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING
    )
    error_message = Column(Text, nullable=True)

    # Embedding info (separate from processing)
    embedding_status = Column(
        SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING
    )
    embedding_error_message = Column(Text, nullable=True)

    # Timestamps
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_date = Column(DateTime, nullable=True)

    # Relationships
    chunks = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', status='{self.processing_status}')>"


class DocumentChunk(Base):
    """Document text chunks for embedding."""

    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(
        Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    chunk_index = Column(Integer, nullable=False)  # Order of chunk in document
    chunk_text = Column(Text, nullable=False)
    embedding_id = Column(String(255), nullable=True)  # ChromaDB reference

    # Metadata
    page_number = Column(Integer, nullable=True)  # For PDFs, PPTX
    section = Column(String(255), nullable=True)  # Section/heading

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="chunks")

    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id}, index={self.chunk_index})>"


class CanvasNode(Base):
    """Canvas visualization nodes."""

    __tablename__ = "canvas_nodes"

    id = Column(String(255), primary_key=True)  # UUID
    type = Column(SQLEnum(NodeType), nullable=False)

    # Position on canvas
    position_x = Column(Float, nullable=False)
    position_y = Column(Float, nullable=False)

    # Node data (stored as JSON)
    data = Column(JSON, nullable=False)  # Contains title, content, color, etc.

    # Link to document if it's a document node
    document_id = Column(
        Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=True
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    source_edges = relationship(
        "CanvasEdge",
        foreign_keys="CanvasEdge.source_node_id",
        back_populates="source_node",
        cascade="all, delete-orphan",
    )
    target_edges = relationship(
        "CanvasEdge",
        foreign_keys="CanvasEdge.target_node_id",
        back_populates="target_node",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<CanvasNode(id='{self.id}', type='{self.type}')>"


class CanvasEdge(Base):
    """Canvas connections between nodes."""

    __tablename__ = "canvas_edges"

    id = Column(String(255), primary_key=True)  # UUID
    source_node_id = Column(
        String(255), ForeignKey("canvas_nodes.id", ondelete="CASCADE"), nullable=False
    )
    target_node_id = Column(
        String(255), ForeignKey("canvas_nodes.id", ondelete="CASCADE"), nullable=False
    )

    # Connection metadata
    connection_type = Column(
        String(50), default="default"
    )  # default, related, derived, etc.
    strength = Column(Float, nullable=True)  # Similarity score or connection strength

    # Edge data (stored as JSON)
    data = Column(JSON, nullable=True)  # Label, color, style, etc.

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    source_node = relationship(
        "CanvasNode", foreign_keys=[source_node_id], back_populates="source_edges"
    )
    target_node = relationship(
        "CanvasNode", foreign_keys=[target_node_id], back_populates="target_edges"
    )

    def __repr__(self):
        return f"<CanvasEdge(id='{self.id}', {self.source_node_id} -> {self.target_node_id})>"


class Setting(Base):
    """Application settings key-value store."""

    __tablename__ = "settings"

    key = Column(String(255), primary_key=True)
    value = Column(Text, nullable=False)

    # Metadata
    description = Column(String(512), nullable=True)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self):
        return f"<Setting(key='{self.key}')>"


class ChatSession(Base):
    """Chat session for organizing conversations."""

    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, default="New Chat")
    system_prompt = Column(Text, nullable=True)  # Custom system prompt for this session

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )

    def __repr__(self):
        return f"<ChatSession(id={self.id}, title='{self.title}')>"


class ChatMessage(Base):
    """Individual chat messages."""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False
    )

    role = Column(String(50), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)

    # Optional metadata
    document_context = Column(JSON, nullable=True)  # Referenced documents/chunks
    model = Column(String(100), nullable=True)  # Which model generated this response

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role='{self.role}', session_id={self.session_id})>"


class Artifact(Base):
    """OSINT artifacts extracted or submitted for analysis."""

    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True, index=True)
    artifact_type = Column(SQLEnum(ArtifactType), nullable=False, index=True)
    value = Column(String(512), nullable=False, index=True)

    # Analysis status
    analysis_status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING)
    threat_level = Column(SQLEnum(ThreatLevel), default=ThreatLevel.UNKNOWN)

    # Analysis results (stored as JSON)
    analysis_data = Column(JSON, nullable=True)

    # Source tracking
    document_id = Column(
        Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )
    extracted = Column(
        Integer, default=0
    )  # 1 if auto-extracted, 0 if manually submitted

    # Metadata
    first_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_analyzed = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    tags = relationship(
        "ArtifactTag", back_populates="artifact", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Artifact(id={self.id}, type='{self.artifact_type}', value='{self.value}')>"


class ArtifactTag(Base):
    """Tags for organizing artifacts."""

    __tablename__ = "artifact_tags"

    id = Column(Integer, primary_key=True, index=True)
    artifact_id = Column(
        Integer, ForeignKey("artifacts.id", ondelete="CASCADE"), nullable=False
    )
    tag = Column(String(50), nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    artifact = relationship("Artifact", back_populates="tags")

    def __repr__(self):
        return f"<ArtifactTag(artifact_id={self.artifact_id}, tag='{self.tag}')>"


class Entity(Base):
    """Extracted entity for knowledge graph."""

    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False, index=True)  # person, organization, etc.
    name = Column(String(512), nullable=False)
    normalized_name = Column(String(512), nullable=False, index=True)  # For deduplication

    # Statistics
    mention_count = Column(Integer, default=1)
    confidence = Column(Float, default=1.0)  # 0.0 to 1.0

    # Source tracking
    document_ids = Column(JSON, nullable=True)  # List of document IDs where mentioned
    extra_data = Column(JSON, nullable=True)  # Additional type-specific data

    # Timestamps
    first_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    source_relationships = relationship(
        "EntityRelationship",
        foreign_keys="EntityRelationship.source_entity_id",
        back_populates="source_entity",
        cascade="all, delete-orphan",
    )
    target_relationships = relationship(
        "EntityRelationship",
        foreign_keys="EntityRelationship.target_entity_id",
        back_populates="target_entity",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Entity(id={self.id}, type='{self.entity_type}', name='{self.name}')>"


class EntityRelationship(Base):
    """Relationship between two entities."""

    __tablename__ = "entity_relationships"

    id = Column(Integer, primary_key=True, index=True)
    source_entity_id = Column(
        Integer, ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target_entity_id = Column(
        Integer, ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Relationship metadata
    relationship_type = Column(String(100), nullable=False)  # works_with, located_in, etc.
    strength = Column(Float, default=0.5)  # 0.0 to 1.0
    context = Column(Text, nullable=True)  # Textual evidence

    # Source tracking
    document_id = Column(
        Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=True
    )

    # Timestamps
    first_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    source_entity = relationship(
        "Entity",
        foreign_keys=[source_entity_id],
        back_populates="source_relationships"
    )
    target_entity = relationship(
        "Entity",
        foreign_keys=[target_entity_id],
        back_populates="target_relationships"
    )

    def __repr__(self):
        return f"<EntityRelationship(id={self.id}, {self.source_entity_id} -> {self.target_entity_id}, type='{self.relationship_type}')>"


class EntityKnowledge(Base):
    """Comprehensive knowledge database for entities."""

    __tablename__ = "entity_knowledge"

    id = Column(Integer, primary_key=True, index=True)

    # Basic identification
    entity_name = Column(String(255), nullable=False, index=True)  # Original name
    full_name = Column(String(512), nullable=True)  # Enhanced/full name (e.g., "Prince Andrew")
    entity_type = Column(String(50), nullable=False)  # person, organization, location, etc.

    # Biographical/descriptive information
    description = Column(Text, nullable=True)  # Who they are
    background = Column(Text, nullable=True)  # Background & past activities
    role_title = Column(String(255), nullable=True)  # Title/position (e.g., "Prince", "President")

    # Investigation context
    connection_to_investigation = Column(Text, nullable=True)  # Why they're relevant
    theories = Column(Text, nullable=True)  # AI-generated theories
    key_associations = Column(JSON, nullable=True)  # List of associated entities

    # Media
    photo_url = Column(String(512), nullable=True)
    photo_source = Column(String(255), nullable=True)  # wikipedia, google, etc.
    photo_attribution = Column(Text, nullable=True)

    # Evidence and sources
    evidence_excerpts = Column(JSON, nullable=True)  # List of document excerpts
    document_ids = Column(JSON, nullable=True)  # List of document IDs mentioning this entity
    mention_count = Column(Integer, default=0)

    # Metadata
    confidence_score = Column(Float, nullable=True)  # Confidence in identification
    verification_status = Column(String(50), default="unverified")  # verified, unverified, disputed
    entity_metadata = Column(JSON, nullable=True)  # Extended metadata (dates, locations, affiliations, etc.)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_analyzed = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<EntityKnowledge(id={self.id}, entity_name='{self.entity_name}', full_name='{self.full_name}')>"
