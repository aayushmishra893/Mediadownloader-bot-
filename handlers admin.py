# ============================================================
#   Admin Panel Handler
# ============================================================

from pyrogram import Client, filters
from pyrogram.types import Message
from config import ADMIN_IDS, AD_REWARD_CREDITS
from database import (
    get_stats, ban_user, unban_user,
    add_credits, get_all_users, get_credits
)


def admin_only(func):
    """Decorator to restrict commands to admins only."""
    async def wrapper(client, message):
        if message.from_user.id not in ADMIN_IDS:
            await message.reply_text("🚫 **Admin Only Command!**")
            return
        await func(client, message)
    return wrapper


@Client.on_message(filters.command("stats") & filters.private)
@admin_only
async def stats_handler(client: Client, message: Message):
    data = get_stats()
    await message.reply_text(
        "📊 **Bot Statistics**\n\n"
        f"👥 Total Users   : `{data['total']}`\n"
        f"✅ Active Users  : `{data['active']}`\n"
        f"🚫 Banned Users  : `{data['banned']}`\n"
    )


@Client.on_message(filters.command("ban") & filters.private)
@admin_only
async def ban_handler(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("❓ Usage: `/ban USER_ID`")
        return
    try:
        target_id = int(args[1])
        ban_user(target_id)
        await message.reply_text(f"✅ User `{target_id}` has been **banned**.")
    except ValueError:
        await message.reply_text("❌ Invalid User ID!")


@Client.on_message(filters.command("unban") & filters.private)
@admin_only
async def unban_handler(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("❓ Usage: `/unban USER_ID`")
        return
    try:
        target_id = int(args[1])
        unban_user(target_id)
        await message.reply_text(f"✅ User `{target_id}` has been **unbanned**.")
    except ValueError:
        await message.reply_text("❌ Invalid User ID!")


@Client.on_message(filters.command("addcredits") & filters.private)
@admin_only
async def addcredits_handler(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 3:
        await message.reply_text("❓ Usage: `/addcredits USER_ID AMOUNT`")
        return
    try:
        target_id = int(args[1])
        amount    = int(args[2])
        add_credits(target_id, amount)
        new_bal = get_credits(target_id)
        await message.reply_text(
            f"✅ Added **{amount} credits** to user `{target_id}`.\n"
            f"💳 New Balance: `{new_bal}`"
        )
    except ValueError:
        await message.reply_text("❌ Invalid User ID or Amount!")


@Client.on_message(filters.command("broadcast") & filters.private)
@admin_only
async def broadcast_handler(client: Client, message: Message):
    """Broadcast a message to all active users."""
    if not message.reply_to_message:
        await message.reply_text(
            "❓ Reply to a message with `/broadcast` to send it to all users."
        )
        return

    all_users = get_all_users()
    success, failed = 0, 0

    status_msg = await message.reply_text(
        f"📡 **Broadcasting to {len(all_users)} users...**"
    )

    for uid in all_users:
        try:
            await message.reply_to_message.copy(uid)
            success += 1
        except Exception:
            failed += 1

    await status_msg.edit_text(
        f"📡 **Broadcast Complete!**\n\n"
        f"✅ Sent    : `{success}`\n"
        f"❌ Failed  : `{failed}`\n"
        f"👥 Total   : `{len(all_users)}`"
    )
