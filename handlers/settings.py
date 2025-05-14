from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.db_channel import set_setting, get_setting
from utils.logger import log_error
from handlers.start import shortener_menu, handle_shortener_selection, handle_shortener_input

async def handle_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle settings configuration."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    if str(user_id) not in context.bot_data.get("admin_ids", []):
        await query.message.reply_text("⚠️ Admins only!")
        await log_error(f"Unauthorized settings access by {user_id}")
        return

    action = query.data
    try:
        if action == "add_channel":
            await query.message.reply_text(
                "➕ Enter the channel ID (e.g., -100123456789).",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Cancel ❌", callback_data="cancel_setting")]
                ])
            )
            context.user_data["setting_action"] = "add_channel"
            logger.info(f"✅ Add channel initiated by {user_id}")
        elif action == "shortener":
            await shortener_menu(update, context)
        elif action in ["set_shortener_gplinks", "set_shortener_modijiurl", "set_shortener_other"]:
            await handle_shortener_selection(update, context)
        else:
            await query.message.reply_text("⚠️ Unsupported setting action!")
            await log_error(f"Unsupported setting action by {user_id}: {action}")
    except Exception as e:
        await query.message.reply_text("⚠️ Failed to process setting!")
        await log_error(f"Settings error for {user_id}: {str(e)}")
