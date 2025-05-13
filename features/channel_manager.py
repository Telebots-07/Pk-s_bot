from telegram.ext import ContextTypes
from utils.logger import log_error

async def get_active_channel(context: ContextTypes.DEFAULT_TYPE):
    """Get an active storage channel."""
    try:
        db = context.bot_data.get("firestore_db")
        channels = db.collection("storage_channels").where("active", "==", True).get()
        return channels[0].to_dict().get("channel_id") if channels else os.getenv("PRIVATE_CHANNEL_ID")
    except Exception as e:
        log_error(f"Channel manager error: {str(e)}")
        return os.getenv("PRIVATE_CHANNEL_ID")
