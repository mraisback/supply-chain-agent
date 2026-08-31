"""Logging configuration."""

import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logging(log_level=logging.INFO, log_dir="./logs"):
    """
    Configure logging for the application.

    Args:
        log_level: Logging level
        log_dir: Directory for log files
    """
    # Create logs directory
    Path(log_dir).mkdir(exist_ok=True)

    # Create logger
    logger = logging.getLogger("supply_chain_agent")
    logger.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler
    log_file = Path(log_dir) / f"supply_chain_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get logger instance."""
    return logging.getLogger(f"supply_chain_agent.{name}")
