Cloner Bot
A Telegram bot for cloning files, managing requests, and hosting cloned bots. Created by @bot_paiyan_official.
Features

File Cloning: Clone files (photo, video, document, audio; max 2GB) to storage channels.
Custom Caption & Buttons: Set custom captions (e.g., 🎥 {filename} | {date}) and buttons (e.g., [Download ⬇️]) for files.
Clone Bot: Host new bot instances via [Clone Bot 🤖]; no user Render deployment.
Shortener Skip: Skip link shortener for 1 hour post-verification.
Dynamic Settings: Configure via button menus, stored in DB channel.
Group Requests: Text as requests, hidden link previews, startid buttons.
User-Friendly: Nested buttons, emojis (e.g., “✅”, “📂”).
Anti-Ban: Private channels, redeployment script.
Render Deployment: Only TELEGRAM_TOKEN, ADMIN_IDS needed.

Setup

Clone Repo:git clone https://github.com/Telebots-07/Pk-s_bot.git
cd cloner_bot


Set Env Vars in Render:
TELEGRAM_TOKEN: From @BotFather.
ADMIN_IDS: Comma-separated admin IDs (e.g., 123456789,987654321).


Deploy:
Create Render Web Service, point to repo, use Dockerfile.
Set env vars in Render dashboard.


Configure:
Run /start, use [Settings ⚙️] to set DB channel, log channel, etc.
Use [Clone Bot 🤖] to create hosted bots.



Folder Structure

bot.py: Main entry point.
handlers/: Handlers for commands/callbacks.
features/: Core features (shortener, cover image, etc.).
utils/: DB channel, logging, helpers.
config/: Settings and shortener configs.
scripts/: Anti-ban scripts.

Contact
Created by @bot_paiyan_official.
