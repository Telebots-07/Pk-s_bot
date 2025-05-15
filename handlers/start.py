from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from utils.db_channel import set_setting, get_setting
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
                [InlineKeyboardButton("🔗 Set Group Link", callback_data="set_group_link")],
                [InlineKeyboardButton("🔗 URL Shortener", callback_data="shortener")],
                [InlineKeyboardButton("📦 Batch Operations", callback_data="batch_menu")]
            ])
        )
        logger.info(f"✅ Admin {user_id} opened settings menu! 🌟")
    except Exception as e:
        update.callback_query.message.reply_text("⚠️ Failed to load settings! Try again! 😅")
        log_error(f"🚨 Settings menu error for {user_id}: {str(e)}")

def batch_menu(update: Update, context: CallbackContext):
    """📦 Show batch operations menu."""
    user_id = update.effective_user.id
    if str(user_id) not in context.bot_data.get("admin_ids", []):
        update.callback_query.answer("🚫 Admins only!")
        log_error(f"🚨 Unauthorized batch menu access by {user_id}")
        return

    try:
        update.callback_query.message.reply_text(
            "📦 Batch Operations! Manage your file batches here! 🛠️",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 Generate Batch", callback_data="generate_batch")],
                [InlineKeyboardButton("✏️ Edit Batch", callback_data="edit_batch")],
                [InlineKeyboardButton("Back to Settings ⚙️", callback_data="settings")]
            ])
        )
        logger.info(f"✅ Admin {user_id} opened batch menu! 🌟")
    except Exception as e:
        update.callback_query.message.reply_text("⚠️ Failed to load batch menu! Try again! 😅")
        log_error(f"🚨 Batch menu error for {user_id}: {str(e)}")

def shortener_menu(update: Update, context: CallbackContext):
    """🔗 Show URL shortener options for admins."""
    user_id = update.effective_user.id
    if str(user_id) not in context.bot_data.get("admin_ids", []):
        update.callback_query.answer("🚫 Admins only!")
        log_error(f"🚨 Unauthorized shortener access by {user_id}")
        return

    try:
        update.callback_query.message.reply_text(
            "🔗 Choose a URL shortener service! 🛠️",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 GPLinks", callback_data="shortener_gplinks")],
                [InlineKeyboardButton("🔗 TinyURL", callback_data="shortener_tinyurl")],
                [InlineKeyboardButton("🔗 None (Disable)", callback_data="shortener_none")]
            ])
        )
        logger.info(f"✅ Admin {user_id} opened shortener menu! 🌟")
    except Exception as e:
        update.callback_query.message.reply_text("⚠️ Failed to load shortener menu! Try again! 😅")
        log_error(f"🚨 Shortener menu error for {user_id}: {str(e)}")

def handle_shortener_selection(update: Update, context: CallbackContext):
    """🔧 Process shortener selection."""
    user_id = update.effective_user.id
    if str(user_id) not in context.bot_data.get("admin_ids", []):
        update.callback_query.answer("🚫 Admins only!")
        log_error(f"🚨 Unauthorized shortener selection by {user_id}")
        return

    try:
        callback_data = update.callback_query.data
        if callback_data == "shortener_none":
            set_setting("shortener_service", "none")
            update.callback_query.message.reply_text("✅ Shortener disabled! 🎉")
            logger.info(f"✅ Admin {user_id} disabled shortener! 🌟")
        else:
            service = callback_data.split("_")[1]  # e.g., "gplinks" or "tinyurl"
            context.user_data["awaiting_shortener_input"] = service
            update.callback_query.message.reply_text(
                f"🔗 Enter the API key or base URL for {service}! 🛠️"
            )
            logger.info(f"✅ Admin {user_id} selected shortener: {service}! 🌟")
    except Exception as e:
        update.callback_query.message.reply_text("⚠️ Failed to select shortener! Try again! 😅")
        log_error(f"🚨 Shortener selection error for {user_id}: {str(e)}")

def handle_shortener_input(update: Update, context: CallbackContext):
    """📝 Save shortener API key or URL."""
    user_id = update.effective_user.id
    if not context.user_data.get("awaiting_shortener_input"):
        return

    if str(user_id) not in context.bot_data.get("admin_ids", []):
        update.message.reply_text("🚫 Admins only!")
        log_error(f"🚨 Unauthorized shortener input by {user_id}")
        return

    try:
        service = context.user_data["awaiting_shortener_input"]
        api_key = update.message.text.strip()
        set_setting(f"shortener_{service}", api_key)
        set_setting("shortener_service", service)
        context.user_data["awaiting_shortener_input"] = None
        update.message.reply_text(f"✅ {service} shortener set! 🎉")
        logger.info(f"✅ Admin {user_id} set {service} shortener! 🌟")
    except Exception as e:
        update.message.reply_text("⚠️ Failed to set shortener! Check input! 😅")
        log_error(f"🚨 Shortener input error for {user_id}: {str(e)}")
