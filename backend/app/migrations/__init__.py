"""Database migrations for Argus Intelligence Platform."""

from pathlib import Path
from importlib import import_module
from app.utils.logger import logger


def run_all_migrations():
    """
    Run all migration scripts in order.

    Migration files should be named: XXX_description.py
    where XXX is a zero-padded number (001, 002, etc.)
    """
    migrations_dir = Path(__file__).parent
    migration_files = sorted(migrations_dir.glob("[0-9][0-9][0-9]_*.py"))

    if not migration_files:
        logger.info("No migrations found")
        return

    logger.info(f"Found {len(migration_files)} migration(s)")

    for migration_file in migration_files:
        module_name = f"app.migrations.{migration_file.stem}"
        logger.info(f"Running migration: {migration_file.name}")

        try:
            module = import_module(module_name)
            if hasattr(module, 'upgrade'):
                module.upgrade()
            else:
                logger.warning(f"Migration {migration_file.name} has no upgrade() function")
        except Exception as e:
            logger.error(f"Migration {migration_file.name} failed: {e}")
            raise

    logger.info("All migrations completed successfully")
