import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from firebase_admin import credentials, initialize_app
from handlers.start import start, help_command, clone_info, about
from handlers.file_handler import handle_file
from handlers.tutorial import tutorial, handle_tutorial_callback
from handlers.settings import settings, shortener, add_channel, set_welcome, autodelete, banner
from handlers.search import search, handle_search_callback
from handlers.request import handle_request
from handlers.broadcast import broadcast
from handlers.batch import genbatch, editbatch
from handlers.error import error_handler
from utils.firestore import initialize_firestore
from utils.redis_cache import initialize_redis

# Logging setup for Render
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Initialize and run the Cloner Bot on Render."""
    # Initialize Firestore (optional: replace with PostgreSQL)
    cred = credentials.Certificate({
        "type": "service_account",
        # Replace with your Firebase service account key JSON (store in Render env vars)
    })
    initialize_app(cred)
    db = initialize_firestore()

    # Initialize Redis (optional, configure in Render)
    redis_client = initialize_redis()

    # Initialize bot with webhook for Render
    application = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()

    # Store shared data
    application.bot_data["firestore_db"] = db
    application.bot_data["redis_client"] = redis_client
    application.bot_data["ADMIN_IDS"] = [int(id) for id in os.getenv("ADMIN_IDS").split(",")]

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
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("genbatch", genbatch))
    application.add_handler(CommandHandler("editbatch", editbatch))
    application.add_handler(MessageHandler(filters.Document | filters.Photo | filters.Video | filters.Audio, handle_file))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_request))
    application.add_handler(MessageHandler(filters.COMMAND & ~filters.Regex("^(start|help|clone_info|about|tutorial|settings|shortener|add_channel|set_welcome|autodelete|banner|search|broadcast|genbatch|editbatch)$"), handle_request))
    application.add_handler(CallbackQueryHandler(handle_tutorial_callback, pattern="^tutorial_"))
    application.add_handler(CallbackQueryHandler(handle_search_callback, pattern="^(retrieve|delete|suggest)_"))

    # Error handler
    application.add_error_handler(error_handler)

    # Set webhook for Render
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    await application.bot.set_webhook(url=webhook_url)

    # Start bot with webhook
    await application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 8443)),
        url_path="/webhook",
        webhook_url=webhook_url
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
