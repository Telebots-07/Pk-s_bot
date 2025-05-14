from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.logger import log_error

async def tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show interactive tutorial."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    try:
        text = "📚 Welcome to the Cloner Bot Tutorial!\nStep 1: Upload files or request them in the group."
        keyboard = [
            [InlineKeyboardButton("Next ➡️", callback_data="tutorial_next"),
             InlineKeyboardButton("Back ⬅️", callback_data="main_menu")]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        logger.info(f"✅ Tutorial started for {user_id}")
    except Exception as e:
        await query.message.reply_text("⚠️ Failed to show tutorial!")
        await log_error(f"Tutorial error for {user_id}: {str(e)}")
