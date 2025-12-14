"""Parser factory for selecting appropriate document parser."""

import os
from typing import Optional
from .base import BaseParser
from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .xlsx_parser import XLSXParser
from .pptx_parser import PPTXParser
from .markdown_parser import MarkdownParser
from .code_parser import CodeParser


class ParserFactory:
    """Factory for creating appropriate document parsers."""

    def __init__(self):
        """Initialize factory with all available parsers."""
        self.parsers: list[BaseParser] = [
            PDFParser(),
            DOCXParser(),
            XLSXParser(),
            PPTXParser(),
            MarkdownParser(),
            CodeParser(),
        ]

    def get_parser(self, file_path: str) -> Optional[BaseParser]:
        """
        Get appropriate parser for the given file.

        Args:
            file_path: Path to file

        Returns:
            Parser instance or None if no parser supports the file

        Raises:
            ValueError: If file extension is not supported
        """
        _, extension = os.path.splitext(file_path)

        # Find first parser that supports this extension
        for parser in self.parsers:
            if parser.supports_file_type(extension):
                return parser

        raise ValueError(f"No parser available for file type: {extension}")

    def is_supported(self, file_path: str) -> bool:
        """
        Check if file type is supported.

        Args:
            file_path: Path to file

        Returns:
            True if supported, False otherwise
        """
        _, extension = os.path.splitext(file_path)

        for parser in self.parsers:
            if parser.supports_file_type(extension):
                return True

        return False

    def get_supported_extensions(self) -> set[str]:
        """
        Get all supported file extensions.

        Returns:
            Set of supported extensions
        """
        extensions = set()

        # PDF
        extensions.add(".pdf")

        # Office documents
        extensions.update([".docx", ".xlsx", ".xls", ".pptx", ".ppt"])

        # Markdown and text
        extensions.update([".md", ".markdown", ".txt"])

        # Code files (from CodeParser)
        extensions.update(CodeParser.SUPPORTED_EXTENSIONS)

        return extensions
