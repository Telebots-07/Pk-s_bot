from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.logger import log_error
from features.link_shortener import set_shortener

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settings command for admins."""
    user_id = update.effective_user.id
    if user_id not in context.bot_data.get("ADMIN_IDS", []):
        await update.message.reply_text("🚫 Admins only.")
        return

    await update.message.reply_text(
        "⚙️ Settings Menu",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Set Shortener", callback_data="settings_shortener")],
            [InlineKeyboardButton("Set Group Link", callback_data="settings_group_link")],
            [InlineKeyboardButton("Add Channel", callback_data="settings_add_channel")],
            [InlineKeyboardButton("Set Welcome", callback_data="settings_welcome")],
            [InlineKeyboardButton("Auto-Delete", callback_data="settings_autodelete")],
            [InlineKeyboardButton("Banner", callback_data="settings_banner")]
        ])
    )

async def shortener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /shortener command."""
    await set_shortener(update, context)

async def set_group_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set dynamic group link."""
    user_id = update.effective_user.id
    if user_id not in context.bot_data.get("ADMIN_IDS", []):
        await update.message.reply_text("🚫 Admins only.")
        return

    args = context.args
    if not args:
        await update.message.reply_text("Usage: /set_group_link <url>")
        return

    group_link = args[0]
    try:
        db = context.bot_data.get("firestore_db")
        db.collection("settings").document("bot_config").set({"request_group_link": group_link}, merge=True)
        await update.message.reply_text(f"✅ Group link set: {group_link}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error setting group link: {str(e)}")
        log_error(f"Set group link error: {str(e)}")

async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a storage channel."""
    user_id = update.effective_user.id
    if user_id not in context.bot_data.get("ADMIN_IDS", []):
        await update.message.reply_text("🚫 Admins only.")
        return

    args = context.args
    if not args:
        await update.message.reply_text("Usage: /add_channel <channel_id>")
        return

    channel_id = args[0]
    try:
        db = context.bot_data.get("firestore_db")
        db.collection("storage_channels").document(channel_id).set({"channel_id": channel_id, "active": True})
        await update.message.reply_text(f"✅ Channel added: {channel_id}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error adding channel: {str(e)}")
        log_error(f"Add channel error: {str(e)}")

async def set_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set welcome message."""
    user_id = update.effective_user.id
    if user_id not in context.bot_data.get("ADMIN_IDS", []):
        await update.message.reply_text("🚫 Admins only.")
        return

    args = context.args
    if not args:
        await update.message.reply_text("Usage: /set_welcome <message>")
        return

    welcome_message = " ".join(args)
    try:
        db = context.bot_data.get("firestore_db")
        db.collection("settings").document("bot_config").set({"welcome_message": welcome_message}, merge=True)
        await update.message.reply_text(f"✅ Welcome message set: {welcome_message}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error setting welcome: {str(e)}")
        log_error(f"Set welcome error: {str(e)}")

async def autodelete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set auto-delete time."""
    user_id = update.effective_user.id
    if user_id not in context.bot_data.get("ADMIN_IDS", []):
        await update.message.reply_text("🚫 Admins only.")
        return

    args = context.args
    if not args:
        await update.message.reply_text("Usage: /autodelete <hours>")
        return

    hours = args[0]
    try:
        db = context.bot_data.get("firestore_db")
        db.collection("settings").document("bot_config").set({"autodelete_hours": int(hours)}, merge=True)
        await update.message.reply_text(f"✅ Auto-delete set: {hours} hours")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error setting auto-delete: {str(e)}")
        log_error(f"Set autodelete error: {str(e)}")

async def banner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set banner text."""
    user_id = update.effective_user.id
    if user_id not in context.bot_data.get("ADMIN_IDS", []):
        await update.message.reply_text("🚫 Admins only.")
        return

    args = context.args
    if not args:
        await update.message.reply_text("Usage: /banner <text>")
        return

    banner_text = " ".join(args)
    try:
        db = context.bot_data.get("firestore_db")
        db.collection("settings").document("bot_config").set({"banner_text": banner_text}, merge=True)
        await update.message.reply_text(f"✅ Banner text set: {banner_text}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error setting banner: {str(e)}")
        log_error(f"Set banner error: {str(e)}")
