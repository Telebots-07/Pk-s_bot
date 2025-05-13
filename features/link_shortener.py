import requests
from telegram.ext import ContextTypes
from utils.logger import log_error

async def shorten_url(context: ContextTypes.DEFAULT_TYPE, url: str, shortener_name: str = "bitly"):
    """Shorten a URL using the specified shortener."""
    try:
        db = context.bot_data.get("firestore_db")
        if not db:
            log_error("Firestore DB not initialized")
            return url

        shortener_doc = db.collection("shorteners").document(shortener_name).get()
        if not shortener_doc.exists:
            log_error(f"Shortener not configured: {shortener_name}")
            return url

        config = shortener_doc.to_dict()
        api_key = config.get("api_key")
        endpoint = config.get("endpoint")

        if not api_key:
            return url  # Fallback to raw URL

        headers = {"Authorization": f"Bearer {api_key}"}
        data = {"long_url": url}
        response = requests.post(endpoint, headers=headers, json=data)
        response.raise_for_status()
        return response.json().get("link", url)
    except Exception as e:
        log_error(f"Shortener error: {str(e)}, shortener: {shortener_name}")
        return url

async def set_shortener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set API key for a shortener."""
    try:
        user_id = update.effective_user.id
        if user_id not in context.bot_data.get("ADMIN_IDS", []):
            await update.message.reply_text("🚫 Admins only.")
            return

        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Usage: /shortener <name> <api_key>")
            return

        name, api_key = args
        db = context.bot_data.get("firestore_db")
        if not db:
            await update.message.reply_text("⚠️ Database unavailable.")
            log_error("Firestore DB not initialized")
            return

        db.collection("shorteners").document(name).set({
            "name": name,
            "api_key": api_key,
            "endpoint": get_shortener_endpoint(name)
        })
        await update.message.reply_text(f"✅ Shortener {name} configured!")
    except Exception as e:
        await update.message.reply_text("⚠️ Error setting shortener. Try again.")
        log_error(f"Set shortener error: {str(e)}, name: {name}")

def get_shortener_endpoint(name: str) -> str:
    """Get API endpoint for a shortener."""
    endpoints = {
        "gplinks": "https://api.gplinks.in/shorten",
        "modijiurl": "https://api.modijiurl.com/shorten",
        "bitly": "https://api-ssl.bitly.com/v4/shorten"
    }
    return endpoints.get(name, "https://api-ssl.bitly.com/v4/shorten")
