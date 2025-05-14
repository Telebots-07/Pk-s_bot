import os
import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from handlers.start import start, settings_menu
from handlers.file_handler import handle_file
from handlers.clone_bot import create_clone_bot, view_clone_bots, handle_clone_input
from handlers.custom_caption import set_custom_caption, set_custom_buttons, handle_caption_input, handle_buttons_input
from handlers.error import error_handler
from handlers.search import search
from handlers.request import handle_request
from handlers.tutorial import tutorial
from handlers.settings import handle_settings
from handlers.broadcast import broadcast
from handlers.batch import batch
from utils.logging_utils import log_error
from utils.db_channel import get_cloned_bots
from config.settings import load_settings

# Logging setup for Render
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Initialize and run the bot with support for cloned bots and custom captions/buttons."""
    # Load static env vars
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    ADMIN_IDS = os.getenv("ADMIN_IDS")

    if not TELEGRAM_TOKEN or not ADMIN_IDS:
        error_msg = "⚠️ Missing TELEGRAM_TOKEN or ADMIN_IDS"
        logger.error(error_msg)
        await log_error(error_msg)
        raise ValueError(error_msg)

    try:
        admin_ids = [int(id.strip()) for id in ADMIN_IDS.split(",")]
    except ValueError:
        error_msg = "⚠️ Invalid ADMIN_IDS format"
        logger.error(error_msg)
        await log_error(error_msg)
        raise ValueError(error_msg)

    context_data = {"admin_ids": admin_ids}

    # Initialize main bot
    try:
        main_app = Application.builder().token(TELEGRAM_TOKEN).build()
        main_app.bot_data.update(context_data)
        logger.info("✅ Main bot initialized")
    except Exception as e:
        error_msg = f"⚠️ Failed to initialize main bot: {str(e)}"
        logger.error(error_msg)
        await log_error(error_msg)
        raise

    # Add handlers for main bot
    main_app.add_handler(CommandHandler("start", start))
    main_app.add_handler(CommandHandler("search", search))
    main_app.add_handler(MessageHandler(filters.Document | filters.Photo | filters.Video | filters.Audio, handle_file))
    main_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_caption_input))
    main_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons_input))
    main_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_clone_input))
    main_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_request))
    main_app.add_handler(CallbackQueryHandler(create_clone_bot, pattern="^create_clone_bot$"))
    main_app.add_handler(CallbackQueryHandler(view_clone_bots, pattern="^view_clone_bots$"))
    main_app.add_handler(CallbackQueryHandler(set_custom_caption, pattern="^set_custom_caption$"))
    main_app.add_handler(CallbackQueryHandler(set_custom_buttons, pattern="^set_custom_buttons$"))
    main_app.add_handler(CallbackQueryHandler(tutorial, pattern="^tutorial$"))
    main_app.add_handler(CallbackQueryHandler(settings_menu, pattern="^settings$"))
    main_app.add_handler(CallbackQueryHandler(handle_settings, pattern="^(add_channel|remove_channel|set_force_sub|set_group_link|set_db_channel|set_log_channel|shortener|welcome_message|auto_delete|banner|set_webhook|anti_ban|enable_redis)$"))
    main_app.add_handler(CallbackQueryHandler(broadcast, pattern="^broadcast$"))
    main_app.add_handler(CallbackQueryHandler(batch, pattern="^(generate_batch|edit_batch)$"))
    main_app.add_error_handler(error_handler)

    # Load cloned bots from DB channel
    try:
        cloned_bots = await get_cloned_bots()
        logger.info(f"✅ Loaded {len(cloned_bots)} cloned bots")
    except Exception as e:
        error_msg = f"⚠️ Failed to load cloned bots: {str(e)}"
        logger.error(error_msg)
        await log_error(error_msg)
        cloned_bots = []

    bot_instances = []
    for bot in cloned_bots:
        try:
            token = bot["token"]
            app = Application.builder().token(token).build()
            app.bot_data.update(context_data)
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("search", search))
            app.add_handler(MessageHandler(filters.Document | filters.Photo | filters.Video | filters.Audio, handle_file))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_caption_input))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons_input))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_request))
            app.add_handler(CallbackQueryHandler(set_custom_caption, pattern="^set_custom_caption$"))
            app.add_handler(CallbackQueryHandler(set_custom_buttons, pattern="^set_custom_buttons$"))
            app.add_handler(CallbackQueryHandler(tutorial, pattern="^tutorial$"))
            app.add_handler(CallbackQueryHandler(settings_menu, pattern="^settings$"))
            app.add_handler(CallbackQueryHandler(handle_settings, pattern="^(add_channel|remove_channel|set_force_sub|set_group_link|set_db_channel|set_log_channel|shortener|welcome_message|auto_delete|banner|set_webhook|anti_ban|enable_redis)$"))
            app.add_handler(CallbackQueryHandler(broadcast, pattern="^broadcast$"))
            app.add_handler(CallbackQueryHandler(batch, pattern="^(generate_batch|edit_batch)$"))
            app.add_error_handler(error_handler)
            bot_instances.append(app)
            logger.info(f"✅ Started cloned bot with token ending {token[-4:]}")
        except Exception as e:
            error_msg = f"⚠️ Failed to start cloned bot: {str(e)}"
            logger.error(error_msg)
            await log_error(error_msg)

    # Start all bot instances
    try:
        await main_app.initialize()
        await main_app.start()
        logger.info("✅ Main bot started")
    except Exception as e:
        error_msg = f"⚠️ Failed to start main bot: {str(e)}"
        logger.error(error_msg)
        await log_error(error_msg)
        raise

    for app in bot_instances:
        try:
            await app.initialize()
            await app.start()
            logger.info("✅ Cloned bot instance started")
        except Exception as e:
            error_msg = f"⚠️ Failed to start cloned bot instance: {str(e)}"
            logger.error(error_msg)
            await log_error(error_msg)

    # Set webhook with retries
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME', 'cloner-bot.onrender.com')}/webhook"
    for attempt in range(3):
        try:
            await main_app.updater.start_webhook(
                listen="0.0.0.0",
                port=int(os.getenv("PORT", 8443)),
                url_path="/webhook",
                webhook_url=webhook_url
            )
            logger.info(f"✅ Webhook set: {webhook_url}")
            break
        except Exception as e:
            error_msg = f"⚠️ Webhook attempt {attempt + 1} failed: {str(e)}"
            logger.error(error_msg)
            await log_error(error_msg)
            if attempt == 2:
                raise
            await asyncio.sleep(5)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
