from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.logger import log_error
from features.link_shortener import shorten_url
from handlers.request import handle_request

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

    # Check chat type
    if chat_type != "private":
        # Treat as a request in group chats
        await update.message.reply_text(
            "🔍 Use /search in private chats. Treating this as a file request!"
        )
        log_error(f"Group /search attempt: {query}, user_id: {user_id}")
        # Pass to request handler
        context.user_data["request_query"] = query
        await handle_request(update, context)
        return

    # Private chat: Perform search
    try:
        db = context.bot_data.get("firestore_db")
        # Query Firestore (simple text search, can enhance with fuzzy search)
        results = db.collection("cloned_files").where("caption", ">=", query).where("caption", "<=", query + "\uf8ff").limit(5).get()

        if not results:
            await update.message.reply_text(
                "🔍 No files found. Try a different query (e.g., 'leo telugu')?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Suggest leo telugu", callback_data="suggest_leo telugu")]
                ])
            )
            return

        # Build response with shortened links
        response = f"🔍 **Search results for '{query}':**\n\n"
        buttons = []
        for doc in results:
            metadata = doc.to_dict()
            searchable_id = metadata["searchable_id"]
            caption = metadata.get("caption", "No caption")
            # Shorten link
            retrieve_url = f"https://t.me/{context.bot.username}?start=retrieve_{searchable_id}"
            shortened_url = await shorten_url(context, retrieve_url, shortener_name="bitly")
            response += f"📄 {caption}\nLink: {shortened_url}\n\n"
            buttons.append([
                InlineKeyboardButton(f"Retrieve: {caption[:20]}", callback_data=f"retrieve_{searchable_id}"),
                InlineKeyboardButton("Delete", callback_data=f"delete_{searchable_id}")
            ])

        await update.message.reply_text(
            response,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Search error: {str(e)}")
        log_error(f"Search error: {str(e)}, query: {query}, user_id: {user_id}")

async def handle_search_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle search result buttons (Retrieve, Delete, Suggest)."""
    query = update.callback_query
    await query.answer()

    callback_data = query.data
    action, value = callback_data.split("_", 1)

    if action == "retrieve":
        db = context.bot_data.get("firestore_db")
        doc = db.collection("cloned_files").document(value).get()
        if not doc.exists:
            await query.message.reply_text("⚠️ File not found.")
            return
        metadata = doc.to_dict()
        try:
            await context.bot.forward_message(
                chat_id=query.message.chat_id,
                from_chat_id=os.getenv("PRIVATE_CHANNEL_ID"),
                message_id=metadata["message_id"]
            )
            await query.message.reply_text("✅ **File retrieved!**")
        except Exception as e:
            await query.message.reply_text(f"⚠️ Retrieve error: {str(e)}")
            log_error(f"Retrieve error: {str(e)}, searchable_id: {value}")

    elif action == "delete":
        db = context.bot_data.get("firestore_db")
        try:
            db.collection("cloned_files").document(value).delete()
            await context.bot.delete_message(
                chat_id=os.getenv("PRIVATE_CHANNEL_ID"),
                message_id=doc.to_dict().get("message_id")
            )
            await query.message.reply_text("🗑️ File deleted.")
        except Exception as e:
            await query.message.reply_text(f"⚠️ Delete error: {str(e)}")
            log_error(f"Delete error: {str(e)}, searchable_id: {value}")

    elif action == "suggest":
        context.user_data["request_query"] = value
        await handle_request(update, context)
