"""Pytest configuration and fixtures."""

import pytest
import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


@pytest.fixture
def test_db():
    """Create a test database."""
    from app.database import Base, engine
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_file_path(tmp_path):
    """Create a temporary file path for testing."""
    return tmp_path / "test_document.txt"


@pytest.fixture
def sample_text():
    """Provide sample text for testing."""
    return "This is a test document. It contains multiple sentences. " * 10
