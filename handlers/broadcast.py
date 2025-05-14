from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.db_channel import get_setting
from utils.logger import log_error

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle broadcast messages."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    if str(user_id) not in context.bot_data.get("admin_ids", []):
        await query.message.reply_text("⚠️ Admins only!")
        await log_error(f"Unauthorized broadcast access by {user_id}")
        return

    try:
        await query.message.reply_text(
            "📢 Enter the broadcast message.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Cancel ❌", callback_data="cancel_broadcast")]
            ])
        )
        context.user_data["broadcasting"] = True
        logger.info(f"✅ Broadcast initiated by {user_id}")
    except Exception as e:
        await query.message.reply_text("⚠️ Failed to initiate broadcast!")
        await log_error(f"Broadcast error for {user_id}: {str(e)}")
