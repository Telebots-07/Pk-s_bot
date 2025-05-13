import os

def load_settings():
    """Load settings from Render env vars."""
    return {
        "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),
        "ADMIN_IDS": os.getenv("ADMIN_IDS", "").split(","),
        "PRIVATE_CHANNEL_ID": os.getenv("PRIVATE_CHANNEL_ID"),
        "REQUEST_GROUP_LINK": os.getenv("REQUEST_GROUP_LINK"),
        "FIREBASE_CREDENTIALS": os.getenv("FIREBASE_CREDENTIALS")
    }
