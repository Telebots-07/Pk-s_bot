from telegram import Update
from telegram.ext import ContextTypes
from utils.logging_utils import log_error

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    user_id = update.effective_user.id if update else "unknown"
    try:
        error = context.error
        error_msg = f"⚠️ Error: {str(error)}"
        await log_error(f"Error for {user_id}: {error_msg}")
        if update and update.message:
            await update.message.reply_text("⚠️ An error occurred. Please try again!")
    except Exception as e:
        await log_error(f"Error handler error for {user_id}: {str(e)}")
