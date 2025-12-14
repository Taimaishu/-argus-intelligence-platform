"""Security middleware for rate limiting and protection."""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import re


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent abuse."""

    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls  # Max calls per period
        self.period = period  # Period in seconds
        self.clients = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host

        # Skip rate limiting for health checks
        if request.url.path == "/health":
            return await call_next(request)

        # Clean old requests
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.period)
        self.clients[client_ip] = [
            req_time for req_time in self.clients[client_ip]
            if req_time > cutoff
        ]

        # Check rate limit
        if len(self.clients[client_ip]) >= self.calls:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": self.period
                }
            )

        # Record this request
        self.clients[client_ip].append(now)

        response = await call_next(request)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response


def sanitize_input(text: str, max_length: int = 5000) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text

    Raises:
        ValueError: If input exceeds max_length or contains dangerous patterns
    """
    if not text:
        return text

    # Check length
    if len(text) > max_length:
        raise ValueError(f"Input exceeds maximum length of {max_length}")

    # Remove null bytes
    text = text.replace('\x00', '')

    # Check for SQL injection patterns
    sql_patterns = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bDROP\b.*\bTABLE\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(--\s*$)",
        r"(;\s*DROP\s)",
    ]

    for pattern in sql_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            raise ValueError("Potentially dangerous input detected")

    # Check for XSS patterns
    xss_patterns = [
        r"<script[\s\S]*?>[\s\S]*?</script>",
        r"javascript:",
        r"on\w+\s*=",
    ]

    for pattern in xss_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            raise ValueError("Potentially dangerous input detected")

    return text


def validate_file_upload(filename: str, content_type: str, max_size_mb: int = 50) -> None:
    """
    Validate file uploads.

    Args:
        filename: Name of uploaded file
        content_type: MIME type of file
        max_size_mb: Maximum file size in MB

    Raises:
        ValueError: If file is invalid
    """
    # Check filename
    if not filename or len(filename) > 255:
        raise ValueError("Invalid filename")

    # Allowed extensions
    allowed_extensions = {
        '.pdf', '.docx', '.xlsx', '.pptx', '.md', '.txt',
        '.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs'
    }

    # Check extension
    ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext not in allowed_extensions:
        raise ValueError(f"File type not allowed: {ext}")

    # Check for path traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        raise ValueError("Invalid filename: path traversal detected")

    # Validate MIME type
    allowed_mimes = {
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'text/plain',
        'text/markdown',
    }

    if content_type and content_type not in allowed_mimes and not content_type.startswith('text/'):
        raise ValueError(f"MIME type not allowed: {content_type}")
