from firebase_admin import firestore

def initialize_firestore():
    """Initialize Firestore client."""
    return firestore.client()

async def get_group_link(context):
    """Get dynamic group link from Firestore or env var."""
    db = context.bot_data.get("firestore_db")
    settings_doc = db.collection("settings").document("bot_config").get()
    if settings_doc.exists:
        return settings_doc.to_dict().get("request_group_link")
    return None

def log_error(error_message: str):
    """Log error to Firestore."""
    db = firestore.client()
    db.collection("logs").add({
        "error": error_message,
        "timestamp": firestore.SERVER_TIMESTAMP
    })
