from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.db_channel import set_setting, get_setting
from utils.logging_utils import log_error
from handlers.start import shortener_menu, handle_shortener_selection, handle_shortener_input

async def handle_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle settings configuration."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    if str(user_id) not in context.bot_data.get("admin_ids", []):
        await query.message.reply_text("⚠️ Admins only!")
        await log_error(f"Unauthorized settings access by {user_id}")
        return

    action = query.data
    try:
        if action == "add_channel":
            await query.message.reply_text(
                "📨 Forward a message from the channel where I’m an admin.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Cancel ❌", callback_data="cancel_setting")]
                ])
            )
            context.user_data["setting_action"] = "add_channel"
            logger.info(f"✅ Add channel initiated by {user_id}")
        elif action == "set_db_channel":
            await query.message.reply_text(
                "📨 Forward a message from the channel where I’m an admin to set as DB channel.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Cancel ❌", callback_data="cancel_setting")]
                ])
            )
            context.user_data["setting_action"] = "set_db_channel"
            logger.info(f"✅ Set DB channel initiated by {user_id}")
        elif action == "shortener":
            await shortener_menu(update, context)
        elif action in ["set_shortener_gplinks", "set_shortener_modijiurl", "set_shortener_other"]:
            await handle_shortener_selection(update, context)
        else:
            await query.message.reply_text("⚠️ Unsupported setting action!")
            await log_error(f"Unsupported setting action by {user_id}: {action}")
    except Exception as e:
        await query.message.reply_text("⚠️ Failed to process setting!")
        await log_error(f"Settings error for {user_id}: {str(e)}")

async def handle_forwarded_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process forwarded message for channel or DB channel settings."""
    user_id = update.effective_user.id
    if str(user_id) not in context.bot_data.get("admin_ids", []):
        await update.message.reply_text("⚠️ Admins only!")
        await log_error(f"Unauthorized forwarded message by {user_id}")
        return

    setting_action = context.user_data.get("setting_action")
    if setting_action not in ["add_channel", "set_db_channel"]:
        return

    try:
        if not update.message.forward_from_chat or update.message.forward_from_chat.type != "channel":
            await update.message.reply_text("⚠️ Please forward a message from a channel!")
            await log_error(f"Invalid forwarded message by {user_id}")
            return

        channel_id = str(update.message.forward_from_chat.id)
        # Validate bot admin status
        bot_member = await context.bot.get_chat_member(channel_id, context.bot.id)
        if bot_member.status not in ["administrator", "creator"]:
            await update.message.reply_text("⚠️ I’m not an admin in this channel!")
            await log_error(f"Bot not admin in {channel_id} by {user_id}")
            return

        if setting_action == "add_channel":
            channels = await get_setting("storage_channels", [])
            if channel_id not in channels:
                channels.append(channel_id)
                await set_setting("storage_channels", channels)
                await update.message.reply_text(
                    "✅ Channel added!",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Back to Settings ⬅️", callback_data="settings")]
                    ])
                )
                logger.info(f"✅ Channel {channel_id} added by {user_id}")
            else:
                await update.message.reply_text(
                    "⚠️ Channel already added!",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Back to Settings ⬅️", callback_data="settings")]
                    ])
                )
                logger.info(f"⚠️ Channel {channel_id} already exists by {user_id}")
        elif setting_action == "set_db_channel":
            settings = await get_setting("settings", {})
            settings["db_channel_id"] = channel_id
            await set_setting("settings", settings)
            await update.message.reply_text(
                "✅ DB Channel set!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Back to Settings ⬅️", callback_data="settings")]
                ])
            )
            logger.info(f"✅ DB Channel {channel_id} set by {user_id}")

        context.user_data["setting_action"] = None
    except Exception as e:
        await update.message.reply_text("⚠️ Failed to process forwarded message!")
        await log_error(f"Forwarded message error for {user_id}: {str(e)}")
