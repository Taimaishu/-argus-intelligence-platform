"""Markdown document parser."""

import frontmatter
import markdown
from .base import BaseParser, ParsedDocument


class MarkdownParser(BaseParser):
    """Parser for Markdown documents."""

    def supports_file_type(self, file_extension: str) -> bool:
        """Check if file extension is .md or .markdown"""
        return file_extension.lower() in [".md", ".markdown", ".txt"]

    def parse(self, file_path: str) -> ParsedDocument:
        """
        Parse Markdown document and extract text and frontmatter.

        Args:
            file_path: Path to Markdown file

        Returns:
            ParsedDocument with extracted content
        """
        try:
            # Read file with frontmatter support
            with open(file_path, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)

            # Extract frontmatter metadata
            metadata = post.metadata
            title = metadata.get("title")
            author = metadata.get("author")

            # Get markdown content
            md_content = post.content

            # Parse sections based on headers
            sections = []
            current_section = {"heading": "Introduction", "content": ""}

            for line in md_content.split("\n"):
                stripped = line.strip()

                # Check for headers
                if stripped.startswith("#"):
                    # Save previous section
                    if current_section["content"].strip():
                        sections.append(current_section.copy())

                    # Extract heading text (remove # symbols)
                    heading = stripped.lstrip("#").strip()
                    current_section = {"heading": heading, "content": ""}
                else:
                    current_section["content"] += line + "\n"

            # Add last section
            if current_section["content"].strip():
                sections.append(current_section)

            # Convert markdown to plain text for full_text
            # (remove markdown formatting)
            full_text = md_content

            return ParsedDocument(
                text=self.clean_text(full_text),
                title=title,
                author=author,
                metadata=metadata,
                sections=sections,
            )

        except Exception as e:
            raise Exception(f"Failed to parse Markdown: {str(e)}")
