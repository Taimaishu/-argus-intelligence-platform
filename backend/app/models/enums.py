"""Enum definitions for the application."""

from enum import Enum


class DocumentType(str, Enum):
    """Supported document types."""

    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    PPTX = "pptx"
    MARKDOWN = "markdown"
    CODE = "code"
    TEXT = "text"


class ProcessingStatus(str, Enum):
    """Document processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class NodeType(str, Enum):
    """Canvas node types."""

    DOCUMENT = "document"
    INSIGHT = "insight"
    NOTE = "note"
    THEME = "theme"


class ArtifactType(str, Enum):
    """OSINT artifact types."""

    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    URL = "url"
    EMAIL = "email"
    HASH = "hash"
    PHONE = "phone"
    USERNAME = "username"
    CVE = "cve"


class AnalysisStatus(str, Enum):
    """Artifact analysis status."""

    PENDING = "pending"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class ThreatLevel(str, Enum):
    """Threat level classification."""

    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
