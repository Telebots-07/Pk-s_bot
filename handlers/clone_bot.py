from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.db_channel import set_setting, get_setting
from utils.logger import log_error
import uuid

async def create_clone_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle creation of a new cloned bot."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    if str(user_id) not in context.bot_data.get("admin_ids", []):
        await query.message.reply_text("⚠️ Admins only!")
        await log_error(f"Unauthorized clone bot access by {user_id}")
        return

    try:
        # Simulated token generation (replace with @BotFather integration if needed)
        available_tokens = await get_setting("available_tokens", ["123456789:ABCDEF", "987654321:XYZ"])
        if not available_tokens:
            await query.message.reply_text("⚠️ No bot tokens available!")
            await log_error(f"No tokens available for {user_id}")
            return

        token = available_tokens.pop(0)
        await set_setting("available_tokens", available_tokens)

        await query.message.reply_text(
            "🤖 Enter the admin ID for the new bot (e.g., 123456789).",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Cancel ❌", callback_data="cancel_clone")]
            ])
        )
        context.user_data["creating_clone"] = True
        context.user_data["clone_token"] = token
        logger.info(f"✅ Clone bot creation initiated by {user_id}")
    except Exception as e:
        await query.message.reply_text("⚠️ Failed to initiate bot creation!")
        await log_error(f"Clone bot creation error for {user_id}: {str(e)}")

async def handle_clone_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process admin ID for new cloned bot."""
    if not context.user_data.get("creating_clone"):
        return

    user_id = update.effective_user.id
    text = update.message.text
    try:
        admin_id = int(text)
        token = context.user_data["clone_token"]
        bot_id = str(uuid.uuid4())

        cloned_bots = await get_setting("cloned_bots", [])
        cloned_bots.append({"bot_id": bot_id, "token": token, "admin_ids": [admin_id]})
        await set_setting("cloned_bots", cloned_bots)

        await update.message.reply_text(
            f"✅ Bot created! Token: {token}\nUse it to configure your bot.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Back to Menu ⬅️", callback_data="main_menu")]
            ])
        )
        context.user_data["creating_clone"] = False
        context.user_data["clone_token"] = None
        logger.info(f"✅ Cloned bot created by {user_id}: {bot_id}")
    except ValueError:
        await update.message.reply_text("⚠️ Invalid admin ID! Enter a number.")
        await log_error(f"Invalid admin ID by {user_id}: {text}")
    except Exception as e:
        await update.message.reply_text("⚠️ Failed to create bot!")
        await log_error(f"Clone bot input error for {user_id}: {str(e)}")

async def view_clone_bots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of cloned bots."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    if str(user_id) not in context.bot_data.get("admin_ids", []):
        await query.message.reply_text("⚠️ Admins only!")
        await log_error(f"Unauthorized clone bots view by {user_id}")
        return

    try:
        cloned_bots = await get_setting("cloned_bots", [])
        if not cloned_bots:
            await query.message.reply_text("🤖 No cloned bots created yet!")
            logger.info(f"✅ No cloned bots for {user_id}")
            return

        keyboard = [[InlineKeyboardButton(f"Bot {bot['bot_id'][:8]}", callback_data=f"manage_{bot['bot_id']}")] for bot in cloned_bots]
        keyboard.append([InlineKeyboardButton("Back ⬅️", callback_data="main_menu")])
        await query.message.edit_text("🤖 Your cloned bots:", reply_markup=InlineKeyboardMarkup(keyboard))
        logger.info(f"✅ Cloned bots shown for {user_id}")
    except Exception as e:
        await query.message.reply_text("⚠️ Failed to show cloned bots!")
        await log_error(f"Clone bots view error for {user_id}: {str(e)}")
