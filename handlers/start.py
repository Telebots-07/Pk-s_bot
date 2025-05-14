from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.db_channel import get_setting, set_setting
from utils.logger import log_error

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with dynamic menu."""
    user_id = update.effective_user.id
    admin_ids = context.bot_data.get("admin_ids", [])

    try:
        if str(user_id) in admin_ids:
            # Admin menu
            keyboard = [
                [InlineKeyboardButton("Files 📂", callback_data="files"),
                 InlineKeyboardButton("Settings ⚙️", callback_data="settings")],
                [InlineKeyboardButton("Start Text ✍️", callback_data="start_text"),
                 InlineKeyboardButton("Tutorial 📚", callback_data="tutorial")],
                [InlineKeyboardButton("Broadcast 📢", callback_data="broadcast"),
                 InlineKeyboardButton("Batch 📦", callback_data="batch")],
                [InlineKeyboardButton("Deploy Bot 🚀", callback_data="deploy_bot"),
                 InlineKeyboardButton("Clone Bot 🤖", callback_data="clone_bot")]
            ]
            text = "👋 Welcome, Admin! Manage your bot with ease.\nCreated by @bot_paiyan_official"
            logger.info(f"✅ Admin menu shown for {user_id}")
        else:
            # Non-admin menu
            group_link = await get_setting("group_link", "https://t.me/+default_group")
            if not group_link.startswith("https://t.me/"):
                group_link = "https://t.me/+default_group"
                await log_error(f"Invalid group link for {user_id}, using default")
            keyboard = [
                [InlineKeyboardButton("Join Group 🌐", url=group_link)],
                [InlineKeyboardButton("Tutorial 📚", callback_data="tutorial"),
                 InlineKeyboardButton("About ℹ️", callback_data="about")]
            ]
            text = "👋 Welcome to the Cloner Bot!\nJoin our group to request files.\nCreated by @bot_paiyan_official"
            logger.info(f"✅ Non-admin menu shown for {user_id}")

        # Check force-sub
        force_sub = await get_setting("force_sub_channel")
        if force_sub and str(user_id) not in admin_ids:
            try:
                is_member = await context.bot.get_chat_member(force_sub, user_id)
                if is_member.status not in ["member", "administrator", "creator"]:
                    force_sub_link = f"https://t.me/{force_sub[1:]}"
                    keyboard = [
                        [InlineKeyboardButton("Join Channel 🔗", url=force_sub_link),
                         InlineKeyboardButton("Verify ✅", callback_data="verify")]
                    ]
                    text = "⚠️ Please join our channel to use the bot!"
                    await log_error(f"Force-sub required for {user_id}")
            except Exception as e:
                text = "⚠️ Error checking channel membership. Try again!"
                await log_error(f"Force-sub check error for {user_id}: {str(e)}")

        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        logger.info(f"✅ Start command processed for {user_id}")
    except Exception as e:
        await update.message.reply_text("⚠️ Failed to process start command!")
        await log_error(f"Start command error for {user_id}: {str(e)}")

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings submenu."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    if str(user_id) not in context.bot_data.get("admin_ids", []):
        await query.message.reply_text("⚠️ Admins only!")
        await log_error(f"Unauthorized settings access by {user_id}")
        return

    try:
        keyboard = [
            [InlineKeyboardButton("Add Channel ➕", callback_data="add_channel"),
             InlineKeyboardButton("Remove Channel ➖", callback_data="remove_channel")],
            [InlineKeyboardButton("Set Force-Sub 🔗", callback_data="set_force_sub"),
             InlineKeyboardButton("Set Group Link 🌐", callback_data="set_group_link")],
            [InlineKeyboardButton("Set DB Channel ➕", callback_data="set_db_channel"),
             InlineKeyboardButton("Set Log Channel 📝", callback_data="set_log_channel")],
            [InlineKeyboardButton("Shortener 🔗", callback_data="shortener"),
             InlineKeyboardButton("Welcome Message 👋", callback_data="welcome_message")],
            [InlineKeyboardButton("Auto-Delete 🗑️", callback_data="auto_delete"),
             InlineKeyboardButton("Banner 🎨", callback_data="banner")],
            [InlineKeyboardButton("Set Custom Caption ✍️", callback_data="set_custom_caption"),
             InlineKeyboardButton("Set Custom Buttons 🔘", callback_data="set_custom_buttons")],
            [InlineKeyboardButton("Set Webhook URL 🌐", callback_data="set_webhook"),
             InlineKeyboardButton("Anti-Ban 🔒", callback_data="anti_ban")],
            [InlineKeyboardButton("Enable Redis ⚡", callback_data="enable_redis"),
             InlineKeyboardButton("Back ⬅️", callback_data="main_menu")]
        ]
        await query.message.edit_text("⚙️ Settings", reply_markup=InlineKeyboardMarkup(keyboard))
        logger.info(f"✅ Settings menu shown for {user_id}")
    except Exception as e:
        await query.message.reply_text("⚠️ Failed to show settings menu!")
        await log_error(f"Settings menu error for {user_id}: {str(e)}")

async def shortener_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show shortener submenu."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    if str(user_id) not in context.bot_data.get("admin_ids", []):
        await query.message.reply_text("⚠️ Admins only!")
        await log_error(f"Unauthorized shortener access by {user_id}")
        return

    try:
        keyboard = [
            [InlineKeyboardButton("GPLinks 🔗", callback_data="set_shortener_gplinks"),
             InlineKeyboardButton("ModijiURL 🔗", callback_data="set_shortener_modijiurl")],
            [InlineKeyboardButton("Other 🔗", callback_data="set_shortener_other"),
             InlineKeyboardButton("Back ⬅️", callback_data="settings")]
        ]
        await query.message.edit_text("🔗 Select a Shortener", reply_markup=InlineKeyboardMarkup(keyboard))
        logger.info(f"✅ Shortener menu shown for {user_id}")
    except Exception as e:
        await query.message.reply_text("⚠️ Failed to show shortener menu!")
        await log_error(f"Shortener menu error for {user_id}: {str(e)}")

async def handle_shortener_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle shortener selection."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    if str(user_id) not in context.bot_data.get("admin_ids", []):
        await query.message.reply_text("⚠️ Admins only!")
        await log_error(f"Unauthorized shortener selection by {user_id}")
        return

    action = query.data
    try:
        if action == "set_shortener_gplinks":
            # Check if GPLinks API token is set
            shortener = await get_setting("shortener", {"type": "none", "api_key": ""})
            if not shortener.get("api_key"):
                await query.message.reply_text(
                    "🔑 Enter your GPLinks API token.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Cancel ❌", callback_data="cancel_shortener")]
                    ])
                )
                context.user_data["setting_shortener"] = "gplinks"
                logger.info(f"✅ GPLinks token input initiated by {user_id}")
            else:
                await set_setting("shortener", {"type": "gplinks", "api_key": shortener["api_key"]})
                await query.message.reply_text(
                    "✅ Shortener set to GPLinks!",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Back to Settings ⬅️", callback_data="settings")]
                    ])
                )
                logger.info(f"✅ Shortener set to GPLinks by {user_id}")
        elif action in ["set_shortener_modijiurl", "set_shortener_other"]:
            await query.message.reply_text(
                "⚠️ Under Development 🚧",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Back to Shorteners ⬅️", callback_data="shortener")]
                ])
            )
            logger.info(f"✅ Under development shown for {action} by {user_id}")
        else:
            await query.message.reply_text("⚠️ Invalid shortener selection!")
            await log_error(f"Invalid shortener action by {user_id}: {action}")
    except Exception as e:
        await query.message.reply_text("⚠️ Failed to process shortener selection!")
        await log_error(f"Shortener selection error for {user_id}: {str(e)}")

async def handle_shortener_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process shortener API token input."""
    if not context.user_data.get("setting_shortener"):
        return

    user_id = update.effective_user.id
    api_key = update.message.text
    shortener_type = context.user_data["setting_shortener"]

    try:
        if not api_key:
            await update.message.reply_text("⚠️ API token cannot be empty!")
            await log_error(f"Empty API token for {shortener_type} by {user_id}")
            return

        await set_setting("shortener", {"type": shortener_type, "api_key": api_key})
        await update.message.reply_text(
            f"✅ Shortener set to {shortener_type.capitalize()}!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Back to Settings ⬅️", callback_data="settings")]
            ])
        )
        context.user_data["setting_shortener"] = None
        logger.info(f"✅ Shortener {shortener_type} set by {user_id}")
    except Exception as e:
        await update.message.reply_text("⚠️ Failed to set shortener!")
        await log_error(f"Shortener input error for {user_id}: {str(e)}")
