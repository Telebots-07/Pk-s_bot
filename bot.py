import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from handlers.start import start, settings_menu
from handlers.file_handler import handle_file
from handlers.clone_bot import create_clone_bot, view_clone_bots
from handlers.custom_caption import set_custom_caption, set_custom_buttons, handle_caption_input, handle_buttons_input
from handlers.error import error_handler
from utils.logger import log_error
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
        raise ValueError(error_msg)

    admin_ids = [int(id.strip()) for id in ADMIN_IDS.split(",")]
    context_data = {"admin_ids": admin_ids}

    # Initialize main bot
    main_app = Application.builder().token(TELEGRAM_TOKEN).build()
    main_app.bot_data.update(context_data)

    # Add handlers for main bot
    main_app.add_handler(CommandHandler("start", start))
    main_app.add_handler(MessageHandler(filters.Document | filters.Photo | filters.Video | filters.Audio, handle_file))
    main_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_caption_input))
    main_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons_input))
    main_app.add_handler(CallbackQueryHandler(create_clone_bot, pattern="^create_clone_bot$"))
    main_app.add_handler(CallbackQueryHandler(view_clone_bots, pattern="^view_clone_bots$"))
    main_app.add_handler(CallbackQueryHandler(set_custom_caption, pattern="^set_custom_caption$"))
    main_app.add_handler(CallbackQueryHandler(set_custom_buttons, pattern="^set_custom_buttons$"))
    main_app.add_handler(CallbackQueryHandler(settings_menu, pattern="^settings$"))
    main_app.add_error_handler(error_handler)

    # Load cloned bots from DB channel
    cloned_bots = await get_cloned_bots()
    bot_instances = []

    for bot in cloned_bots:
        try:
            token = bot["token"]
            app = Application.builder().token(token).build()
            app.bot_data.update(context_data)
            app.add_handler(CommandHandler("start", start))
            app.add_handler(MessageHandler(filters.Document | filters.Photo | filters.Video | filters.Audio, handle_file))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_caption_input))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons_input))
            app.add_handler(CallbackQueryHandler(set_custom_caption, pattern="^set_custom_caption$"))
            app.add_handler(CallbackQueryHandler(set_custom_buttons, pattern="^set_custom_buttons$"))
            app.add_handler(CallbackQueryHandler(settings_menu, pattern="^settings$"))
            app.add_error_handler(error_handler)
            bot_instances.append(app)
            logger.info(f"Started cloned bot with token ending {token[-4:]}")
        except Exception as e:
            await log_error(f"Failed to start cloned bot: {str(e)}")

    # Start all bot instances
    await main_app.initialize()
    await main_app.start()
    for app in bot_instances:
        await app.initialize()
        await app.start()

    # Set webhook
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME', 'cloner-bot.onrender.com')}/webhook"
    await main_app.updater.start_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 8443)),
        url_path="/webhook",
        webhook_url=webhook_url
    )
    logger.info(f"Bot started with webhook: {webhook_url}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
