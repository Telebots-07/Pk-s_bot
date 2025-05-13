from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.logger import log_error
from utils.firestore import get_group_link

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /search command, private chats only."""
    user_id = update.effective_user.id
    if user_id not in context.bot_data.get("ADMIN_IDS", []):
        await update.message.reply_text("🚫 Admins only.")
        return

    chat_type = update.message.chat.type
    query = " ".join(context.args).strip()

    if not query:
        await update.message.reply_text("🔍 Usage: /search <query>")
        return

    # Redirect to group for requests
    group_link = await get_group_link(context) or os.getenv("REQUEST_GROUP_LINK", "https://t.me/+your_group_id")
    await update.message.reply_text(
        f"please request in this group this will also added dynamically in admins bot that start text itself ok: {group_link}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Join Group", url=group_link)]
        ])
    )
    log_error(f"Private /search attempt redirected: {query}, user_id: {user_id}")

async def handle_search_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle search suggestion buttons."""
    query = update.callback_query
    await query.answer()

    callback_data = query.data
    action, value = callback_data.split("_", 1)

    if action == "suggest":
        context.user_data["request_query"] = value
        from handlers.request import handle_request
        await handle_request(update, context)
