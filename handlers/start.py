from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from utils.logging_utils import log_error
import logging

logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext):
    """🚀 Welcome users to the Cloner Bot with a cool menu for admins!"""
    user_id = update.effective_user.id
    admin_ids = context.bot_data.get("admin_ids", [])

    try:
        if str(user_id) in admin_ids:
            update.message.reply_text(
                "👋 Yo, admin! Welcome to @bot_paiyan_official! 🌟\n"
                "Manage your bot empire from here! 💪",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔍 Search Files", callback_data="search_files")],
                    [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
                    [InlineKeyboardButton("🤖 Clone Bots", callback_data="view_clone_bots")],
                    [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")],
                    [InlineKeyboardButton("📝 Tutorial", callback_data="tutorial")]
                ])
            )
            logger.info(f"✅ Admin {user_id} started bot with menu! 🎉")
        else:
            update.message.reply_text(
                "👋 Welcome to @bot_paiyan_official! 🎈\n"
                "Use /search to find files or join our group! 🔍"
            )
            logger.info(f"✅ User {user_id} started bot! 🌟")
    except Exception as e:
        update.message.reply_text("⚠️ Oops! Something broke! Try again! 😅")
        log_error(f"🚨 Start error for user {user_id}: {str(e)}")

def settings_menu(update: Update, context: CallbackContext):
    """⚙️ Show admin settings menu."""
    user_id = update.effective_user.id
    if str(user_id) not in context.bot_data.get("admin_ids", []):
        update.callback_query.answer("🚫 Admins only!")
        log_error(f"🚨 Unauthorized settings access by {user_id}")
        return

    try:
        update.callback_query.message.reply_text(
            "⚙️ Bot Settings Menu! Tweak your bot here! 🛠️",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📝 Set Caption", callback_data="set_custom_caption")],
                [InlineKeyboardButton("🔘 Set Buttons", callback_data="set_custom_buttons")],
                [InlineKeyboardButton("📺 Add Channel", callback_data="add_channel")],
                [InlineKeyboardButton("🗑️ Remove Channel", callback_data="remove_channel")],
                [InlineKeyboardButton("🔗 Set Group Link", callback_data="set_group_link")]
            ])
        )
        logger.info(f"✅ Admin {user_id} opened settings menu! 🌟")
    except Exception as e:
        update.callback_query.message.reply_text("⚠️ Failed to load settings! Try again! 😅")
        log_error(f"🚨 Settings menu error for {user_id}: {str(e)}")
