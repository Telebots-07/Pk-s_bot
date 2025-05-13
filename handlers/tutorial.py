from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.logger import log_error
from utils.firestore import get_group_link

async def tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /tutorial command for admins."""
    user_id = update.effective_user.id
    if user_id not in context.bot_data.get("ADMIN_IDS", []):
        await update.message.reply_text("🚫 Admins only.")
        return

    group_link = await get_group_link(context) or os.getenv("REQUEST_GROUP_LINK", "https://t.me/+your_group_id")
    db = context.bot_data.get("firestore_db")
    tutorial_steps = db.collection("tutorials").order_by("step").get()

    if not tutorial_steps:
        default_steps = [
            {
                "step": 1,
                "content": f"Welcome to Cloner Bot! 📂\n- Clone files by sending them to the bot.\n- Request files in: {group_link}",
                "buttons": ["Next", "Try Cloning"]
            },
            {
                "step": 2,
                "content": f"Request Files 📨\n- In groups, type any text (e.g., 'leo tamil') to request.\n- Private /search redirects to: {group_link}",
                "buttons": ["Back", "Try Request"]
            }
        ]
        for step in default_steps:
            db.collection("tutorials").document(str(step["step"])).set(step)

    context.user_data["tutorial_step"] = 1
    await show_tutorial_step(update, context)

async def show_tutorial_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show a tutorial step."""
    step = context.user_data.get("tutorial_step", 1)
    db = context.bot_data.get("firestore_db")
    step_doc = db.collection("tutorials").document(str(step)).get()

    if not step_doc.exists:
        await update.message.reply_text("⚠️ Tutorial step not found.")
        return

    step_data = step_doc.to_dict()
    buttons = []
    for btn in step_data.get("buttons", []):
        if btn == "Next":
            buttons.append([InlineKeyboardButton("Next", callback_data=f"tutorial_{step + 1}")])
        elif btn == "Back":
            buttons.append([InlineKeyboardButton("Back", callback_data=f"tutorial_{step - 1}")])
        elif btn == "Try Cloning":
            buttons.append([InlineKeyboardButton("Try Cloning", callback_data="tutorial_clone")])
        elif btn == "Try Request":
            buttons.append([InlineKeyboardButton("Try Request", callback_data="tutorial_request")])

    await update.message.reply_text(
        step_data["content"],
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def handle_tutorial_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle tutorial navigation."""
    query = update.callback_query
    await query.answer()

    callback_data = query.data
    if callback_data.startswith("tutorial_"):
        action = callback_data.replace("tutorial_", "")
        if action.isdigit():
            context.user_data["tutorial_step"] = int(action)
            await show_tutorial_step(query, context)
        elif action == "clone":
            await query.message.reply_text("📂 Send a file to clone it!")
        elif action == "request":
            group_link = await get_group_link(context) or os.getenv("REQUEST_GROUP_LINK")
            await query.message.reply_text(f"📨 Type a file name in: {group_link}")
