"""
Logging configuration for the Release Orchestration Platform.
"""
import logging
import sys
from typing import Optional
from config import settings


def setup_logging(log_level: Optional[str] = None) -> None:
    """
    Configure application logging.
    
    Args:
        log_level: Override log level from settings
    """
    level = log_level or settings.log_level
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=settings.log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers
    logging.getLogger(name="uvicorn").setLevel(level=logging.INFO)
    logging.getLogger(name="sqlalchemy.engine").setLevel(
        level=logging.INFO if settings.database_echo else logging.WARNING
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

# Made with Bob
