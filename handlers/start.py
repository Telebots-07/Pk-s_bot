from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.firestore import get_group_link

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with dynamic group link for admins."""
    user_id = update.effective_user.id
    is_admin = user_id in context.bot_data.get("ADMIN_IDS", [])

    # Get dynamic group link
    group_link = await get_group_link(context) or os.getenv("REQUEST_GROUP_LINK", "https://t.me/+your_group_id")

    if is_admin:
        db = context.bot_data.get("firestore_db")
        file_count = len(db.collection("cloned_files").get())
        await update.message.reply_text(
            f"👋 Welcome, Admin! Files: {file_count}\nRequest group: {group_link}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Help", callback_data="help")],
                [InlineKeyboardButton("Clone Info", callback_data="clone_info")],
                [InlineKeyboardButton("About", callback_data="about")]
            ])
        )
    else:
        await update.message.reply_text(
            f"👋 Welcome! Request files in: {group_link}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Join Group", url=group_link)]
            ])
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    await update.message.reply_text(
        "📚 Commands:\n/start - Start the bot\n/help - Show this message\n/search - Search files (admins only, private DM)\n/tutorial - Learn how to use the bot"
    )

async def clone_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /clone_info command."""
    await update.message.reply_text("ℹ️ This bot clones and manages files securely.")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command."""
    await update.message.reply_text("🤖 Cloner Bot: Your secure file management assistant.")
