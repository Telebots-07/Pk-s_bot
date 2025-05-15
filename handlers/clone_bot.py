from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from utils.db_channel import store_cloned_bot
from utils.logging_utils import log_error
import logging

logger = logging.getLogger(__name__)

def create_clone_bot(update: Update, context: CallbackContext):
    """🤖 Initiate cloning a new bot."""
    user_id = update.effective_user.id
    if str(user_id) not in context.bot_data.get("admin_ids", []):
        update.callback_query.answer("🚫 Admins only!")
        log_error(f"🚨 Unauthorized clone attempt by {user_id}")
        return

    context.user_data["awaiting_clone_token"] = True
    update.callback_query.message.reply_text(
        "🤖 Send the Telegram bot token for the new clone! 🔑"
    )
    logger.info(f"✅ Clone bot creation started by admin {user_id}! 🌟")

def view_clone_bots(update: Update, context: CallbackContext):
    """📋 Show list of cloned bots."""
    user_id = update.effective_user.id
    if str(user_id) not in context.bot_data.get("admin_ids", []):
        update.callback_query.answer("🚫 Admins only!")
        log_error(f"🚨 Unauthorized view attempt by {user_id}")
        return

    try:
        cloned_bots = context.bot_data.get("cloned_bots", [])
        if not cloned_bots:
            update.callback_query.message.reply_text("📋 No cloned bots found! 😕")
            logger.info(f"✅ Admin {user_id} viewed empty clone list")
            return

        message = "📋 Cloned Bots:\n"
        for bot in cloned_bots:
            message += f"🔑 Token ending: {bot['token'][-4:]}, Created by: {bot['created_by']}\n"
        update.callback_query.message.reply_text(message)
        logger.info(f"✅ Admin {user_id} viewed clone list! 🌟")
    except Exception as e:
        update.callback_query.message.reply_text("⚠️ Failed to view clones! Try again! 😅")
        log_error(f"🚨 Error viewing clones for {user_id}: {str(e)}")

def handle_clone_input(update: Update, context: CallbackContext):
    """🔧 Handle bot token input for cloning."""
    user_id = update.effective_user.id
    if not context.user_data.get("awaiting_clone_token", False):
        return

    if str(user_id) not in context.bot_data.get("admin_ids", []):
        update.message.reply_text("🚫 Admins only!")
        log_error(f"🚨 Unauthorized clone input by {user_id}")
        return

    token = update.message.text.strip()
    try:
        bot_data = {"token": token, "created_by": user_id}
        store_cloned_bot(bot_data)
        context.user_data["awaiting_clone_token"] = False
        update.message.reply_text("✅ Bot cloned successfully! 🎉")
        logger.info(f"✅ Admin {user_id} cloned bot with token ending {token[-4:]}! 🌟")
    except Exception as e:
        update.message.reply_text("⚠️ Failed to clone bot! Check token! 😅")
        log_error(f"🚨 Error cloning bot for {user_id}: {str(e)}")
