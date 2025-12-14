"""Tests for document processing."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.core.document_processor import DocumentProcessor
from app.models.enums import DocumentType


@pytest.fixture
def doc_processor():
    """Create a document processor instance."""
    return DocumentProcessor()


def test_document_processor_initialization(doc_processor):
    """Test document processor initializes correctly."""
    assert doc_processor is not None
    assert hasattr(doc_processor, 'process_document')


@pytest.mark.parametrize("file_type,expected_parser", [
    (DocumentType.PDF, "PDFParser"),
    (DocumentType.DOCX, "DOCXParser"),
    (DocumentType.XLSX, "XLSXParser"),
])
def test_parser_selection(doc_processor, file_type, expected_parser):
    """Test correct parser is selected for file types."""
    with patch('app.core.parsers.factory.ParserFactory.get_parser') as mock_get:
        mock_parser = Mock()
        mock_parser.__class__.__name__ = expected_parser
        mock_get.return_value = mock_parser

        parser = doc_processor._get_parser(file_type)
        assert parser.__class__.__name__ == expected_parser


def test_text_chunking():
    """Test text is chunked correctly."""
    doc_processor = DocumentProcessor()
    text = "This is a test. " * 100  # Create long text

    chunks = doc_processor._chunk_text(text, chunk_size=50, overlap=10)

    assert len(chunks) > 0
    assert all(len(chunk) <= 50 for chunk in chunks)


def test_process_document_creates_chunks():
    """Test document processing creates text chunks."""
    doc_processor = DocumentProcessor()

    with patch.object(doc_processor, '_get_parser') as mock_parser:
        mock_parser.return_value.parse.return_value = {
            'text': 'Test document content',
            'metadata': {}
        }

        with patch.object(doc_processor, '_chunk_text') as mock_chunk:
            mock_chunk.return_value = ['chunk1', 'chunk2']

            result = doc_processor.process_document('test.pdf', DocumentType.PDF)

            assert 'chunks' in result
            assert len(result['chunks']) == 2


def test_empty_document_handling(doc_processor):
    """Test handling of empty documents."""
    with patch.object(doc_processor, '_get_parser') as mock_parser:
        mock_parser.return_value.parse.return_value = {
            'text': '',
            'metadata': {}
        }

        result = doc_processor.process_document('empty.pdf', DocumentType.PDF)

        assert 'error' in result or result['chunks'] == []


def test_document_processor_error_handling(doc_processor):
    """Test error handling in document processing."""
    with patch.object(doc_processor, '_get_parser') as mock_parser:
        mock_parser.return_value.parse.side_effect = Exception("Parse error")

        result = doc_processor.process_document('bad.pdf', DocumentType.PDF)

        assert 'error' in result
