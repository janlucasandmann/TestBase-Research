"""Structured logging with Rich support."""

import logging
import sys
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

from .config import config

console = Console()


def setup_logging(
    level: Optional[str] = None,
    force: bool = True
) -> logging.Logger:
    """Set up structured logging with Rich formatting.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        force: Force reconfiguration even if already configured
        
    Returns:
        Configured root logger
    """
    log_level = level or config.LOG_LEVEL
    
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=console,
                rich_tracebacks=True,
                markup=True,
                show_path=False
            )
        ],
        force=force
    )
    
    logger = logging.getLogger("testbase")
    logger.setLevel(log_level)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a named logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"testbase.{name}")


logger = setup_logging()