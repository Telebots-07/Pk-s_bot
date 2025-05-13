from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import log_error

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /broadcast command for admins."""
    user_id = update.effective_user.id
    if user_id not in context.bot_data.get("ADMIN_IDS", []):
        await update.message.reply_text("🚫 Admins only.")
        return

    args = context.args
    if not args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return

    message = " ".join(args)
    try:
        db = context.bot_data.get("firestore_db")
        users = db.collection("users").get()
        for user in users:
            user_id = user.to_dict().get("user_id")
            await context.bot.send_message(chat_id=user_id, text=message)
        await update.message.reply_text("✅ Broadcast sent!")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Broadcast error: {str(e)}")
        log_error(f"Broadcast error: {str(e)}")
