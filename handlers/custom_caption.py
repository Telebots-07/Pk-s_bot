from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from utils.db_channel import set_setting, get_setting
from utils.logging_utils import log_error
import logging

logger = logging.getLogger(__name__)

def set_custom_caption(update: Update, context: CallbackContext):
    """Initiate setting a custom caption."""
    user_id = update.effective_user.id
    if str(user_id) not in context.bot_data.get("admin_ids", []):
        update.callback_query.answer("Admins only!")
        log_error(f"Unauthorized caption set by {user_id}")
        return

    context.user_data["awaiting_caption"] = True
    update.callback_query.message.reply_text(
        "Please send the custom caption. Use placeholders like {filename}, {date}, {size}, {file_id}, {user_id}, {file_link}."
    )
    logger.info(f"Custom caption setting initiated by admin {user_id}")

def set_custom_buttons(update: Update, context: CallbackContext):
    """Initiate setting custom buttons."""
    user_id = update.effective_user.id
    if str(user_id) not in context.bot_data.get("admin_ids", []):
        update.callback_query.answer("Admins only!")
        log_error(f"Unauthorized button set by {user_id}")
        return

    context.user_data["awaiting_buttons"] = True
    update.callback_query.message.reply_text(
        "Please send the custom buttons in JSON format. Example:\n"
        '[{"text": "Download", "url": "{file_link}"}, {"text": "Share", "callback": "share_file_{file_id}"}]'
    )
    logger.info(f"Custom buttons setting initiated by admin {user_id}")

def handle_caption_input(update: Update, context: CallbackContext):
    """Handle the custom caption input."""
    user_id = update.effective_user.id
    if not context.user_data.get("awaiting_caption", False):
        return

    if str(user_id) not in context.bot_data.get("admin_ids", []):
        update.message.reply_text("Admins only!")
        log_error(f"Unauthorized caption input by {user_id}")
        return

    caption = update.message.text.strip()
    try:
        set_setting("custom_caption", caption)
        context.user_data["awaiting_caption"] = False
        update.message.reply_text("Custom caption set successfully!")
        logger.info(f"Custom caption set by admin {user_id}")
    except Exception as e:
        update.message.reply_text("Failed to set custom caption!")
        log_error(f"Error setting custom caption for {user_id}: {str(e)}")

def handle_buttons_input(update: Update, context: CallbackContext):
    """Handle the custom buttons input."""
    user_id = update.effective_user.id
    if not context.user_data.get("awaiting_buttons", False):
        return

    if str(user_id) not in context.bot_data.get("admin_ids", []):
        update.message.reply_text("Admins only!")
        log_error(f"Unauthorized button input by {user_id}")
        return

    buttons_text = update.message.text.strip()
    try:
        buttons = json.loads(buttons_text)
        if not isinstance(buttons, list):
            raise ValueError("Buttons must be a list")
        set_setting("custom_buttons", buttons)
        context.user_data["awaiting_buttons"] = False
        update.message.reply_text("Custom buttons set successfully!")
        logger.info(f"Custom buttons set by admin {user_id}")
    except Exception as e:
        update.message.reply_text("Failed to set custom buttons! Ensure valid JSON format.")
        log_error(f"Error setting custom buttons for {user_id}: {str(e)}")
