from telegram import Update
from telegram.ext import CallbackContext
import logging

logger = logging.getLogger(__name__)

def error_handler(update: Update, context: CallbackContext):
    """⚠️ Handle errors with style and log them! 🚨"""
    logger.error(f"🚨 Exception occurred: {context.error}")
    if update and update.effective_message:
        update.effective_message.reply_text("⚠️ Oops! Something broke! Hang tight! 😅")
