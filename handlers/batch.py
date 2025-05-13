from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.logger import log_error
from features.link_shortener import shorten_url

async def genbatch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /genbatch command for bulk cloning."""
    try:
        user_id = update.effective_user.id
        if user_id not in context.bot_data.get("ADMIN_IDS", []):
            await update.message.reply_text("🚫 Admins only.")
            return

        args = context.args
        if not args:
            await update.message.reply_text("Usage: /genbatch <file_ids>")
            return

        file_ids = args
        db = context.bot_data.get("firestore_db")
        if not db:
            await update.message.reply_text("⚠️ Database unavailable.")
            log_error("Firestore DB not initialized")
            return

        batch_links = []
        for file_id in file_ids:
            doc = db.collection("cloned_files").document(file_id).get()
            if doc.exists:
                retrieve_url = f"https://t.me/{context.bot.username}?start=retrieve_{file_id}"
                shortened_url = await shorten_url(context, retrieve_url, shortener_name="bitly")
                batch_links.append(shortened_url or retrieve_url)

        await update.message.reply_text(
            f"✅ Batch generated:\n" + "\n".join(batch_links),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Confirm Batch", callback_data="batch_confirm")]
            ])
        )
    except Exception as e:
        await update.message.reply_text("⚠️ Error generating batch. Try again.")
        log_error(f"Batch generation error: {str(e)}")

async def editbatch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /editbatch command for bulk metadata editing."""
    try:
        user_id = update.effective_user.id
        if user_id not in context.bot_data.get("ADMIN_IDS", []):
            await update.message.reply_text("🚫 Admins only.")
            return

        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Usage: /editbatch <file_ids> <new_caption>")
            return

        file_ids = args[:-1]
        new_caption = args[-1]
        db = context.bot_data.get("firestore_db")
        if not db:
            await update.message.reply_text("⚠️ Database unavailable.")
            log_error("Firestore DB not initialized")
            return

        for file_id in file_ids:
            db.collection("cloned_files").document(file_id).update({"caption": new_caption})
        await update.message.reply_text(
            f"✅ Batch edited: {len(file_ids)} files",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Apply Changes", callback_data="batch_apply")]
            ])
        )
    except Exception as e:
        await update.message.reply_text("⚠️ Error editing batch. Try again.")
        log_error(f"Batch edit error: {str(e)}")
