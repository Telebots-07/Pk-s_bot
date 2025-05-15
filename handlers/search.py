from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from utils.db_channel import get_setting
from utils.logging_utils import log_error
import logging

logger = logging.getLogger(__name__)

def search(update: Update, context: CallbackContext):
    """🔍 Redirect /search to group for non-admins or show admin search menu."""
    user_id = update.effective_user.id
    admin_ids = context.bot_data.get("admin_ids", [])

    try:
        if str(user_id) in admin_ids:
            update.message.reply_text(
                "🔍 Search files in storage channels! 🗄️",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Search Files 🔎", callback_data="search_files")]
                ])
            )
            logger.info(f"✅ Admin {user_id} saw search menu! 🎉")
        else:
            group_link = get_setting("group_link", "https://t.me/+default_group")
            if not group_link.startswith("https://t.me/"):
                group_link = "https://t.me/+default_group"
                log_error(f"⚠️ Invalid group link for user {user_id}, using default")
            update.message.reply_text(
                "🔍 Join the group to search or request files! 🌐",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Join Group 🚀", url=group_link)]
                ])
            )
            logger.info(f"✅ Non-admin {user_id} redirected to group! 🌟")
    except Exception as e:
        update.message.reply_text("⚠️ Oops, search failed! Try again! 😅")
        log_error(f"🚨 Search error for user {user_id}: {str(e)}")
