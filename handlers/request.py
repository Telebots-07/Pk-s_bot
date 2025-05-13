from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from uuid import uuid4
from utils.logger import log_error
from features.link_shortener import shorten_url

async def handle_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages in group chats as file requests."""
    chat_type = update.message.chat.type
    if chat_type not in ["group", "supergroup"]:
        return  # Silently ignore non-group chats

    query = context.user_data.get("request_query") or update.message.text.strip()
    if not query:
        await update.message.reply_text("📨 Please provide a file name or query.")
        return

    try:
        # Generate request ID
        request_id = str(uuid4())
        db = context.bot_data.get("firestore_db")

        # Check for matches (fuzzy search simulation)
        results = db.collection("cloned_files").where("caption", ">=", query).where("caption", "<=", query + "\uf8ff").limit(1).get()
        suggestion = None
        if not results:
            # Suggest alternative (e.g., replace 'tamil' with 'telugu')
            alt_query = query.replace("tamil", "telugu") if "tamil" in query.lower() else "leo telugu"
            suggestion = alt_query

        # Store request
        db.collection("requests").document(request_id).set({
            "query": query,
            "user_id": update.message.from_user.id,
            "timestamp": update.message.date.isoformat(),
            "status": "pending"
        })

        # Generate shortened startid link
        startid_url = f"https://t.me/{context.bot.username}?start=request_{request_id}"
        shortened_url = await shorten_url(context, startid_url, shortener_name="bitly")

        # Reply to user
        reply_text = f"📨 **Request submitted:** {query}\nCheck status: {shortened_url}"
        buttons = [[InlineKeyboardButton("Check Status", url=shortened_url)]]
        if suggestion:
            reply_text += f"\n\nNo exact matches. Try '{suggestion}'?"
            buttons.append([InlineKeyboardButton(f"Suggest: {suggestion}", callback_data=f"suggest_{suggestion}")])

        await update.message.reply_text(
            reply_text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

        # Notify admins
        for admin_id in context.bot_data.get("ADMIN_IDS", []):
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"📬 **New request:** {query}\nRequest ID: {request_id}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Approve", callback_data=f"approve_{request_id}")],
                    [InlineKeyboardButton("Deny", callback_data=f"deny_{request_id}")]
                ])
            )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Request error: {str(e)}")
        log_error(f"Request error: {str(e)}, query: {query}")

async def handle_request_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle request approval/denial buttons."""
    query = update.callback_query
    await query.answer()

    callback_data = query.data
    action, request_id = callback_data.split("_", 1)

    db = context.bot_data.get("firestore_db")
    request_doc = db.collection("requests").document(request_id).get()

    if not request_doc.exists:
        await query.message.reply_text("⚠️ Request not found.")
        return

    request = request_doc.to_dict()
    user_id = request["user_id"]
    query_text = request["query"]

    try:
        if action == "approve":
            # Forward matching file (simplified; enhance with search)
            results = db.collection("cloned_files").where("caption", ">=", query_text).where("caption", "<=", query_text + "\uf8ff").limit(1).get()
            if results:
                metadata = results[0].to_dict()
                await context.bot.forward_message(
                    chat_id=user_id,
                    from_chat_id=os.getenv("PRIVATE_CHANNEL_ID"),
                    message_id=metadata["message_id"]
                )
                status = "approved"
                reply_text = "✅ **Request approved!** File sent."
            else:
                status = "no_match"
                reply_text = "⚠️ **Request approved, but no matching file found.**"
        else:
            status = "denied"
            reply_text = "❌ **Request denied.**"

        # Update request status
        db.collection("requests").document(request_id).update({"status": status})

        # Notify user
        await context.bot.send_message(
            chat_id=user_id,
            text=reply_text
        )
        await query.message.reply_text(reply_text)

    except Exception as e:
        await query.message.reply_text(f"⚠️ Error processing request: {str(e)}")
        log_error(f"Request callback error: {str(e)}, request_id: {request_id}")
