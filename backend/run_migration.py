#!/usr/bin/env python3
"""
Run database migrations for Argus Intelligence Platform.

Usage:
    python run_migration.py              # Run all pending migrations
    python run_migration.py --check      # Check migration status without running
"""

import sys
import argparse
from app.migrations import run_all_migrations
from app.utils.logger import logger


def main():
    parser = argparse.ArgumentParser(description="Run database migrations")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check migration status without running"
    )
    args = parser.parse_args()

    if args.check:
        logger.info("Migration check mode (not implemented yet)")
        logger.info("This would show which migrations have/haven't been run")
        return

    try:
        logger.info("Starting database migrations...")
        run_all_migrations()
        logger.info("✅ All migrations completed successfully!")
        return 0
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
