import logging
from utils.firestore import log_error

def log_error(error_message: str):
    """Log error to Firestore and Render logs."""
    try:
        log_error(f"Error: {error_message}")
        logging.error(error_message)
    except Exception as e:
        logging.error(f"Failed to log error: {str(e)}")
