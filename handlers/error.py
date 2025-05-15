from telegram import Update  # Added import for Update
from telegram.ext import CallbackContext
from utils.logging_utils import log_error
import logging

logger = logging.getLogger(__name__)

def error_handler(update: Update, context: CallbackContext):
    """🚨 Log errors and notify the user."""
    user_id = str(update.effective_user.id) if update and update.effective_user else "unknown"
    error_msg = f"🚨 Update caused error for user {user_id}: {str(context.error)}"
    logger.error(error_msg)
    log_error(error_msg)
    if update and update.message:
        update.message.reply_text("⚠️ Something went wrong! Try again! 😅")
    else:
        logger.warning("⚠️ Error occurred, but no update to reply to.")
