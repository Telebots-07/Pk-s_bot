import json
from telegram import Bot
from utils.logger import log_error
import os

async def get_db_channel_id(bot: Bot):
    """Get DB channel ID from settings."""
    settings = await get_setting("settings", {})
    return settings.get("db_channel_id")

async def set_setting(key: str, value):
    """Store a setting in the DB channel."""
    bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
    db_channel = await get_db_channel_id(bot)
    if not db_channel:
        await log_error("No DB channel set!")
        return

    settings = await get_setting("settings", {})
    settings[key] = value
    try:
        message = await bot.send_message(
            chat_id=db_channel,
            text=json.dumps({"type": "settings", **settings}),
            disable_notification=True
        )
        await bot.pin_chat_message(db_channel, message.message_id, disable_notification=True)
    except Exception as e:
        await log_error(f"Failed to set setting {key}: {str(e)}")

async def get_setting(key: str, default=None):
    """Retrieve a setting from the DB channel."""
    bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
    db_channel = await get_db_channel_id(bot)
    if not db_channel:
        return default

    try:
        messages = await bot.get_chat_history(chat_id=db_channel, limit=10)
        for message in messages:
            if message.text and '"type": "settings"' in message.text:
                settings = json.loads(message.text)
                return settings.get(key, default)
    except Exception as e:
        await log_error(f"Failed to get setting {key}: {str(e)}")
    return default

async def store_file_metadata(metadata: dict):
    """Store file metadata in the DB channel."""
    bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
    db_channel = await get_db_channel_id(bot)
    if not db_channel:
        await log_error("No DB channel set!")
        return

    try:
        await bot.send_message(
            chat_id=db_channel,
            text=json.dumps({"type": "cloned_files", **metadata}),
            disable_notification=True
        )
    except Exception as e:
        await log_error(f"Failed to store file metadata: {str(e)}")

async def get_cloned_bots():
    """Retrieve cloned bot configs from the DB channel."""
    bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
    db_channel = await get_db_channel_id(bot)
    if not db_channel:
        return []

    try:
        messages = await bot.get_chat_history(chat_id=db_channel, limit=100)
        return [json.loads(msg.text) for msg in messages if msg.text and '"type": "cloned_bot"' in msg.text]
    except Exception as e:
        await log_error(f"Failed to get cloned bots: {str(e)}")
        return []
