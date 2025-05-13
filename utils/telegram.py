from telegram.ext import ContextTypes
from utils.logger import log_error

async def send_message(context: ContextTypes.DEFAULT_TYPE, chat_id: str, text: str):
    """Helper to send messages."""
    try:
        await context.bot.send_message(chat_id=chat_id, text=text)
    except Exception as e:
        log_error(f"Send message error: {str(e)}")
