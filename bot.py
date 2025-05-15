import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from handlers.start import start, settings_menu, batch_menu, bot_stats
from handlers.file_handler import handle_file
from handlers.clone_bot import create_clone_bot, view_clone_bots, handle_clone_input, handle_visibility_selection
from handlers.custom_caption import set_custom_caption, set_custom_buttons, handle_caption_input, handle_buttons_input
from handlers.error import error_handler
from handlers.search import search
from handlers.request import handle_request
from handlers.tutorial import tutorial
from handlers.settings import handle_settings, handle_settings_input
from handlers.broadcast import broadcast, handle_broadcast_input, cancel_broadcast
from handlers.batch import batch, handle_batch_input, handle_batch_edit, cancel_batch
from handlers.filestore import store_file, linkgen, batchgen, handle_linkgen_selection, handle_batchgen_selection, handle_filestore_link  # New imports
from utils.logging_utils import log_error
from utils.db_channel import get_cloned_bots
from config.settings import load_settings

# 🌟 Logging setup for Render
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global list to keep track of running bot instances
bot_instances = []

def start_cloned_bot(token, admin_ids):
    """🤖 Start a cloned bot instance dynamically with visibility restrictions."""
    try:
        # Fetch cloned bots to get visibility and standalone status
        cloned_bots = get_cloned_bots()
        bot_info = next((bot for bot in cloned_bots if bot["token"] == token), None)
        if not bot_info:
            raise ValueError("Bot not found in cloned_bots")

        # Skip if the bot is marked as standalone
        if bot_info.get("standalone", False):
            logger.info(f"ℹ️ Skipped starting cloned bot with token ending {token[-4:]} - marked as standalone! 🤖")
            return None

        visibility = bot_info.get("visibility", "public")
        owner_id = bot_info.get("owner_id", None)

        clone_updater = Updater(token, use_context=True)
        clone_dispatcher = clone_updater.dispatcher
        clone_context_data = {"admin_ids": admin_ids, "is_main_bot": False, "visibility": visibility, "owner_id": owner_id}
        clone_dispatcher.bot_data.update(clone_context_data)

        # Log the bot's username for debugging
        bot_username = clone_updater.bot.get_me().username
        logger.info(f"ℹ️ Initializing cloned bot @{bot_username} with token ending {token[-4:]}")

        # Access restriction for private bots
        def restrict_access(handler_func):
            def wrapper(update: Update, context: CallbackContext):
                user_id = str(update.effective_user.id)
                if context.bot_data.get("visibility") == "private" and user_id != context.bot_data.get("owner_id"):
                    update.message.reply_text("🚫 This bot is private! Only the owner can use it! 🔒")
                    logger.info(f"🚫 User {user_id} denied access to private bot with token ending {token[-4:]}")
                    return
                return handler_func(update, context)
            return wrapper

        # Limited handlers for cloned bots (no admin features)
        clone_dispatcher.add_handler(CommandHandler("start", restrict_access(start)))
        clone_dispatcher.add_handler(CommandHandler("search", restrict_access(search)))
        clone_dispatcher.add_handler(MessageHandler(Filters.document | Filters.photo | Filters.video | Filters.audio, restrict_access(store_file)))  # Updated to store_file
        clone_dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, restrict_access(handle_request)))
        clone_dispatcher.add_handler(CommandHandler("linkgen", restrict_access(linkgen)))  # New LinkGen command
        clone_dispatcher.add_handler(CommandHandler("batchgen", restrict_access(batchgen)))  # New BatchGen command
        clone_dispatcher.add_handler(CallbackQueryHandler(handle_linkgen_selection, pattern="^(linkgen_|cancel_linkgen)"))  # New LinkGen callback
        clone_dispatcher.add_handler(CallbackQueryHandler(handle_batchgen_selection, pattern="^(batch_select_|batch_done|cancel_batchgen)"))  # New BatchGen callback
        clone_dispatcher.add_handler(CommandHandler("start", handle_filestore_link, pass_args=True))  # Handle deep links
        clone_dispatcher.add_error_handler(error_handler)
        clone_updater.start_polling()
        logger.info(f"✅ Started cloned bot @{bot_username} with token ending {token[-4:]} and visibility {visibility}! 🤖")
        return clone_updater
    except Exception as e:
        error_msg = f"🚨 Failed to start cloned bot with token ending {token[-4:]}: {str(e)}"
        logger.error(error_msg)
        log_error(error_msg)
        return None

