"""Base parser interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ParsedDocument:
    """Parsed document data structure."""

    text: str  # Full extracted text
    title: Optional[str] = None
    author: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    sections: List[Dict[str, str]] = field(
        default_factory=list
    )  # [{"heading": "...", "content": "..."}]
    page_count: Optional[int] = None


class BaseParser(ABC):
    """Abstract base class for document parsers."""

    @abstractmethod
    def parse(self, file_path: str) -> ParsedDocument:
        """
        Parse a document and extract text and metadata.

        Args:
            file_path: Path to the file to parse

        Returns:
            ParsedDocument with extracted content

        Raises:
            Exception: If parsing fails
        """
        pass

    @abstractmethod
    def supports_file_type(self, file_extension: str) -> bool:
        """
        Check if this parser supports the given file extension.

        Args:
            file_extension: File extension (e.g., '.pdf', '.docx')

        Returns:
            True if supported, False otherwise
        """
        pass

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove excessive whitespace
        text = " ".join(text.split())

        # Remove null bytes
        text = text.replace("\x00", "")

        return text.strip()
