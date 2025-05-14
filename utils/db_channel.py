import json
import asyncio
from telegram import Bot
from utils.logger import log_error
import os

db_lock = asyncio.Lock()

async def get_db_channel_id(bot: Bot):
    """Get DB channel ID from settings."""
    async with db_lock:
        try:
            settings = await get_setting("settings", {})
            channel_id = settings.get("db_channel_id")
            if channel_id:
                logger.info("✅ DB channel ID retrieved")
            else:
                logger.info("⚠️ No DB channel ID set")
            return channel_id
        except Exception as e:
            await log_error(f"DB channel ID error: {str(e)}")
            return None

async def set_setting(key: str, value):
    """Store a setting in the DB channel."""
    bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
    async with db_lock:
        for attempt in range(3):
            try:
                db_channel = await get_db_channel_id(bot)
                if not db_channel:
                    await log_error("⚠️ No DB channel set!")
                    return

                settings = await get_setting("settings", {})
                settings[key] = value
                message = await bot.send_message(
                    chat_id=db_channel,
                    text=json.dumps({"type": "settings", **settings}),
                    disable_notification=True
                )
                await bot.pin_chat_message(db_channel, message.message_id, disable_notification=True)
                logger.info(f"✅ Setting {key} stored")
                return
            except Exception as e:
                await log_error(f"Set setting attempt {attempt + 1} error: {str(e)}")
                if attempt == 2:
                    logger.info(f"⚠️ Failed to set setting {key}")
                    return
                await asyncio.sleep(2)

async def get_setting(key: str, default=None):
    """Retrieve a setting from the DB channel."""
    bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
    async with db_lock:
        for attempt in range(3):
            try:
                db_channel = await get_db_channel_id(bot)
                if not db_channel:
                    logger.info("⚠️ No DB channel for get_setting")
                    return default

                messages = await bot.get_chat_history(chat_id=db_channel, limit=10)
                for message in messages:
                    if message.text and '"type": "settings"' in message.text:
                        settings = json.loads(message.text)
                        value = settings.get(key, default)
                        logger.info(f"✅ Retrieved setting {key}")
                        return value
                logger.info(f"⚠️ Setting {key} not found")
                return default
            except Exception as e:
                await log_error(f"Get setting attempt {attempt + 1} error: {str(e)}")
                if attempt == 2:
                    logger.info(f"⚠️ Failed to get setting {key}")
                    return default
                await asyncio.sleep(2)

async def store_file_metadata(metadata: dict):
    """Store file metadata in the DB channel."""
    bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
    async with db_lock:
        for attempt in range(3):
            try:
                db_channel = await get_db_channel_id(bot)
                if not db_channel:
                    await log_error("⚠️ No DB channel set!")
                    return

                await bot.send_message(
                    chat_id=db_channel,
                    text=json.dumps({"type": "cloned_files", **metadata}),
                    disable_notification=True
                )
                logger.info(f"✅ Metadata stored: {metadata.get('searchable_id')}")
                return
            except Exception as e:
                await log_error(f"Store metadata attempt {attempt + 1} error: {str(e)}")
                if attempt == 2:
                    logger.info("⚠️ Failed to store metadata")
                    return
                await asyncio.sleep(2)

async def get_cloned_bots():
    """Retrieve cloned bot configs from the DB channel."""
    bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
    async with db_lock:
        for attempt in range(3):
            try:
                db_channel = await get_db_channel_id(bot)
                if not db_channel:
                    logger.info("⚠️ No DB channel for cloned bots")
                    return []

                messages = await bot.get_chat_history(chat_id=db_channel, limit=100)
                bots = [json.loads(msg.text) for msg in messages if msg.text and '"type": "cloned_bot"' in msg.text]
                logger.info(f"✅ Retrieved {len(bots)} cloned bots")
                return bots
            except Exception as e:
                await log_error(f"Get cloned bots attempt {attempt + 1} error: {str(e)}")
                if attempt == 2:
                    logger.info("⚠️ Failed to get cloned bots")
                    return []
                await asyncio.sleep(2)
