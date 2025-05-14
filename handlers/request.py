from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.db_channel import store_file_metadata, get_setting
from utils.logger import log_error
import uuid

async def handle_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle group text as requests with hidden link previews."""
    user_id = update.effective_user.id
    group_id = await get_setting("group_id")
    
    if str(update.message.chat_id) != str(group_id):
        return

    text = update.message.text
    try:
        request_id = str(uuid.uuid4())
        await store_file_metadata({
            "type": "request",
            "request_id": request_id,
            "user_id": user_id,
            "text": text,
            "date": datetime.now().strftime("%Y-%m-%d")
        })
        await update.message.reply_text(
            f"✅ Request submitted: {text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("View Status 🔍", callback_data=f"status_{request_id}")]
            ]),
            disable_web_page_preview=True
        )
        logger.info(f"✅ Request submitted by {user_id}: {request_id}")
    except Exception as e:
        await update.message.reply_text("⚠️ Failed to submit request!")
        await log_error(f"Request error for {user_id}: {str(e)}")
