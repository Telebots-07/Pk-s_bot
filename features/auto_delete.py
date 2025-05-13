from telegram.ext import ContextTypes
from utils.logger import log_error

async def schedule_auto_delete(context: ContextTypes.DEFAULT_TYPE, message_id: int, chat_id: str, hours: int):
    """Schedule message/file deletion."""
    try:
        job = context.job_queue.run_once(
            delete_message,
            hours * 3600,
            data={"message_id": message_id, "chat_id": chat_id}
        )
        return job
    except Exception as e:
        log_error(f"Auto-delete schedule error: {str(e)}")
        return None

async def delete_message(context: ContextTypes.DEFAULT_TYPE):
    """Delete scheduled message."""
    job = context.job
    try:
        await context.bot.delete_message(
            chat_id=job.data["chat_id"],
            message_id=job.data["message_id"]
        )
    except Exception as e:
        log_error(f"Auto-delete error: {str(e)}")
