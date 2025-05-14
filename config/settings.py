import os
from utils.logger import log_error

async def load_settings():
    """Load and validate env vars."""
    try:
        TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
        ADMIN_IDS = os.getenv("ADMIN_IDS")
        if not TELEGRAM_TOKEN or not ADMIN_IDS:
            await log_error("⚠️ Missing TELEGRAM_TOKEN or ADMIN_IDS")
            raise ValueError("Missing env vars")
        admin_ids = [int(id.strip()) for id in ADMIN_IDS.split(",")]
        logger.info("✅ Environment variables loaded")
        return {"TELEGRAM_TOKEN": TELEGRAM_TOKEN, "ADMIN_IDS": admin_ids}
    except Exception as e:
        await log_error(f"Settings error: {str(e)}")
        raise
