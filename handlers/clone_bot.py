from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import CallbackContext
from telegram.error import TelegramError, Unauthorized, NetworkError
from utils.db_channel import get_setting, set_setting
from utils.logging_utils import log_error
import logging
import os

logger = logging.getLogger(__name__)

def create_clone_bot(update: Update, context: CallbackContext):
    """🤖 Prompt for bot type visibility before creating a new cloned bot (main bot only)."""
    user_id = str(update.effective_user.id)
    if user_id not in context.bot_data.get("admin_ids", []):
        update.callback_query.answer("🚫 Admins only!")
        log_error(f"🚨 Unauthorized clone bot creation by {user_id}")
        return
    if not context.bot_data.get("is_main_bot", False):
        update.callback_query.answer("🚫 Main bot only!")
        log_error(f"🚨 Unauthorized clone bot creation by {user_id} on clone")
        return

    try:
        # Prompt for visibility type
        update.callback_query.message.reply_text(
            "🤖 Choose the visibility for the new cloned bot! 🔒",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔒 Private (Only You)", callback_data="visibility_private")],
                [InlineKeyboardButton("🌍 Public (Everyone)", callback_data="visibility_public")],
                [InlineKeyboardButton("Cancel 🚫", callback_data="cancel_clone")]
            ])
        )
        logger.info(f"✅ Admin {user_id} started cloning bot - selecting visibility! 🌟")
    except Exception as e:
        update.callback_query.message.reply_text("⚠️ Failed to start cloning! Try again! 😅")
        log_error(f"🚨 Clone bot error for {user_id}: {str(e)}")

def handle_visibility_selection(update: Update, context: CallbackContext):
    """🔒 Handle visibility selection and prompt for bot usage."""
    user_id = str(update.effective_user.id)
    if user_id not in context.bot_data.get("admin_ids", []):
        update.callback_query.answer("🚫 Admins only!")
        log_error(f"🚨 Unauthorized visibility selection by {user_id}")
        return
    if not context.bot_data.get("is_main_bot", False):
        update.callback_query.answer("🚫 Main bot only!")
        log_error(f"🚨 Unauthorized visibility selection by {user_id} on clone")
        return

    try:
        callback_data = update.callback_query.data
        if callback_data == "cancel_clone":
            update.callback_query.message.reply_text("🚫 Cloning cancelled! 😅")
            logger.info(f"✅ Admin {user_id} cancelled cloning! 🌟")
            return

        # Store visibility selection
        visibility = "private" if callback_data == "visibility_private" else "public"
        context.user_data["new_bot_visibility"] = visibility

        # Prompt for bot usage
        update.callback_query.message.reply_text(
            f"🤖 Visibility set to {visibility.upper()}! 🔒\n"
            "Now choose the usage for the new cloned bot! 🛠️",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📦 File Store (GenLink/Batch)", callback_data="usage_filestore")],
                [InlineKeyboardButton("🔍 Search Bot", callback_data="usage_searchbot")],
                [InlineKeyboardButton("Cancel 🚫", callback_data="cancel_clone")]
            ])
        )
        logger.info(f"✅ Admin {user_id} set visibility to {visibility} and awaiting usage selection! 🌟")
    except Exception as e:
        update.callback_query.message.reply_text("⚠️ Failed to set visibility! Try again! 😅")
        log_error(f"🚨 Visibility selection error for {user_id}: {str(e)}")

def handle_usage_selection(update: Update, context: CallbackContext):
    """🛠️ Handle bot usage selection and prompt for bot token."""
    user_id = str(update.effective_user.id)
    if user_id not in context.bot_data.get("admin_ids", []):
        update.callback_query.answer("🚫 Admins only!")
        log_error(f"🚨 Unauthorized usage selection by {user_id}")
        return
    if not context.bot_data.get("is_main_bot", False):
        update.callback_query.answer("🚫 Main bot only!")
        log_error(f"🚨 Unauthorized usage selection by {user_id} on clone")
        return

    try:
        callback_data = update.callback_query.data
        if callback_data == "cancel_clone":
            update.callback_query.message.reply_text("🚫 Cloning cancelled! 😅")
            logger.info(f"✅ Admin {user_id} cancelled cloning! 🌟")
            return

        # Store usage selection
        usage = "filestore" if callback_data == "usage_filestore" else "searchbot"
        context.user_data["new_bot_usage"] = usage
        context.user_data["awaiting_clone_token"] = True

        update.callback_query.message.reply_text(
            f"🤖 Usage set to {usage.upper()}! 🛠️\n"
            "Now send the Telegram Bot Token for the new cloned bot! 🔑",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Cancel 🚫", callback_data="cancel_clone")]
            ])
        )
        logger.info(f"✅ Admin {user_id} set usage to {usage} and awaiting token! 🌟")
    except Exception as e:
        update.callback_query.message.reply_text("⚠️ Failed to set usage! Try again! 😅")
        log_error(f"🚨 Usage selection error for {user_id}: {str(e)}")

def view_clone_bots(update: Update, context: CallbackContext):
    """🤖 View all cloned bots (main bot only)."""
    user_id = str(update.effective_user.id)
    if user_id not in context.bot_data.get("admin_ids", []):
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
        response = "🤖 Cloned Bots:\n\n" + "\n".join([f"🔑 Token ending: {bot['token'][-4:]} | Visibility: {bot['visibility'].upper()} | Usage: {bot['usage'].upper()} | Standalone: {bot.get('standalone', False)}" for bot in cloned_bots])
        update.callback_query.message.reply_text(response)
        logger.info(f"✅ Admin {user_id} viewed {len(cloned_bots)} cloned bots! 🌟")
    except Exception as e:
        update.callback_query.message.reply_text("⚠️ Failed to view cloned bots! Try again! 😅")
        log_error(f"🚨 View clone bots error for {user_id}: {str(e)}")

