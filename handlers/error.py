from telegram import Update
from telegram.ext import CallbackContext
from utils.logging_utils import log_error
import logging

logger = logging.getLogger(__name__)

def error_handler(update: Update, context: CallbackContext):
    """🚨 Handle errors and log them."""
    try:
        error = context.error
        user_id = update.effective_user.id if update.effective_user else "Unknown"
        log_error(f"🚨 Error for user {user_id}: {str(error)}")
        if update:
            update.message.reply_text("⚠️ An error occurred! Try again later! 😅")
    except Exception as e:
        log_error(f"🚨 Error handler failed: {str(e)}")
