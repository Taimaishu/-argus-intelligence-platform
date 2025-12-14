"""PDF document parser using PyMuPDF."""

import fitz  # PyMuPDF
from typing import List, Dict
from .base import BaseParser, ParsedDocument


class PDFParser(BaseParser):
    """Parser for PDF documents."""

    def supports_file_type(self, file_extension: str) -> bool:
        """Check if file extension is .pdf"""
        return file_extension.lower() == ".pdf"

    def parse(self, file_path: str) -> ParsedDocument:
        """
        Parse PDF document and extract text and metadata.

        Args:
            file_path: Path to PDF file

        Returns:
            ParsedDocument with extracted content
        """
        try:
            doc = fitz.open(file_path)

            # Extract metadata
            metadata = doc.metadata or {}
            title = metadata.get("title") or metadata.get("subject")
            author = metadata.get("author")

            # Extract text from all pages
            full_text = ""
            sections = []

            for page_num, page in enumerate(doc, start=1):
                page_text = page.get_text()

                if page_text.strip():
                    full_text += page_text + "\n\n"

                    # Store page as section
                    sections.append(
                        {
                            "heading": f"Page {page_num}",
                            "content": page_text,
                            "page": page_num,
                        }
                    )

            doc.close()

            return ParsedDocument(
                text=self.clean_text(full_text),
                title=title,
                author=author,
                metadata={
                    "format": metadata.get("format", "PDF"),
                    "creator": metadata.get("creator"),
                    "producer": metadata.get("producer"),
                    "creation_date": metadata.get("creationDate"),
                },
                sections=sections,
                page_count=len(doc),
            )

        except Exception as e:
            raise Exception(f"Failed to parse PDF: {str(e)}")