def handle_clone_input(update: Update, context: CallbackContext):
    """🤖 Handle bot token input for cloning and start the bot dynamically."""
    from bot import start_cloned_bot, bot_instances  # Moved import inside function to avoid circular import

    user_id = str(update.effective_user.id)
    if not context.user_data.get("awaiting_clone_token"):
        return
    if user_id not in context.bot_data.get("admin_ids", []):
        update.message.reply_text("🚫 Admins only!")
        log_error(f"🚨 Unauthorized clone input by {user_id}")
        return
    if not context.bot_data.get("is_main_bot", False):
        update.message.reply_text("🚫 Main bot only!")
        log_error(f"🚨 Unauthorized clone input by {user_id} on clone")
        return

    try:
        token = update.message.text.strip()
        visibility = context.user_data.get("new_bot_visibility", "public")  # Default to public if not set
        usage = context.user_data.get("new_bot_usage", "searchbot")  # Default to searchbot if not set

        # Validate token format (basic check)
        if not token or ":" not in token or len(token.split(":")) != 2:
            update.message.reply_text("⚠️ Invalid token format! It should look like '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'. Try again! 😅")
            logger.info(f"⚠️ Admin {user_id} provided invalid token format: {token}")
            return

        # Verify token with Telegram API
        try:
            bot = Bot(token)
            bot_info = bot.get_me()  # This will raise an exception if the token is invalid
            bot_username = bot_info.username
            logger.info(f"✅ Token verification successful for bot @{bot_username} with token ending {token[-4:]}")
        except Unauthorized:
            update.message.reply_text("⚠️ Token is invalid or revoked! Get a new token from BotFather and try again! 😅")
            logger.error(f"🚨 Token verification failed for user {user_id}: Unauthorized")
            return
        except NetworkError:
            update.message.reply_text("⚠️ Network error while verifying token! Check your connection and try again! 😅")
            logger.error(f"🚨 Token verification failed for user {user_id}: NetworkError")
            return
        except TelegramError as e:
            update.message.reply_text(f"⚠️ Telegram error while verifying token: {str(e)}! Try again! 😅")
            logger.error(f"🚨 Token verification failed for user {user_id}: {str(e)}")
            return
        except Exception as e:
            update.message.reply_text(f"⚠️ Unexpected error while verifying token: {str(e)}! Try again! 😅")
            logger.error(f"🚨 Token verification failed for user {user_id}: {str(e)}")
            return

        cloned_bots = get_setting("cloned_bots", [])
        # Check if token already exists
        existing_bot = next((bot for bot in cloned_bots if bot["token"] == token), None)
        if existing_bot:
            standalone_status = "running independently" if existing_bot.get("standalone", False) else "managed by Cloner Bot"
            update.message.reply_text(f"⚠️ This bot token is already added! It’s @{bot_username} ({standalone_status}). Try a different token! 😅")
            logger.info(f"⚠️ Admin {user_id} tried to add duplicate token ending {token[-4:]} for @{bot_username}")
            return

        # Check if this token matches FILESTORE_TOKEN and verify it
        filestore_token = os.getenv("FILESTORE_TOKEN")
        is_standalone = token == filestore_token
        if is_standalone and usage != "filestore":
            update.message.reply_text("⚠️ The token matches FILESTORE_TOKEN but usage is not set to File Store! Please set usage to File Store for this token! 😅")
            logger.info(f"⚠️ Admin {user_id} tried to use FILESTORE_TOKEN with incorrect usage: {usage}")
            return

        # Store bot with visibility, usage, and standalone status
        cloned_bots.append({
            "token": token,
            "visibility": visibility,
            "usage": usage,
            "owner_id": user_id,
            "standalone": is_standalone
        })
        set_setting("cloned_bots", cloned_bots)

        # Dynamically start the cloned bot (if not standalone)
        if not is_standalone:
            admin_ids = context.bot_data.get("admin_ids", [])
            instance = start_cloned_bot(token, admin_ids)
            if instance:
                bot_instances.append(instance)
                update.message.reply_text(f"✅ Cloned bot @{bot_username} added and started! 🎉\nVisibility: {visibility.upper()} 🔒 | Usage: {usage.upper()} 🛠️")
                logger.info(f"✅ Admin {user_id} added and started cloned bot @{bot_username} with token ending {token[-4:]} and visibility {visibility} and usage {usage}! 🌟")
            else:
                update.message.reply_text(f"⚠️ Cloned bot @{bot_username} added but failed to start! Check the token or logs! 😅")
                logger.info(f"⚠️ Admin {user_id} added cloned bot @{bot_username} but failed to start, token ending {token[-4:]}")
        else:
            update.message.reply_text(f"✅ Cloned bot @{bot_username} added as standalone (running independently)! 🎉\nVisibility: {visibility.upper()} 🔒 | Usage: {usage.upper()} 🛠️")
            logger.info(f"✅ Admin {user_id} added standalone bot @{bot_username} with token ending {token[-4:]} and visibility {visibility} and usage {usage}! 🌟")

        context.user_data["awaiting_clone_token"] = None
        context.user_data["new_bot_visibility"] = None
        context.user_data["new_bot_usage"] = None
    except Exception as e:
        update.message.reply_text("⚠️ Failed to add cloned bot! Check token or logs! 😅")
        log_error(f"🚨 Clone input error for {user_id}: {str(e)}")
