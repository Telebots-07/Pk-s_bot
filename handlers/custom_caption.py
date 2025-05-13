from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.db_channel import set_setting, get_setting
from utils.logger import log_error

async def set_custom_caption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle custom caption setup."""
    query = update.callback_query
    await query.answer()

    if str(update.effective_user.id) not in context.bot_data.get("admin_ids", []):
        await query.message.reply_text("⚠️ Admins only!")
        return

    await query.message.reply_text(
        "✍️ Enter the custom caption template (e.g., '🎥 {filename} | {date} | {size}MB').\n"
        "Placeholders: {filename}, {date}, {size}, {file_id}, {user_id}, {file_link}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Cancel ❌", callback_data="cancel_caption")]
        ])
    )
    context.user_data["setting_caption"] = True

async def set_custom_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle custom buttons setup."""
    query = update.callback_query
    await query.answer()

    if str(update.effective_user.id) not in context.bot_data.get("admin_ids", []):
        await query.message.reply_text("⚠️ Admins only!")
        return

    await query.message.reply_text(
        "🔘 Enter custom buttons as JSON (e.g., [{'text': 'Download ⬇️', 'url': '{file_link}'}, {'text': 'Share 🔗', 'callback': 'share_file_{file_id}'}]).\n"
        "Max 3 buttons per row, 10 total. Placeholders: {file_link}, {file_id}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Cancel ❌", callback_data="cancel_buttons")]
        ])
    )
    context.user_data["setting_buttons"] = True

async def handle_caption_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process custom caption input."""
    if not context.user_data.get("setting_caption"):
        return

    text = update.message.text
    if len(text) > 4096:
        await update.message.reply_text("⚠️ Caption too long! Max 4096 characters.")
        return

    await set_setting("custom_caption", text)
    await update.message.reply_text("✅ Custom caption set!", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("Back to Settings ⬅️", callback_data="settings")]
    ]))
    context.user_data["setting_caption"] = False
    await log_error(f"Custom caption set by {update.effective_user.id}")

async def handle_buttons_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process custom buttons input."""
    if not context.user_data.get("setting_buttons"):
        return

    import json
    text = update.message.text
    try:
        buttons = json.loads(text)
        if not isinstance(buttons, list) or len(buttons) > 10:
            raise ValueError("Invalid format or too many buttons")
        for btn in buttons:
            if not isinstance(btn, dict) or "text" not in btn or ("url" not in btn and "callback" not in btn):
                raise ValueError("Invalid button format")
            if "url" in btn:
                url = btn["url"]
                if "{file_link}" in url and not url.startswith("{file_link}"):
                    raise ValueError("Invalid URL format for {file_link}")
        await set_setting("custom_buttons", buttons)
        await update.message.reply_text("✅ Custom buttons set!", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Back to Settings ⬅️", callback_data="settings")]
        ]))
        context.user_data["setting_buttons"] = False
        await log_error(f"Custom buttons set by {update.effective_user.id}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Invalid JSON or format: {str(e)}")
        await log_error(f"Button input error: {str(e)}")
