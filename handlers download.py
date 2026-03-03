# ============================================================
#   Download Handler
# ============================================================

import asyncio
import re
from pyrogram import Client, filters
from pyrogram.types import Message
from config import AUTO_DELETE_TIMER, FSUB_CHANNEL_ID
from database import get_credits, deduct_credit, get_user_status
from downloader import download_video, delete_file
from helpers import generate_verify_link
from handlers.start import check_fsub

# Regex pattern for supported URLs
URL_PATTERN = re.compile(
    r"(https?://)?(www\.)?"
    r"(youtube\.com/watch\?v=|youtu\.be/|"
    r"facebook\.com/(watch|video|reel)|fb\.watch/|"
    r"instagram\.com/(p|reel|tv)/)"
    r"[^\s]+",
    re.IGNORECASE
)


@Client.on_message(filters.private & filters.text & ~filters.command(["start", "verify", "admin", "stats", "ban", "unban", "broadcast"]))
async def download_handler(client: Client, message: Message):
    user_id = message.from_user.id
    text    = message.text.strip()

    # --- Only process if it looks like a URL ---
    if not URL_PATTERN.search(text):
        await message.reply_text(
            "❓ Please send a valid **YouTube**, **Facebook**, or **Instagram** video link."
        )
        return

    # --- Status Check ---
    status = get_user_status(user_id)
    if status == "Banned":
        await message.reply_text("🚫 You are banned from using this bot.")
        return

    # --- FSUB Check ---
    if not await check_fsub(client, user_id):
        await message.reply_text(
            "⚠️ Please join our channel first! Send /start"
        )
        return

    # --- Credits Check ---
    credits = get_credits(user_id)
    if credits <= 0:
        verify_link = await generate_verify_link(user_id)
        await message.reply_text(
            "😔 **Limit Reached!**\n\n"
            f"Your credits are **0**.\n\n"
            f"To get **+5 Credits**, complete the verification:\n"
            f"👉 [Click Here to Verify]({verify_link})\n\n"
            f"_After completing the ad, you'll be redirected back to the bot with your token._",
            disable_web_page_preview=True
        )
        return

    # --- Start Download ---
    status_msg = await message.reply_text("⏳ **Downloading...** Please wait.")

    result = await download_video(text)

    if not result["success"]:
        await status_msg.edit_text(
            f"❌ **Download Failed!**\n\n`{result['error']}`\n\n"
            "Please make sure the link is valid and the video is publicly accessible."
        )
        return

    # --- Send Video ---
    await status_msg.edit_text("📤 **Uploading video...**")

    try:
        sent_msg = await client.send_video(
            chat_id    = user_id,
            video      = result["file_path"],
            caption    = (
                f"✅ **{result['title']}**\n\n"
                f"⏱ Duration: `{result['duration'] // 60}m {result['duration'] % 60}s`\n"
                f"⚠️ _This video will be auto-deleted in 1 hour (Copyright Policy)._"
            ),
            supports_streaming = True
        )

        # Deduct 1 credit
        deduct_credit(user_id)
        remaining = get_credits(user_id)

        await status_msg.delete()

        # Notify remaining credits
        await client.send_message(
            user_id,
            f"💳 **Credits Remaining: `{remaining}`**\n"
            + (f"\n⚠️ Credits low! Get more by sending /start" if remaining <= 1 else "")
        )

        # Schedule auto-delete after 1 hour
        asyncio.create_task(auto_delete(client, user_id, sent_msg.id, result["file_path"]))

    except Exception as e:
        await status_msg.edit_text(f"❌ Upload failed: `{e}`")
        delete_file(result["file_path"])


async def auto_delete(client: Client, chat_id: int, message_id: int, file_path: str):
    """Auto-delete video after AUTO_DELETE_TIMER seconds."""
    await asyncio.sleep(AUTO_DELETE_TIMER)
    try:
        await client.delete_messages(chat_id, message_id)
        await client.send_message(
            chat_id,
            "🗑 **Auto-Delete Notice**\n\n"
            "Your downloaded video has been deleted to comply with copyright policies.\n"
            "Download again anytime!"
        )
    except Exception as e:
        print(f"[AutoDelete Error]: {e}")
    finally:
        delete_file(file_path)
