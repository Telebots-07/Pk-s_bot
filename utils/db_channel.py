import json
import logging
from telegram import Bot
from utils.logging_utils import log_error

logger = logging.getLogger(__name__)

def get_setting(key: str, default=None):
    """🔍 Retrieve a setting from the database channel."""
    try:
        with open("config/settings.json", "r") as f:
            settings = json.load(f)
        result = settings.get(key, default)
        logger.info(f"✅ Retrieved setting {key}! 🌟")
        return result
    except Exception as e:
        log_error(f"🚨 Error retrieving setting {key}: {str(e)}")
        return default

def set_setting(key: str, value):
    """📝 Store a setting in the database channel."""
    try:
        try:
            with open("config/settings.json", "r") as f:
                settings = json.load(f)
        except FileNotFoundError:
            settings = {}
        
        settings[key] = value
        with open("config/settings.json", "w") as f:
            json.dump(settings, f, indent=2)
        logger.info(f"✅ Stored setting {key}! 🎉")
    except Exception as e:
        log_error(f"🚨 Error storing setting {key}: {str(e)}")

def store_file_metadata(metadata: dict):
    """🗄️ Store file metadata in the database channel."""
    try:
        with open("config/files.json", "a") as f:
            json.dump(metadata, f)
            f.write("\n")
        logger.info(f"✅ Stored file metadata: {metadata['searchable_id']} 🌟")
    except Exception as e:
        log_error(f"🚨 Error storing file metadata: {str(e)}")

def get_cloned_bots():
    """🤖 Retrieve the list of cloned bots from the database channel."""
    try:
        try:
            with open("config/cloned_bots.json", "r") as f:
                bots = json.load(f)
        except FileNotFoundError:
            bots = []
        logger.info(f"✅ Retrieved {len(bots)} cloned bots! 🌟")
        return bots
    except Exception as e:
        log_error(f"🚨 Error retrieving cloned bots: {str(e)}")
        return []

def store_cloned_bot(bot_data: dict):
    """🔑 Store a new cloned bot in the database channel."""
    try:
        try:
            with open("config/cloned_bots.json", "r") as f:
                bots = json.load(f)
        except FileNotFoundError:
            bots = []
        
        bots.append(bot_data)
        with open("config/cloned_bots.json", "w") as f:
            json.dump(bots, f, indent=2)
        logger.info(f"✅ Stored cloned bot with token ending {bot_data['token'][-4:]}! 🎉")
    except Exception as e:
        log_error(f"🚨 Error storing cloned bot: {str(e)}")