def main():
    """🚀 Initialize and run the bot with cloned bots and custom captions/buttons."""
    global bot_instances

    # 🔑 Load static env vars
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    ADMIN_IDS = os.getenv("ADMIN_IDS")

    if not TELEGRAM_TOKEN or not ADMIN_IDS:
        error_msg = "🚨 Missing TELEGRAM_TOKEN or ADMIN_IDS"
        logger.error(error_msg)
        log_error(error_msg)
        raise ValueError(error_msg)

    try:
        admin_ids = [str(id.strip()) for id in ADMIN_IDS.split(",")]  # Convert to strings
        logger.info(f"✅ Loaded admin IDs: {admin_ids}")
    except ValueError:
        error_msg = "🚨 Invalid ADMIN_IDS format"
        logger.error(error_msg)
        log_error(error_msg)
        raise ValueError(error_msg)

    context_data = {"admin_ids": admin_ids, "is_main_bot": True}

    # 🤖 Initialize main bot
    try:
        updater = Updater(TELEGRAM_TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        dispatcher.bot_data.update(context_data)
        # Log the bot's username for debugging
        bot_username = updater.bot.get_me().username
        logger.info(f"✅ Main bot initialized! 🎉 Bot username: @{bot_username}")
    except Exception as e:
        error_msg = f"🚨 Failed to initialize main bot: {str(e)}"
        logger.error(error_msg)
        log_error(error_msg)
        raise

    # 📡 Add handlers for main bot (full admin features)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("search", search))
    dispatcher.add_handler(MessageHandler(Filters.document | Filters.photo | Filters.video | Filters.audio, handle_file))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_caption_input))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_buttons_input))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_clone_input))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_request))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_broadcast_input))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_batch_input))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_settings_input))
    dispatcher.add_handler(CallbackQueryHandler(create_clone_bot, pattern="^create_clone_bot$"))
    dispatcher.add_handler(CallbackQueryHandler(view_clone_bots, pattern="^view_clone_bots$"))
    dispatcher.add_handler(CallbackQueryHandler(handle_visibility_selection, pattern="^(visibility_private|visibility_public|cancel_clone)$"))
    dispatcher.add_handler(CallbackQueryHandler(set_custom_caption, pattern="^set_custom_caption$"))
    dispatcher.add_handler(CallbackQueryHandler(set_custom_buttons, pattern="^set_custom_buttons$"))
    dispatcher.add_handler(CallbackQueryHandler(tutorial, pattern="^tutorial$"))
    dispatcher.add_handler(CallbackQueryHandler(settings_menu, pattern="^settings$"))
    dispatcher.add_handler(CallbackQueryHandler(batch_menu, pattern="^batch_menu$"))
    dispatcher.add_handler(CallbackQueryHandler(bot_stats, pattern="^bot_stats$"))
    dispatcher.add_handler(CallbackQueryHandler(handle_settings, pattern="^(add_channel|remove_channel|set_force_sub|set_group_link|set_db_channel|set_log_channel|shortener|welcome_message|auto_delete|banner|set_webhook|anti_ban|enable_redis)$"))
    dispatcher.add_handler(CallbackQueryHandler(broadcast, pattern="^broadcast$"))
    dispatcher.add_handler(CallbackQueryHandler(cancel_broadcast, pattern="^cancel_broadcast$"))
    dispatcher.add_handler(CallbackQueryHandler(batch, pattern="^(generate_batch|edit_batch)$"))
    dispatcher.add_handler(CallbackQueryHandler(handle_batch_edit, pattern="^edit_batch_"))
    dispatcher.add_handler(CallbackQueryHandler(cancel_batch, pattern="^cancel_batch$"))
    # New File Store handlers for main bot
    dispatcher.add_handler(MessageHandler(Filters.document | Filters.photo | Filters.video | Filters.audio, store_file))  # Store files
    dispatcher.add_handler(CommandHandler("linkgen", linkgen))  # LinkGen command
    dispatcher.add_handler(CommandHandler("batchgen", batchgen))  # BatchGen command
    dispatcher.add_handler(CallbackQueryHandler(handle_linkgen_selection, pattern="^(linkgen_|cancel_linkgen)"))  # LinkGen callback
    dispatcher.add_handler(CallbackQueryHandler(handle_batchgen_selection, pattern="^(batch_select_|batch_done|cancel_batchgen)"))  # BatchGen callback
    dispatcher.add_handler(CommandHandler("start", handle_filestore_link, pass_args=True))  # Handle deep links
    dispatcher.add_error_handler(error_handler)

    # 🗄️ Load cloned bots from DB channel
    try:
        cloned_bots = get_cloned_bots()
        logger.info(f"✅ Loaded {len(cloned_bots)} cloned bots! 🌟")
        # Log details of each bot for debugging
        for bot in cloned_bots:
            logger.info(f"ℹ️ Cloned bot: token ending {bot['token'][-4:]} | Visibility: {bot['visibility']} | Standalone: {bot.get('standalone', False)}")
    except Exception as e:
        error_msg = f"🚨 Failed to load cloned bots: {str(e)}"
        logger.error(error_msg)
        log_error(error_msg)
        cloned_bots = []

    # Start cloned bots initially
    bot_instances = []
    for bot in cloned_bots:
        instance = start_cloned_bot(bot["token"], admin_ids)
        if instance:
            bot_instances.append(instance)

    # 🌍 Start main bot
    try:
        updater.start_polling()
        logger.info(f"✅ Main bot started! 🚀 Bot username: @{bot_username}")
    except Exception as e:
        error_msg = f"🚨 Failed to start main bot: {str(e)}"
        logger.error(error_msg)
        log_error(error_msg)
        raise

    # 💤 Keep the main thread running
    updater.idle()

if __name__ == "__main__":
    main()
