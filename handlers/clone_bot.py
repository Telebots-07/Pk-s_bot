from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from utils.db_channel import store_cloned_bot, get_cloned_bots
from utils.logging_utils import log_error
import logging

logger = logging.getLogger(__name__)

def create_clone_bot(update: Update, context: CallbackContext):
    """Initiate the process to create a cloned bot."""
    user_id = update.effective_user.id
    if str(user_id) not in context.bot_data.get("admin_ids", []):
        update.callback_query.answer("Admins only!")
        log_error(f"Unauthorized clone bot creation by {user_id}")
        return

    context.user_data["awaiting_clone_token"] = True
    update.callback_query.message.reply_text("Please send the bot token for the new cloned bot.")
    logger.info(f"Clone bot creation initiated by admin {user_id}")

def view_clone_bots(update: Update, context: CallbackContext):
    """Display a list of all cloned bots."""
    user_id = update.effective_user.id
    if str(user_id) not in context.bot_data.get("admin_ids", []):
        update.callback_query.answer("Admins only!")
        log_error(f"Unauthorized clone bot view by {user_id}")
        return

    try:
        cloned_bots = get_cloned_bots()
        if not cloned_bots:
            update.callback_query.message.reply_text("No cloned bots found.")
            logger.info(f"No cloned bots found for admin {user_id}")
            return

        message = "Cloned Bots:\n"
        for bot in cloned_bots:
            token = bot["token"][-4:]  # Show last 4 digits for security
            message += f"- Bot with token ending {token}\n"
        update.callback_query.message.reply_text(message)
        logger.info(f"Cloned bots viewed by admin {user_id}")
    except Exception as e:
        update.callback_query.message.reply_text("Failed to retrieve cloned bots!")
        log_error(f"Error viewing cloned bots for {user_id}: {str(e)}")

def handle_clone_input(update: Update, context: CallbackContext):
    """Handle the bot token input for creating a cloned bot."""
    user_id = update.effective_user.id
    if not context.user_data.get("awaiting_clone_token", False):
        return

    if str(user_id) not in context.bot_data.get("admin_ids", []):
        update.message.reply_text("Admins only!")
        log_error(f"Unauthorized clone input by {user_id}")
        return

    token = update.message.text.strip()
    try:
        # Validate token format (basic check)
        if not token.startswith("bot") and ":" not in token:
            update.message.reply_text("Invalid bot token format!")
            log_error(f"Invalid bot token format by {user_id}")
            return

        # Store the cloned bot
        store_cloned_bot({"token": token, "created_by": user_id})
        context.user_data["awaiting_clone_token"] = False
        update.message.reply_text(
            "Cloned bot added! Restarting bot to apply changes.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Restart Bot", callback_data="restart_bot")]
            ])
        )
        logger.info(f"Cloned bot added by admin {user_id} with token ending {token[-4:]}")
    except Exception as e:
        update.message.reply_text("Failed to add cloned bot!")
        log_error(f"Error adding cloned bot for {user_id}: {str(e)}")
