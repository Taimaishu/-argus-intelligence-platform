"""Migration: Add entity_knowledge table for comprehensive entity information."""

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    JSON,
    MetaData,
    Table,
)
from datetime import datetime
import os


def get_database_url():
    """Get database URL from environment or use default."""
    db_path = os.getenv(
        "DATABASE_PATH", "/home/taimaishu/argus-intelligence-platform/backend/storage/database/research_tool.db"
    )
    return f"sqlite:///{db_path}"


def upgrade():
    """Create entity_knowledge table."""
    engine = create_engine(get_database_url())
    metadata = MetaData()

    entity_knowledge = Table(
        "entity_knowledge",
        metadata,
        Column("id", Integer, primary_key=True, autoincrement=True),
        # Basic identification
        Column("entity_name", String(255), nullable=False, index=True),
        Column("full_name", String(512), nullable=True),
        Column("entity_type", String(50), nullable=False),
        # Biographical/descriptive information
        Column("description", Text, nullable=True),
        Column("background", Text, nullable=True),
        Column("role_title", String(255), nullable=True),
        # Investigation context
        Column("connection_to_investigation", Text, nullable=True),
        Column("theories", Text, nullable=True),
        Column("key_associations", JSON, nullable=True),
        # Media
        Column("photo_url", String(512), nullable=True),
        Column("photo_source", String(255), nullable=True),
        Column("photo_attribution", Text, nullable=True),
        # Evidence and sources
        Column("evidence_excerpts", JSON, nullable=True),
        Column("document_ids", JSON, nullable=True),
        Column("mention_count", Integer, default=0),
        # Metadata
        Column("confidence_score", Float, nullable=True),
        Column("verification_status", String(50), default="unverified"),
        # Timestamps
        Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
        Column("updated_at", DateTime, default=datetime.utcnow, nullable=False),
        Column("last_analyzed", DateTime, nullable=True),
    )

    # Create table
    metadata.create_all(engine)
    print("✓ Created entity_knowledge table")


def downgrade():
    """Drop entity_knowledge table."""
    engine = create_engine(get_database_url())
    metadata = MetaData()
    metadata.reflect(bind=engine)

    if "entity_knowledge" in metadata.tables:
        entity_knowledge = metadata.tables["entity_knowledge"]
        entity_knowledge.drop(engine)
        print("✓ Dropped entity_knowledge table")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        print("Running downgrade...")
        downgrade()
    else:
        print("Running upgrade...")
        upgrade()
    print("Migration complete!")
