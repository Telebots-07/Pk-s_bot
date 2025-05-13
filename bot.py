import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from firebase_admin import credentials, initialize_app
from handlers.start import start, help_command, clone_info, about
from handlers.file_handler import handle_file
from handlers.tutorial import tutorial, handle_tutorial_callback
from handlers.settings import settings, shortener, add_channel, set_welcome, autodelete, banner, set_group_link
from handlers.search import search, handle_search_callback
from handlers.request import handle_request, handle_request_callback
from handlers.broadcast import broadcast
from handlers.batch import genbatch, editbatch
from handlers.error import error_handler
from utils.firestore import initialize_firestore
from utils.redis_cache import initialize_redis
from config.settings import load_settings

# Logging setup for Render
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Initialize and run the Cloner Bot on Render."""
    # Validate environment variables
    required_env_vars = [
        "TELEGRAM_TOKEN", "ADMIN_IDS", "FIREBASE_CREDENTIALS",
        "PRIVATE_CHANNEL_ID", "REQUEST_GROUP_LINK"
    ]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        error_msg = f"Missing environment variables: {', '.join(missing_vars)}. Set them in Render dashboard."
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Initialize Firestore
    try:
        cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS"))
        initialize_app(cred)
        db = initialize_firestore()
    except Exception as e:
        logger.error(f"Firestore init error: {str(e)}")
        raise RuntimeError(f"Failed to initialize Firestore: {str(e)}")

    # Initialize Redis (optional)
    redis_client = initialize_redis()

    # Initialize bot with webhook
    try:
        application = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    except Exception as e:
        logger.error(f"Bot init error: {str(e)}")
        raise RuntimeError(f"Failed to initialize bot: {str(e)}")

    # Store shared data
    application.bot_data["firestore_db"] = db
    application.bot_data["redis_client"] = redis_client
    try:
        application.bot_data["ADMIN_IDS"] = [int(id) for id in os.getenv("ADMIN_IDS").split(",")]
    except ValueError as e:
        logger.error(f"Invalid ADMIN_IDS format: {str(e)}")
        raise ValueError("ADMIN_IDS must be comma-separated integers.")

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clone_info", clone_info))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("tutorial", tutorial))
    application.add_handler(CommandHandler("settings", settings))
    application.add_handler(CommandHandler("shortener", shortener))
    application.add_handler(CommandHandler("add_channel", add_channel))
    application.add_handler(CommandHandler("set_welcome", set_welcome))
    application.add_handler(CommandHandler("autodelete", autodelete))
    application.add_handler(CommandHandler("banner", banner))
    application.add_handler(CommandHandler("set_group_link", set_group_link))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("genbatch", genbatch))
    application.add_handler(CommandHandler("editbatch", editbatch))
    application.add_handler(MessageHandler(filters.Document | filters.Photo | filters.Video | filters.Audio, handle_file))
    # Handle all text in groups as requests
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_request))
    # Ignore non-command text in private DMs
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & ~filters.COMMAND, lambda u, c: None))
    # Handle unrecognized commands in groups as requests
    application.add_handler(MessageHandler(
        filters.COMMAND & filters.ChatType.GROUPS & ~filters.Regex(
            "^(start|help|clone_info|about|tutorial|settings|shortener|add_channel|set_welcome|autodelete|banner|set_group_link|search|broadcast|genbatch|editbatch)$"
        ), handle_request))
    application.add_handler(CallbackQueryHandler(handle_tutorial_callback, pattern="^tutorial_"))
    application.add_handler(CallbackQueryHandler(handle_search_callback, pattern="^suggest_"))
    application.add_handler(CallbackQueryHandler(handle_request_callback, pattern="^(approve|deny)_"))

    # Error handler
    application.add_error_handler(error_handler)

    # Set webhook for Render
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    try:
        await application.bot.set_webhook(url=webhook_url)
    except Exception as e:
        logger.error(f"Webhook setup error: {str(e)}")
        raise RuntimeError(f"Failed to set webhook: {str(e)}")

    # Start bot with webhook
    try:
        await application.run_webhook(
            listen="0.0.0.0",
            port=int(os.getenv("PORT", 8443)),
            url_path="/webhook",
            webhook_url=webhook_url
        )
    except Exception as e:
        logger.error(f"Webhook run error: {str(e)}")
        raise RuntimeError(f"Failed to run webhook: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
