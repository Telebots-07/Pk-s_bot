from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.logging_utils import log_error

async def batch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle batch operations."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    if str(user_id) not in context.bot_data.get("admin_ids", []):
        await query.message.reply_text("⚠️ Admins only!")
        await log_error(f"Unauthorized batch access by {user_id}")
        return

    try:
        if query.data == "generate_batch":
            await query.message.reply_text(
                "📦 Enter batch details for file cloning.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Cancel ❌", callback_data="cancel_batch")]
                ])
            )
            context.user_data["batching"] = True
            logger.info(f"✅ Batch generation initiated by {user_id}")
        else:
            await query.message.reply_text("⚠️ Unsupported batch action!")
            await log_error(f"Unsupported batch action by {user_id}: {query.data}")
    except Exception as e:
        await query.message.reply_text("⚠️ Failed to process batch operation!")
        await log_error(f"Batch error for {user_id}: {str(e)}")
