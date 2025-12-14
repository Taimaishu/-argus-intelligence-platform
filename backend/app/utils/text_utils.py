"""Text processing and chunking utilities."""

import re
from typing import List
from app.config import settings


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: Text to chunk
        chunk_size: Maximum tokens per chunk (default from settings)
        overlap: Number of overlapping tokens (default from settings)

    Returns:
        List of text chunks
    """
    chunk_size = chunk_size or settings.CHUNK_SIZE
    overlap = overlap or settings.CHUNK_OVERLAP

    # Simple word-based chunking (approximate tokens)
    words = text.split()

    if len(words) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))

        # Move start with overlap
        start = end - overlap

    return chunks


def chunk_text_by_paragraphs(text: str, chunk_size: int = None) -> List[str]:
    """
    Split text into chunks respecting paragraph boundaries.

    Args:
        text: Text to chunk
        chunk_size: Target maximum tokens per chunk

    Returns:
        List of text chunks
    """
    chunk_size = chunk_size or settings.CHUNK_SIZE

    # Split by paragraphs (double newlines or single newlines)
    paragraphs = re.split(r"\n\s*\n", text)

    chunks = []
    current_chunk = []
    current_size = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        para_size = len(para.split())

        # If single paragraph is too large, split it
        if para_size > chunk_size:
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = []
                current_size = 0

            # Split large paragraph
            para_chunks = chunk_text(para, chunk_size=chunk_size, overlap=100)
            chunks.extend(para_chunks)
        else:
            # Check if adding this paragraph exceeds chunk size
            if current_size + para_size > chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [para]
                current_size = para_size
            else:
                current_chunk.append(para)
                current_size += para_size

    # Add remaining chunk
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks


def clean_whitespace(text: str) -> str:
    """
    Clean excessive whitespace from text.

    Args:
        text: Text to clean

    Returns:
        Cleaned text
    """
    # Replace multiple spaces with single space
    text = re.sub(r" +", " ", text)

    # Replace multiple newlines with double newline
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum character length

    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text

    return text[:max_length].rsplit(" ", 1)[0] + "..."


def extract_snippet(text: str, query: str, context_length: int = 150) -> str:
    """
    Extract a snippet of text around a query term.

    Args:
        text: Full text
        query: Search query
        context_length: Characters of context on each side

    Returns:
        Text snippet with context around query
    """
    # Find query in text (case-insensitive)
    text_lower = text.lower()
    query_lower = query.lower()

    index = text_lower.find(query_lower)

    if index == -1:
        # Query not found, return beginning of text
        return truncate_text(text, context_length * 2)

    # Extract context around query
    start = max(0, index - context_length)
    end = min(len(text), index + len(query) + context_length)

    snippet = text[start:end]

    # Add ellipsis if truncated
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."

    return snippet
