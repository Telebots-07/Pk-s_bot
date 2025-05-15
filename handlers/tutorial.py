from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from utils.db_channel import get_setting
from utils.logging_utils import log_error
import logging

logger = logging.getLogger(__name__)

def tutorial(update: Update, context: CallbackContext):
    """📚 Show a tutorial on using the Cloner Bot!"""
    user_id = update.effective_user.id
    admin_ids = context.bot_data.get("admin_ids", [])

    try:
        if str(user_id) not in admin_ids:
            update.callback_query.answer("🚫 Admins only!")
            log_error(f"🚨 Unauthorized tutorial access by {user_id}")
            return

        group_link = get_setting("group_link", "https://t.me/+default_group")
        if not group_link.startswith("https://t.me/"):
            group_link = "https://t.me/+default_group"
            log_error(f"⚠️ Invalid group link for user {user_id}, using default")

        update.callback_query.message.reply_text(
            "📚 Cloner Bot Tutorial! 🌟\n\n"
            "Welcome to @bot_paiyan_official! Here’s how to use me:\n"
            "1. 🔍 Use /search to find files in storage channels.\n"
            "2. 📬 Send text to request files (non-admins, join the group!).\n"
            "3. 🤖 Create clone bots via Settings > Clone Bots.\n"
            "4. 📝 Customize captions/buttons in Settings.\n"
            "5. 📢 Broadcast messages to users (admins only).\n\n"
            "Need help? Join our group! 🚀",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Join Group 🌐", url=group_link)],
                [InlineKeyboardButton("Back to Menu ↩️", callback_data="settings")]
            ])
        )
        logger.info(f"✅ Admin {user_id} viewed tutorial! 🎉")
    except Exception as e:
        update.callback_query.message.reply_text("⚠️ Oops! Tutorial failed! Try again! 😅")
        log_error(f"🚨 Tutorial error for user {user_id}: {str(e)}")
