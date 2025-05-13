from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from uuid import uuid4
from utils.logger import log_error
from features.cover_image import add_cover_image

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming files for cloning."""
    user_id = update.effective_user.id
    if user_id not in context.bot_data.get("ADMIN_IDS", []):
        await update.message.reply_text("🚫 Admins only.")
        return

    file = update.message.document or update.message.photo[-1] if update.message.photo else update.message.video or update.message.audio
    if not file:
        await update.message.reply_text("⚠️ Unsupported file type.")
        return

    # Check file size (2GB max)
    file_size = getattr(file, "file_size", 0)
    if file_size > 2 * 1024 * 1024 * 1024:
        await update.message.reply_text("⚠️ File too large. Max 2GB.")
        return

    try:
        # Download file
        file_obj = await file.get_file()
        file_path = f"/app/temp/{uuid4()}.{file.mime_type.split('/')[-1]}"
        await file_obj.download_to_drive(file_path)

        # Add cover image (if configured)
        cover_path = await add_cover_image(file_path, context)
        final_path = cover_path or file_path

        # Forward to private channel
        db = context.bot_data.get("firestore_db")
        caption = update.message.caption or "No caption"
        searchable_id = str(uuid4())
        if update.message.document:
            sent_message = await context.bot.send_document(
                chat_id=os.getenv("PRIVATE_CHANNEL_ID"),
                document=open(final_path, "rb"),
                caption=caption
            )
        elif update.message.photo:
            sent_message = await context.bot.send_photo(
                chat_id=os.getenv("PRIVATE_CHANNEL_ID"),
                photo=open(final_path, "rb"),
                caption=caption
            )
        elif update.message.video:
            sent_message = await context.bot.send_video(
                chat_id=os.getenv("PRIVATE_CHANNEL_ID"),
                video=open(final_path, "rb"),
                caption=caption
            )
        elif update.message.audio:
            sent_message = await context.bot.send_audio(
                chat_id=os.getenv("PRIVATE_CHANNEL_ID"),
                audio=open(final_path, "rb"),
                caption=caption
            )

        # Store metadata
        db.collection("cloned_files").document(searchable_id).set({
            "searchable_id": searchable_id,
            "caption": caption,
            "message_id": sent_message.message_id,
            "file_type": file.mime_type,
            "timestamp": update.message.date.isoformat()
        })

        await update.message.reply_text(
            f"✅ File cloned: {caption}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Retrieve", callback_data=f"retrieve_{searchable_id}")],
                [InlineKeyboardButton("Delete", callback_data=f"delete_{searchable_id}")]
            ])
        )

    except Exception as e:
        await update.message.reply_text(f"⚠️ File cloning error: {str(e)}")
        log_error(f"File cloning error: {str(e)}, user_id: {user_id}")
