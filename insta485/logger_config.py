"""
Centralized logging configuration for TicketVault application.
"""

import logging
import logging.handlers
import os
from datetime import datetime


def setup_logging():
    """Setup centralized logging configuration."""

    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Clear any existing handlers
    logger.handlers.clear()

    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    simple_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
    )

    # Console handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    # File handler (DEBUG and above)
    log_file = os.path.join(
        log_dir, f"ticketvault_{datetime.now().strftime('%Y%m%d')}.log"
    )
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)

    # Error file handler (ERROR and above)
    error_log_file = os.path.join(
        log_dir, f"errors_{datetime.now().strftime('%Y%m%d')}.log"
    )
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=10,
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)

    # Payment-specific logger
    payment_logger = logging.getLogger("payment")
    payment_log_file = os.path.join(
        log_dir, f"payments_{datetime.now().strftime('%Y%m%d')}.log"
    )
    payment_handler = logging.handlers.RotatingFileHandler(
        payment_log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=10,
    )
    payment_handler.setLevel(logging.INFO)
    payment_handler.setFormatter(detailed_formatter)
    payment_logger.addHandler(payment_handler)
    payment_logger.setLevel(logging.INFO)

    # Email-specific logger
    email_logger = logging.getLogger("email")
    email_log_file = os.path.join(
        log_dir, f"emails_{datetime.now().strftime('%Y%m%d')}.log"
    )
    email_handler = logging.handlers.RotatingFileHandler(
        email_log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=10,
    )
    email_handler.setLevel(logging.INFO)
    email_handler.setFormatter(detailed_formatter)
    email_logger.addHandler(email_handler)
    email_logger.setLevel(logging.INFO)

    return logger


def get_logger(name=None):
    """Get a logger instance."""
    if name:
        return logging.getLogger(name)
    return logging.getLogger()


# Initialize logging when module is imported
setup_logging()
