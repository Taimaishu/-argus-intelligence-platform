"""File handling and validation utilities."""

import os
import hashlib
from pathlib import Path
from typing import Tuple
from app.config import settings


def validate_file_size(file_size: int) -> bool:
    """
    Check if file size is within allowed limit.

    Args:
        file_size: File size in bytes

    Returns:
        True if valid, False otherwise
    """
    return file_size <= settings.max_upload_size_bytes


def get_file_extension(filename: str) -> str:
    """
    Extract file extension from filename.

    Args:
        filename: Name of the file

    Returns:
        File extension including the dot (e.g., '.pdf')
    """
    return os.path.splitext(filename)[1].lower()


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a unique filename using hash.

    Args:
        original_filename: Original filename

    Returns:
        Unique filename with timestamp and hash
    """
    import time
    import uuid

    # Get extension
    _, ext = os.path.splitext(original_filename)

    # Generate unique ID
    unique_id = f"{int(time.time())}_{uuid.uuid4().hex[:8]}"

    # Clean original filename (remove extension and special chars)
    clean_name = os.path.splitext(original_filename)[0]
    clean_name = "".join(c for c in clean_name if c.isalnum() or c in (' ', '-', '_'))
    clean_name = clean_name.replace(' ', '_')[:50]  # Limit length

    return f"{clean_name}_{unique_id}{ext}"


def ensure_upload_dir() -> Path:
    """
    Ensure upload directory exists.

    Returns:
        Path to upload directory
    """
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def calculate_file_hash(file_path: str) -> str:
    """
    Calculate MD5 hash of file.

    Args:
        file_path: Path to file

    Returns:
        MD5 hash as hex string
    """
    md5_hash = hashlib.md5()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)

    return md5_hash.hexdigest()


def get_file_type_from_extension(extension: str) -> str:
    """
    Map file extension to document type.

    Args:
        extension: File extension (e.g., '.pdf')

    Returns:
        Document type string
    """
    extension = extension.lower()

    if extension == ".pdf":
        return "pdf"
    elif extension == ".docx":
        return "docx"
    elif extension in [".xlsx", ".xls"]:
        return "xlsx"
    elif extension in [".pptx", ".ppt"]:
        return "pptx"
    elif extension in [".md", ".markdown"]:
        return "markdown"
    elif extension == ".txt":
        return "text"
    else:
        return "code"
