from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.db_channel import set_setting
from utils.logger import log_error
import uuid

async def create_clone_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle creation of a new cloned bot."""
    query = update.callback_query
    await query.answer()

    if str(update.effective_user.id) not in context.bot_data.get("admin_ids", []):
        await query.message.reply_text("⚠️ Admins only!")
        return

    await query.message.reply_text(
        "🤖 Enter the admin ID for the new bot (e.g., 123456789).",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Cancel ❌", callback_data="cancel_clone")]
        ])
    )
    context.user_data["creating_clone"] = True

async def view_clone_bots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of cloned bots."""
    query = update.callback_query
    await query.answer()

    if str(update.effective_user.id) not in context.bot_data.get("admin_ids", []):
        await query.message.reply_text("⚠️ Admins only!")
        return

    cloned_bots = await get_setting("cloned_bots", [])
    if not cloned_bots:
        await query.message.reply_text("🤖 No cloned bots created yet!")
        return

    keyboard = [[InlineKeyboardButton(f"Bot {bot['bot_id']}", callback_data=f"manage_{bot['bot_id']}")] for bot in cloned_bots]
    keyboard.append([InlineKeyboardButton("Back ⬅️", callback_data="main_menu")])
    await query.message.edit_text("🤖 Your cloned bots:", reply_markup=InlineKeyboardMarkup(keyboard))
