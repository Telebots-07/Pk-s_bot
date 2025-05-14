from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from utils.db_channel import get_setting
from utils.logging_utils import log_error
import logging

logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext):
    """Handle the /start command and display the main menu."""
    user_id = update.effective_user.id
    is_admin = str(user_id) in context.bot_data.get("admin_ids", [])

    welcome_message = get_setting("welcome_message", "Welcome to @bot_paiyan_official's Cloner Bot!")
    keyboard = [
        [InlineKeyboardButton("Settings", callback_data="settings"),
         InlineKeyboardButton("Tutorial", callback_data="tutorial")],
        [InlineKeyboardButton("Search", callback_data="search"),
         InlineKeyboardButton("Create Clone Bot", callback_data="create_clone_bot")]
    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton("View Clone Bots", callback_data="view_clone_bots")])
        keyboard.append([InlineKeyboardButton("Broadcast", callback_data="broadcast")])
        keyboard.append([InlineKeyboardButton("Batch", callback_data="batch")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(welcome_message, reply_markup=reply_markup)
    logger.info(f"Start command executed by user {user_id}")

def settings_menu(update: Update, context: CallbackContext):
    """Display the settings menu for admins."""
    user_id = update.effective_user.id
    if str(user_id) not in context.bot_data.get("admin_ids", []):
        update.callback_query.answer("Admins only!")
        log_error(f"Unauthorized settings access by {user_id}")
        return

    keyboard = [
        [InlineKeyboardButton("Add Channel", callback_data="add_channel"),
         InlineKeyboardButton("Remove Channel", callback_data="remove_channel")],
        [InlineKeyboardButton("Set Force Sub", callback_data="set_force_sub"),
         InlineKeyboardButton("Set Group Link", callback_data="set_group_link")],
        [InlineKeyboardButton("Set DB Channel", callback_data="set_db_channel"),
         InlineKeyboardButton("Set Log Channel", callback_data="set_log_channel")],
        [InlineKeyboardButton("Shortener", callback_data="shortener"),
         InlineKeyboardButton("Welcome Message", callback_data="welcome_message")],
        [InlineKeyboardButton("Auto Delete", callback_data="auto_delete"),
         InlineKeyboardButton("Banner", callback_data="banner")],
        [InlineKeyboardButton("Set Webhook", callback_data="set_webhook"),
         InlineKeyboardButton("Anti-Ban", callback_data="anti_ban")],
        [InlineKeyboardButton("Enable Redis", callback_data="enable_redis")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.reply_text("Settings Menu:", reply_markup=reply_markup)
    logger.info(f"Settings menu accessed by admin {user_id}")
