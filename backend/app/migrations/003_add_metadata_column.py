"""Migration: Add metadata column to entity_knowledge table."""

from sqlalchemy import create_engine, MetaData, Table, Column, JSON, text
import os


def get_database_url():
    """Get database URL from environment or use default."""
    db_path = os.getenv(
        "DATABASE_PATH", "/home/taimaishu/argus-intelligence-platform/backend/storage/database/research_tool.db"
    )
    return f"sqlite:///{db_path}"


def upgrade():
    """Add entity_metadata column to entity_knowledge table."""
    engine = create_engine(get_database_url())

    # SQLite doesn't support ALTER TABLE ADD COLUMN for complex types easily
    # So we'll use raw SQL
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE entity_knowledge ADD COLUMN entity_metadata JSON"))
            conn.commit()
            print("✓ Added entity_metadata column to entity_knowledge table")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("⚠ entity_metadata column already exists")
            else:
                raise


def downgrade():
    """Remove metadata column from entity_knowledge table."""
    # SQLite doesn't support DROP COLUMN, so this would require table recreation
    print("⚠ SQLite doesn't support DROP COLUMN - manual migration required")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        print("Running downgrade...")
        downgrade()
    else:
        print("Running upgrade...")
        upgrade()
    print("Migration complete!")
