"""Database initialization script."""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import init_db, engine
from app.models.database_models import Base


def main():
    """Initialize the database."""
    print("Creating database tables...")

    # Create all tables
    Base.metadata.create_all(bind=engine)

    print("✓ Database initialized successfully!")
    print(f"✓ Tables created: {', '.join(Base.metadata.tables.keys())}")


if __name__ == "__main__":
    main()
