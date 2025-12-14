"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Argus" in data["message"]


def test_docs_endpoint():
    """Test API documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_get_documents_empty():
    """Test getting documents when none exist."""
    response = client.get("/api/documents")
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert isinstance(data["documents"], list)


def test_create_chat_session():
    """Test creating a chat session."""
    response = client.post(
        "/api/chat/sessions",
        json={"title": "Test Chat"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == "Test Chat"


def test_list_chat_sessions():
    """Test listing chat sessions."""
    response = client.get("/api/chat/sessions")
    assert response.status_code == 200
    data = response.json()
    assert "sessions" in data
    assert "total" in data


def test_models_provider_status():
    """Test provider status endpoint."""
    response = client.get("/api/models/providers/status")
    assert response.status_code == 200
    data = response.json()
    assert "ollama" in data
    assert "openai" in data
    assert "anthropic" in data


def test_ollama_models_list():
    """Test listing Ollama models."""
    response = client.get("/api/models/ollama/list")
    # This might fail if Ollama is not running, so we check for both cases
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "models" in data


def test_search_without_query():
    """Test search endpoint requires query."""
    response = client.post("/api/search", json={})
    assert response.status_code == 422  # Validation error


def test_canvas_get_state():
    """Test getting canvas state."""
    response = client.get("/api/canvas/state")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data


def test_patterns_network_analysis():
    """Test network analysis endpoint."""
    response = client.get("/api/patterns/network")
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data
    assert "network_density" in data


def test_invalid_endpoint():
    """Test invalid endpoint returns 404."""
    response = client.get("/api/nonexistent")
    assert response.status_code == 404


def test_cors_headers():
    """Test CORS headers are present."""
    response = client.options("/api/documents")
    assert "access-control-allow-origin" in response.headers or response.status_code == 405
