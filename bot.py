import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from handlers.start import start, settings_menu
from handlers.file_handler import handle_file
from handlers.clone_bot import create_clone_bot, view_clone_bots, handle_clone_input
from handlers.custom_caption import set_custom_caption, set_custom_buttons, handle_caption_input, handle_buttons_input
from handlers.error import error_handler
from handlers.search import search
from handlers.request import handle_request
from handlers.tutorial import tutorial
from handlers.settings import handle_settings
from handlers.broadcast import broadcast, handle_broadcast_input, cancel_broadcast
from handlers.batch import batch
from utils.logging_utils import log_error
from utils.db_channel import get_cloned_bots
from config.settings import load_settings

# 🌟 Logging setup for Render
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """🚀 Initialize and run the bot with cloned bots and custom captions/buttons."""
    # 🔑 Load static env vars
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    ADMIN_IDS = os.getenv("ADMIN_IDS")

    if not TELEGRAM_TOKEN or not ADMIN_IDS:
        error_msg = "🚨 Missing TELEGRAM_TOKEN or ADMIN_IDS"
        logger.error(error_msg)
        log_error(error_msg)
        raise ValueError(error_msg)

    try:
        admin_ids = [int(id.strip()) for id in ADMIN_IDS.split(",")]
    except ValueError:
        error_msg = "🚨 Invalid ADMIN_IDS format"
        logger.error(error_msg)
        log_error(error_msg)
        raise ValueError(error_msg)

    context_data = {"admin_ids": admin_ids}

    # 🤖 Initialize main bot
    try:
        updater = Updater(TELEGRAM_TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        dispatcher.bot_data.update(context_data)
        logger.info("✅ Main bot initialized! 🎉")
    except Exception as e:
        error_msg = f"🚨 Failed to initialize main bot: {str(e)}"
        logger.error(error_msg)
        log_error(error_msg)
        raise

    # 📡 Add handlers for main bot
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("search", search))
    dispatcher.add_handler(MessageHandler(Filters.document | Filters.photo | Filters.video | Filters.audio, handle_file))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_caption_input))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_buttons_input))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_clone_input))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_request))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_broadcast_input))
    dispatcher.add_handler(CallbackQueryHandler(create_clone_bot, pattern="^create_clone_bot$"))
    dispatcher.add_handler(CallbackQueryHandler(view_clone_bots, pattern="^view_clone_bots$"))
    dispatcher.add_handler(CallbackQueryHandler(set_custom_caption, pattern="^set_custom_caption$"))
    dispatcher.add_handler(CallbackQueryHandler(set_custom_buttons, pattern="^set_custom_buttons$"))
    dispatcher.add_handler(CallbackQueryHandler(tutorial, pattern="^tutorial$"))
    dispatcher.add_handler(CallbackQueryHandler(settings_menu, pattern="^settings$"))
    dispatcher.add_handler(CallbackQueryHandler(handle_settings, pattern="^(add_channel|remove_channel|set_force_sub|set_group_link|set_db_channel|set_log_channel|shortener|welcome_message|auto_delete|banner|set_webhook|anti_ban|enable_redis)$"))
    dispatcher.add_handler(CallbackQueryHandler(broadcast, pattern="^broadcast$"))
    dispatcher.add_handler(CallbackQueryHandler(cancel_broadcast, pattern="^cancel_broadcast$"))
    dispatcher.add_handler(CallbackQueryHandler(batch, pattern="^(generate_batch|edit_batch)$"))
    dispatcher.add_error_handler(error_handler)

    # 🗄️ Load cloned bots from DB channel
    try:
        cloned_bots = get_cloned_bots()
        logger.info(f"✅ Loaded {len(cloned_bots)} cloned bots! 🌟")
    except Exception as e:
        error_msg = f"🚨 Failed to load cloned bots: {str(e)}"
        logger.error(error_msg)
        log_error(error_msg)
        cloned_bots = []

    bot_instances = []
    for bot in cloned_bots:
        try:
            token = bot["token"]
            clone_updater = Updater(token, use_context=True)
            clone_dispatcher = clone_updater.dispatcher
            clone_dispatcher.bot_data.update(context_data)
            clone_dispatcher.add_handler(CommandHandler("start", start))
            clone_dispatcher.add_handler(CommandHandler("search", search))
            clone_dispatcher.add_handler(MessageHandler(Filters.document | Filters.photo | Filters.video | Filters.audio, handle_file))
            clone_dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_caption_input))
            clone_dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_buttons_input))
            clone_dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_request))
            clone_dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_broadcast_input))
            clone_dispatcher.add_handler(CallbackQueryHandler(set_custom_caption, pattern="^set_custom_caption$"))
            clone_dispatcher.add_handler(CallbackQueryHandler(set_custom_buttons, pattern="^set_custom_buttons$"))
            clone_dispatcher.add_handler(CallbackQueryHandler(tutorial, pattern="^tutorial$"))
            clone_dispatcher.add_handler(CallbackQueryHandler(settings_menu, pattern="^settings$"))
            clone_dispatcher.add_handler(CallbackQueryHandler(handle_settings, pattern="^(add_channel|remove_channel|set_force_sub|set_group_link|set_db_channel|set_log_channel|shortener|welcome_message|auto_delete|banner|set_webhook|anti_ban|enable_redis)$"))
            clone_dispatcher.add_handler(CallbackQueryHandler(broadcast, pattern="^broadcast$"))
            clone_dispatcher.add_handler(CallbackQueryHandler(cancel_broadcast, pattern="^cancel_broadcast$"))
            clone_dispatcher.add_error_handler(error_handler)
            bot_instances.append(clone_updater)
            logger.info(f"✅ Started cloned bot with token ending {token[-4:]}! 🤖")
        except Exception as e:
            error_msg = f"🚨 Failed to start cloned bot: {str(e)}"
            logger.error(error_msg)
            log_error(error_msg)

    # 🌍 Start main bot
    try:
        updater.start_polling()
        logger.info("✅ Main bot started! 🚀")
    except Exception as e:
        error_msg = f"Failed to start main bot: {str(e)}"
        logger.error(error_msg)
        log_error(error_msg)
        raise

    # 🔄 Start cloned bots
    for clone_updater in bot_instances:
        try:
            clone_updater.start_polling()
            logger.info("✅ Cloned bot instance started! 🌟")
        except Exception as e:
            error_msg = f"🚨 Failed to start cloned bot instance: {str(e)}"
            logger.error(error_msg)
            log_error(error_msg)

    # 💤 Keep the main thread running
    updater.idle()

if __name__ == "__main__":
    main()
