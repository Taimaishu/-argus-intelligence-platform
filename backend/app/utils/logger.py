"""Logging configuration."""

import logging
import sys
from app.config import settings


def setup_logger(name: str = "research_tool") -> logging.Logger:
    """
    Set up application logger.

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Set level from settings
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # Only add handler if it doesn't have one
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# Default logger instance
logger = setup_logger()
