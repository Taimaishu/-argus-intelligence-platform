"""
Migration: Add embedding_status and embedding_error_message columns to documents table

Created: 2025-12-25
Purpose: Separate processing status from embedding status for better error tracking
"""

from sqlalchemy import text
from app.database import engine
from app.utils.logger import logger


def upgrade():
    """Add embedding status columns to documents table."""
    try:
        with engine.connect() as conn:
            # Check if columns already exist
            result = conn.execute(text("PRAGMA table_info(documents)"))
            columns = [row[1] for row in result.fetchall()]

            if 'embedding_status' in columns:
                logger.info("Column 'embedding_status' already exists, skipping migration")
                return

            logger.info("Starting migration: Adding embedding status columns")

            # SQLite doesn't support adding multiple columns in one statement
            # Add embedding_status column (use uppercase to match ProcessingStatus enum)
            conn.execute(text("""
                ALTER TABLE documents
                ADD COLUMN embedding_status VARCHAR(10) DEFAULT 'PENDING'
            """))
            logger.info("Added column: embedding_status")

            # Add embedding_error_message column
            conn.execute(text("""
                ALTER TABLE documents
                ADD COLUMN embedding_error_message TEXT
            """))
            logger.info("Added column: embedding_error_message")

            # Update existing rows to have proper status
            # Documents that are completed should also have embedding_status = COMPLETED
            # (assuming they were processed before this migration)
            conn.execute(text("""
                UPDATE documents
                SET embedding_status = 'COMPLETED'
                WHERE processing_status = 'COMPLETED'
            """))
            logger.info("Updated existing completed documents with embedding_status = 'COMPLETED'")

            # Documents that are failed should have embedding_status = FAILED
            conn.execute(text("""
                UPDATE documents
                SET embedding_status = 'FAILED'
                WHERE processing_status = 'FAILED'
            """))
            logger.info("Updated existing failed documents with embedding_status = 'FAILED'")

            conn.commit()
            logger.info("Migration completed successfully!")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


def downgrade():
    """Remove embedding status columns (SQLite doesn't support DROP COLUMN easily)."""
    logger.warning("Downgrade not supported for SQLite ALTER TABLE operations")
    logger.warning("To revert, you would need to recreate the table without these columns")


if __name__ == "__main__":
    """Run migration directly."""
    logger.info("=" * 60)
    logger.info("Running migration: Add embedding status columns")
    logger.info("=" * 60)
    upgrade()
    logger.info("=" * 60)
    logger.info("Migration complete!")
    logger.info("=" * 60)
