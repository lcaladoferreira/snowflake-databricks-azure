"""Logging utilities for the migration pipeline.

Provides a standardized way to obtain a logger with consistent formatting.
"""

import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """Returns a configured logger with a stream handler.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
