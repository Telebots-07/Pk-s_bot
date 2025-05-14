import os
from telegram import Bot

async def log_error(message: str):
    """Log errors to log channel and Render console."""
    try:
        bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
        # Fetch log channel ID directly (avoid importing db_channel)
        log_channel = None
        try:
            # Assuming settings are stored in a pinned message in DB channel
            # This is a simplified approach; adjust based on actual DB channel logic
            settings = {}  # Placeholder: In practice, fetch from DB channel
            log_channel = settings.get("log_channel_id")
        except Exception:
            pass

        if log_channel:
            await bot.send_message(
                chat_id=log_channel,
                text=message,
                disable_notification=True
            )
        print(message)  # Log to Render console
        return True
    except Exception as e:
        print(f"⚠️ Logger error: {str(e)}")
        return False
