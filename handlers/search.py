from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.db_channel import get_setting
from utils.logger import log_error

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Redirect /search to group for non-admins."""
    user_id = update.effective_user.id
    admin_ids = context.bot_data.get("admin_ids", [])

    try:
        if str(user_id) in admin_ids:
            await update.message.reply_text(
                "🔍 Search files in storage channels.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Search Files 🔍", callback_data="search_files")]
                ])
            )
            logger.info(f"✅ Search menu shown for admin {user_id}")
        else:
            group_link = await get_setting("group_link", "https://t.me/+default_group")
            if not group_link.startswith("https://t.me/"):
                group_link = "https://t.me/+default_group"
                await log_error(f"Invalid group link for {user_id}, using default")
            await update.message.reply_text(
                "🔍 Please use the group to search or request files!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Join Group 🌐", url=group_link)]
                ])
            )
            logger.info(f"✅ Search redirect for non-admin {user_id}")
    except Exception as e:
        await update.message.reply_text("⚠️ Failed to process search command!")
        await log_error(f"Search error for {user_id}: {str(e)}")
