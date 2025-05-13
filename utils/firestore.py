from firebase_admin import firestore

def initialize_firestore():
    """Initialize Firestore client."""
    return firestore.client()

def log_error(error_message: str):
    """Log error to Firestore (called by utils/logger.py)."""
    db = firestore.client()
    db.collection("logs").add({
        "error": error_message,
        "timestamp": firestore.SERVER_TIMESTAMP
    })
