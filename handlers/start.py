from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.db_channel import get_setting
from utils.logger import log_error

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with dynamic menu."""
    user_id = update.effective_user.id
    admin_ids = context.bot_data.get("admin_ids", [])

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
    else:
        # Non-admin menu
        group_link = await get_setting("group_link", "https://t.me/+default_group")
        try:
            if not group_link.startswith("https://t.me/"):
                group_link = "https://t.me/+default_group"
                await log_error(f"Invalid group link, using default")
        except Exception as e:
            await log_error(f"Group link error: {str(e)}")
        keyboard = [
            [InlineKeyboardButton("Join Group 🌐", url=group_link)],
            [InlineKeyboardButton("Tutorial 📚", callback_data="tutorial"),
             InlineKeyboardButton("About ℹ️", callback_data="about")]
        ]
        text = "👋 Welcome to the Cloner Bot!\nJoin our group to request files.\nCreated by @bot_paiyan_official"

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
        except Exception as e:
            await log_error(f"Force-sub check error: {str(e)}")
            text = "⚠️ Error checking channel membership. Try again!"

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings submenu."""
    query = update.callback_query
    await query.answer()

    if str(update.effective_user.id) not in context.bot_data.get("admin_ids", []):
        await query.message.reply_text("⚠️ Admins only!")
        return

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
