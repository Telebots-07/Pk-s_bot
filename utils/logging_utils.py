import logging

logger = logging.getLogger(__name__)

def log_error(message: str):
    """📜 Log an error message with style."""
    logger.error(f"🚨 {message}")
