from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.db_channel import store_file_metadata, get_setting
from utils.logger import log_error
from features.link_shortener import shorten_link
from datetime import datetime
import uuid

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle file uploads and apply custom captions/buttons."""
    if str(update.effective_user.id) not in context.bot_data.get("admin_ids", []):
        await update.message.reply_text("⚠️ Admins only!")
        return

    file = update.message.document or (update.message.photo[-1] if update.message.photo else update.message.video or update.message.audio)
    if not file:
        await update.message.reply_text("⚠️ Unsupported file type!")
        return

    file_size = file.file_size / (1024 * 1024)  # Size in MB
    if file_size > 2000:
        await update.message.reply_text("⚠️ File too large! Max 2GB.")
        return

    # Get storage channel
    storage_channels = await get_setting("storage_channels", [])
    if not storage_channels:
        await update.message.reply_text("⚠️ No storage channels set!")
        return

    # Clone file to storage channel
    storage_channel = storage_channels[0]
    file_id = str(uuid.uuid4())
    try:
        message = await context.bot.forward_message(
            chat_id=storage_channel,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )
    except Exception as e:
        await update.message.reply_text("⚠️ Failed to clone file!")
        await log_error(f"File cloning error: {str(e)}")
        return

    # Get custom caption and buttons
    custom_caption = await get_setting("custom_caption", "🎥 {filename} | Uploaded: {date} | Size: {size}MB | By: @bot_paiyan_official")
    custom_buttons = await get_setting("custom_buttons", [
        {"text": "Download ⬇️", "url": "{file_link}"},
        {"text": "Share 🔗", "callback": "share_file_{file_id}"}
    ])

    # Prepare metadata
    filename = getattr(file, "file_name", "Unnamed File")
    date = datetime.now().strftime("%Y-%m-%d")
    file_link = f"https://t.me/@BotPaiyanOfficial?start={file_id}"
    short_link = file_link
    try:
        if not await is_shortener_skipped(update.effective_user.id):
            short_link = await shorten_link(file_link)
    except Exception as e:
        await log_error(f"Shortener error: {str(e)}")

    # Format caption
    try:
        caption = custom_caption.format(
            filename=filename,
            date=date,
            size=round(file_size, 2),
            file_id=file_id,
            user_id=update.effective_user.id,
            file_link=short_link
        )
    except Exception as e:
        caption = f"🎥 {filename} | Uploaded: {date} | Size: {file_size:.2f}MB"
        await log_error(f"Caption formatting error: {str(e)}")

    # Format buttons
    keyboard = []
    for btn in custom_buttons[:10]:
        text = btn["text"]
        try:
            if "url" in btn:
                url = btn["url"].format(file_link=short_link, file_id=file_id)
                if not url.startswith("http"):
                    url = file_link
                    await log_error(f"Invalid URL in button: {btn['url']}")
                keyboard.append([InlineKeyboardButton(text, url=url)])
            elif "callback" in btn:
                callback = btn["callback"].format(file_id=file_id)
                keyboard.append([InlineKeyboardButton(text, callback_data=callback)])
        except Exception as e:
            await log_error(f"Button formatting error: {str(e)}")
            continue

    # Update message with caption and buttons
    try:
        await context.bot.edit_message_caption(
            chat_id=storage_channel,
            message_id=message.message_id,
            caption=caption[:4096],
            reply_markup=InlineKeyboardMarkup(keyboard if keyboard else None)
        )
    except Exception as e:
        await log_error(f"Failed to set caption/buttons: {str(e)}")

    # Store metadata
    await store_file_metadata({
        "searchable_id": file_id,
        "filename": filename,
        "message_id": message.message_id,
        "chat_id": storage_channel,
        "size": file_size,
        "date": date
    })

    await update.message.reply_text(
        "✅ File cloned!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Retrieve 🔍", callback_data=f"retrieve_{file_id}"),
             InlineKeyboardButton("Delete 🗑️", callback_data=f"delete_{file_id}")]
        ])
    )
    await log_error(f"File cloned by {update.effective_user.id}: {filename}")

async def is_shortener_skipped(user_id: int) -> bool:
    """Check if shortener should be skipped."""
    from datetime import datetime, timedelta
    verification = await get_setting(f"verifications_{user_id}")
    if not verification:
        return False
    timestamp = datetime.fromisoformat(verification["timestamp"])
    return datetime.now() < timestamp + timedelta(hours=1)
