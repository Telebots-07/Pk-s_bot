from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from utils.db_channel import get_setting, set_setting
from utils.logging_utils import log_error
import logging

logger = logging.getLogger(__name__)

def create_clone_bot(update: Update, context: CallbackContext):
    """🤖 Create a new cloned bot (main bot only)."""
    user_id = update.effective_user.id
    if str(user_id) not in context.bot_data.get("admin_ids", []):
        update.callback_query.answer("🚫 Admins only!")
        log_error(f"🚨 Unauthorized clone bot creation by {user_id}")
        return
    if not context.bot_data.get("is_main_bot", False):
        update.callback_query.answer("🚫 Main bot only!")
        log_error(f"🚨 Unauthorized clone bot creation by {user_id} on clone")
        return

    try:
        context.user_data["awaiting_clone_token"] = True
        update.callback_query.message.reply_text(
            "🤖 Send the Telegram Bot Token for the new cloned bot! 🔑",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Cancel 🚫", callback_data="cancel_clone")]
            ])
        )
        logger.info(f"✅ Admin {user_id} started cloning bot! 🌟")
    except Exception as e:
        update.callback_query.message.reply_text("⚠️ Failed to start cloning! Try again! 😅")
        log_error(f"🚨 Clone bot error for {user_id}: {str(e)}")

def view_clone_bots(update: Update, context: CallbackContext):
    """🤖 View all cloned bots (main bot only)."""
    user_id = update.effective_user.id
    if str(user_id) not in context.bot_data.get("admin_ids", []):
        update.callback_query.answer("🚫 Admins only!")
        log_error(f"🚨 Unauthorized view clone bots by {user_id}")
        return
    if not context.bot_data.get("is_main_bot", False):
        update.callback_query.answer("🚫 Main bot only!")
        log_error(f"🚨 Unauthorized view clone bots by {user_id} on clone")
        return

    try:
        cloned_bots = get_setting("cloned_bots", [])
        if not cloned_bots:
            update.callback_query.message.reply_text("⚠️ No cloned bots found! Create one first! 😅")
            logger.info(f"✅ Admin {user_id} viewed clone bots - none found! 🌟")
            return
        response = "🤖 Cloned Bots:\n\n" + "\n".join([f"🔑 Token ending: {bot['token'][-4:]}" for bot in cloned_bots])
        update.callback_query.message.reply_text(response)
        logger.info(f"✅ Admin {user_id} viewed {len(cloned_bots)} cloned bots! 🌟")
    except Exception as e:
        update.callback_query.message.reply_text("⚠️ Failed to view cloned bots! Try again! 😅")
        log_error(f"🚨 View clone bots error for {user_id}: {str(e)}")

def handle_clone_input(update: Update, context: CallbackContext):
    """🤖 Handle bot token input for cloning."""
    user_id = update.effective_user.id
    if not context.user_data.get("awaiting_clone_token"):
        return
    if str(user_id) not in context.bot_data.get("admin_ids", []):
        update.message.reply_text("🚫 Admins only!")
        log_error(f"🚨 Unauthorized clone input by {user_id}")
        return
    if not context.bot_data.get("is_main_bot", False):
        update.message.reply_text("🚫 Main bot only!")
        log_error(f"🚨 Unauthorized clone input by {user_id} on clone")
        return

    try:
        token = update.message.text.strip()
        cloned_bots = get_setting("cloned_bots", [])
        cloned_bots.append({"token": token})
        set_setting("cloned_bots", cloned_bots)
        context.user_data["awaiting_clone_token"] = None
        update.message.reply_text("✅ Cloned bot added! Restart the bot to activate! 🎉")
        logger.info(f"✅ Admin {user_id} added cloned bot with token ending {token[-4:]}! 🌟")
    except Exception as e:
        update.message.reply_text("⚠️ Failed to add cloned bot! Check token! 😅")
        log_error(f"🚨 Clone input error for {user_id}: {str(e)}")
