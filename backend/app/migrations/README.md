# Database Migrations

This directory contains database migration scripts for the Argus Intelligence Platform.

## Structure

Migrations are numbered sequentially: `001_description.py`, `002_description.py`, etc.

Each migration file should contain:
- `upgrade()` function - applies the migration
- `downgrade()` function - reverts the migration (optional for SQLite)

## Running Migrations

To run all pending migrations:

```bash
cd /home/taimaishu/argus-intelligence-platform/backend
source venv/bin/activate
python run_migration.py
```

## Migration History

### 001_add_embedding_status.py
**Date:** 2025-12-25
**Purpose:** Added separate embedding status tracking to documents table

**Changes:**
- Added `embedding_status` column (VARCHAR(10), default 'PENDING')
- Added `embedding_error_message` column (TEXT, nullable)

**Rationale:** Separates document parsing status from embedding generation status. This allows:
- Documents to be marked as COMPLETED even if embeddings fail
- Better error tracking for embedding-specific failures
- Clearer status reporting in the UI

**Data Migration:** Existing documents were updated:
- COMPLETED processing → COMPLETED embedding
- FAILED processing → FAILED embedding
- PENDING processing → PENDING embedding

## Notes

- **SQLite Limitation:** SQLite doesn't support `DROP COLUMN`, so downgrade operations would require recreating tables
- **Enum Values:** Status columns use uppercase values (PENDING, PROCESSING, COMPLETED, FAILED) to match the `ProcessingStatus` enum
- **No Alembic:** This project uses custom migrations instead of Alembic for simplicity
