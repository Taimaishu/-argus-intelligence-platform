"""Code file parser with syntax highlighting support."""

from pathlib import Path
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, guess_lexer
from pygments.formatters import NullFormatter
from .base import BaseParser, ParsedDocument


class CodeParser(BaseParser):
    """Parser for code files."""

    SUPPORTED_EXTENSIONS = {
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".java",
        ".cpp",
        ".c",
        ".h",
        ".cs",
        ".go",
        ".rs",
        ".rb",
        ".php",
        ".swift",
        ".kt",
        ".scala",
        ".r",
        ".sql",
        ".sh",
        ".bash",
        ".zsh",
        ".yaml",
        ".yml",
        ".json",
        ".xml",
        ".html",
        ".css",
        ".scss",
        ".sass",
        ".less",
    }

    def supports_file_type(self, file_extension: str) -> bool:
        """Check if file extension is a supported code file"""
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    def parse(self, file_path: str) -> ParsedDocument:
        """
        Parse code file and extract text with metadata.

        Args:
            file_path: Path to code file

        Returns:
            ParsedDocument with extracted content
        """
        try:
            file_path_obj = Path(file_path)

            # Read file content
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                code = f.read()

            # Try to determine language from file extension
            try:
                lexer = get_lexer_for_filename(file_path)
                language = lexer.name
            except:
                try:
                    lexer = guess_lexer(code)
                    language = lexer.name
                except:
                    language = "Text"

            # Extract basic structure (functions, classes, etc.)
            sections = self._extract_code_structure(code, language)

            # Create title from filename
            title = file_path_obj.stem

            return ParsedDocument(
                text=code,
                title=title,
                author=None,
                metadata={
                    "language": language,
                    "filename": file_path_obj.name,
                    "extension": file_path_obj.suffix,
                    "line_count": len(code.splitlines()),
                },
                sections=sections,
            )

        except Exception as e:
            raise Exception(f"Failed to parse code file: {str(e)}")

    def _extract_code_structure(self, code: str, language: str) -> list:
        """
        Extract basic code structure (functions, classes).

        Args:
            code: Source code
            language: Programming language

        Returns:
            List of sections with code structure
        """
        sections = []
        lines = code.splitlines()

        # Simple heuristic-based extraction
        current_section = None

        for i, line in enumerate(lines, start=1):
            stripped = line.strip()

            # Python/JavaScript/TypeScript functions and classes
            if (
                stripped.startswith("def ")
                or stripped.startswith("function ")
                or stripped.startswith("class ")
                or stripped.startswith("async def ")
                or stripped.startswith("async function ")
            ):

                # Extract function/class name
                parts = stripped.split("(")[0].split()
                if len(parts) >= 2:
                    name = parts[-1]

                    if current_section:
                        sections.append(current_section)

                    current_section = {
                        "heading": f"{parts[0].title()}: {name}",
                        "content": line,
                        "line_number": i,
                    }
            elif current_section:
                current_section["content"] += "\n" + line

        # Add last section
        if current_section:
            sections.append(current_section)

        # If no structure found, treat whole file as one section
        if not sections:
            sections.append({"heading": "Code", "content": code})

        return sections
