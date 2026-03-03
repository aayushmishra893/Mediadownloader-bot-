# ============================================================
#   /start Handler
# ============================================================

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import FSUB_CHANNEL_ID, FSUB_CHANNEL_LINK, FREE_CREDITS_NEW_USER
from database import add_or_get_user, get_user_status
from handlers.verify import handle_verify_deep_link


async def check_fsub(client: Client, user_id: int) -> bool:
    """Check if user has joined the Force Subscribe channel."""
    try:
        member = await client.get_chat_member(FSUB_CHANNEL_ID, user_id)
        return member.status.value not in ("left", "banned", "kicked")
    except Exception:
        return False


@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    user_id  = message.from_user.id
    username = message.from_user.username or message.from_user.first_name

    # --- Handle deep link verify (e.g. /start verify_TOKEN) ---
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("verify_"):
        token = args[1].replace("verify_", "")
        await handle_verify_deep_link(client, message, token)
        return

    # --- Force Subscribe Check ---
    if not await check_fsub(client, user_id):
        await message.reply_text(
            "⚠️ **Access Blocked!**\n\n"
            "You must join our Updates Channel first to use this bot.\n\n"
            "👇 Click the button below to join:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ Join Channel", url=FSUB_CHANNEL_LINK),
                InlineKeyboardButton("🔄 I've Joined", callback_data="check_fsub")
            ]])
        )
        return

    # --- Database Check ---
    user = add_or_get_user(user_id, username)

    # --- Banned Check ---
    if user["status"] == "Banned":
        await message.reply_text("🚫 **You have been banned from using this bot.**")
        return

    # --- Welcome Message ---
    welcome_msg = (
        f"👋 **Welcome, {message.from_user.first_name}!**\n\n"
        f"{'🎉 You are a new user! ' if user['is_new'] else ''}"
        f"I can download videos from:\n"
        f"  • 🎥 YouTube\n"
        f"  • 📘 Facebook\n"
        f"  • 📸 Instagram\n\n"
        f"💳 **Your Credits: `{user['credits']}`**\n\n"
        f"📤 Just send me a video link to download!\n"
        f"⚡ Each download costs **1 Credit**."
    )
    await message.reply_text(welcome_msg)


# --- Callback: Re-check FSUB ---
@Client.on_callback_query(filters.regex("^check_fsub$"))
async def check_fsub_callback(client, callback_query):
    user_id = callback_query.from_user.id
    if await check_fsub(client, user_id):
        await callback_query.message.delete()
        await callback_query.message.reply_text(
            "✅ **Verified!** You can now use the bot.\n"
            "Send /start again to continue."
        )
    else:
        await callback_query.answer(
            "❌ You haven't joined yet! Please join first.", show_alert=True
        )
