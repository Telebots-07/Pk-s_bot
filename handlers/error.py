from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import log_error

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors globally."""
    error = context.error
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text("⚠️ An error occurred. Please try again.")
        log_error(f"Bot error: {str(error)}")
    except Exception as e:
        log_error(f"Error handler error: {str(e)}")
