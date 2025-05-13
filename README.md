# Pk-s_bot

Cloner Bot
A Telegram bot for secure file cloning and management.

File Cloning: Clone photos, videos, documents, audio (up to 2GB).
Request Workflow: Group text as file requests, private /search redirects to group.
Dynamic Group Link: Configurable via /settings.
Link Shortener: Supports bitly, gplinks, modijiurl.
Cover Image: Add covers to files.
Tutorial: Admin-only, Firestore-backed.
Batch Operations: /genbatch, /editbatch for bulk cloning/editing.
Anti-Ban: Render deployment, redeployment script, backup channels.

Setup

Clone the repo: git clone <repo_url>
Install dependencies: pip install -r requirements.txt
Set environment variables in Render:
TELEGRAM_TOKEN
ADMIN_IDS
PRIVATE_CHANNEL_ID
REQUEST_GROUP_LINK
FIREBASE_CREDENTIALS


Deploy to Render using render.yaml.

Usage

Admins: Use /start, /tutorial, /settings, /search, /genbatch, /editbatch.
Users: Type file names in group to request files.

License
MIT
