from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from utils.db_channel import get_setting
from utils.logging_utils import log_error
import logging

logger = logging.getLogger(__name__)

def handle_request(update: Update, context: CallbackContext):
    """📬 Handle user file requests, redirect non-admins to group."""
    user_id = update.effective_user.id
    admin_ids = context.bot_data.get("admin_ids", [])

    try:
        if str(user_id) in admin_ids:
            request_text = update.message.text.strip()
            update.message.reply_text(
                f"📬 Admin, your request: '{request_text}' has been noted! 🔍\n"
                "We'll process it in the storage channels! 🗄️"
            )
            logger.info(f"✅ Admin {user_id} submitted request: {request_text}! 🌟")
        else:
            group_link = get_setting("group_link", "https://t.me/+default_group")
            if not group_link.startswith("https://t.me/"):
                group_link = "https://t.me/+default_group"
                log_error(f"⚠️ Invalid group link for user {user_id}, using default")
            update.message.reply_text(
                "📬 Please submit file requests in our group! 🌐",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Join Group 🚀", url=group_link)]
                ])
            )
            logger.info(f"✅ Non-admin {user_id} redirected to group for request! 🌟")
    except Exception as e:
        update.message.reply_text("⚠️ Oops! Request failed! Try again! 😅")
        log_error(f"🚨 Request error for user {user_id}: {str(e)}")
