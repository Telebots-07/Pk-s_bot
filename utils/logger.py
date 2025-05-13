from utils.firestore import log_error

def log_error(error_message: str):
    """Log error to Firestore with additional context."""
    try:
        log_error(f"Error: {error_message}")
    except Exception as e:
        print(f"Failed to log error: {str(e)}")
