# ============================================================
#   /verify Handler
# ============================================================

from pyrogram import Client, filters
from pyrogram.types import Message
from config import AD_REWARD_CREDITS
from database import verify_token, add_credits, get_credits


@Client.on_message(filters.command("verify") & filters.private)
async def verify_command(client: Client, message: Message):
    user_id = message.from_user.id
    args    = message.text.split()

    if len(args) < 2:
        await message.reply_text(
            "❓ **Usage:** `/verify YOUR_TOKEN`\n\n"
            "You'll get the token after completing the ad verification link."
        )
        return

    token = args[1].strip().upper()
    await _process_verify(client, message, user_id, token)


async def handle_verify_deep_link(client: Client, message: Message, token: str):
    """Called when user comes from deep link /start verify_TOKEN"""
    await _process_verify(client, message, message.from_user.id, token.upper())


async def _process_verify(client: Client, message: Message, user_id: int, token: str):
    if verify_token(token, user_id):
        add_credits(user_id, AD_REWARD_CREDITS)
        new_balance = get_credits(user_id)
        await message.reply_text(
            f"🎉 **Verification Successful!**\n\n"
            f"✅ **+{AD_REWARD_CREDITS} Credits** added to your account.\n"
            f"💳 **New Balance: `{new_balance}` Credits**\n\n"
            f"Now send a video link to download! 🚀"
        )
    else:
        await message.reply_text(
            "❌ **Invalid or Expired Token!**\n\n"
            "The token may have already been used or is incorrect.\n"
            "Please generate a new verification link by trying to download."
        )
