"""Logging utilities for the Amazon product analysis application."""

import logging
from langchain_app.core.config import LOG_LEVEL, LOG_FORMAT

def configure_logger(name=None):
    """Configure and return a logger with standardized settings.
    
    Args:
        name: Optional name for the logger. If None, returns the root logger.
        
    Returns:
        A configured logger instance.
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured to avoid duplicate handlers
    if not logger.handlers:
        # Set level based on config
        level = getattr(logging, LOG_LEVEL, logging.INFO)
        logger.setLevel(level)
        
        # Create handler
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)
    
    return logger
