# ============================================================
#   Global Media Downloader Bot - Main
#   Version: 1.0 | Pyrogram + yt-dlp + SQLite3
# ============================================================

import os
from pyrogram import Client
from config import BOT_TOKEN, API_ID, API_HASH
from database import init_db

# Import handlers (they register themselves via decorators)
from handlers import start, download, verify, admin


def main():
    print("🤖 Starting Global Media Downloader Bot...")

    # Initialize database
    init_db()
    print("✅ Database initialized.")

    # Create downloads directory
    os.makedirs("./downloads", exist_ok=True)

    # Start Pyrogram client
    app = Client(
        name      = "GlobalMediaDownloader",
        api_id    = API_ID,
        api_hash  = API_HASH,
        bot_token = BOT_TOKEN
    )

    # Include handler modules
    from handlers.start    import start_handler, check_fsub_callback
    from handlers.download import download_handler
    from handlers.verify   import verify_command
    from handlers.admin    import (
        stats_handler, ban_handler, unban_handler,
        addcredits_handler, broadcast_handler
    )

    print("✅ All handlers registered.")
    print("🚀 Bot is running...")
    app.run()


if __name__ == "__main__":
    main()
