"""
╔══════════════════════════════════════════════════════════════╗
║           core/handlers/admin.py                            ║
║   Admin & sudo-only commands                                ║
║   Sudo ID: 8192070400 (@xivasudev owner)                    ║
╚══════════════════════════════════════════════════════════════╝
"""

import logging
import os
import sys

from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message

from config import Config
from core.forcejoin import force_join_check
from core.songqueue import queue_manager

logger = logging.getLogger(__name__)

_PREFIX = Config.PREFIX

# ── Filter helpers ─────────────────────────────────────────────────────────────

def sudo_filter(_, __, message: Message) -> bool:
    return bool(message.from_user and message.from_user.id in Config.SUDOERS)


def admin_filter(_, __, message: Message) -> bool:
    if not message.from_user:
        return False
    if message.from_user.id in Config.SUDOERS:
        return True
    return False   # will be extended per-handler via get_chat_member


sudo_only = filters.create(sudo_filter)


async def is_group_admin(client: Client, chat_id: int, user_id: int) -> bool:
    if user_id in Config.SUDOERS:
        return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}
    except Exception:
        return False


# ── !broadcast (sudo only) ─────────────────────────────────────────────────────
@Client.on_message(filters.command(["broadcast", "bc"], prefixes=_PREFIX) & sudo_only)
async def broadcast(client: Client, message: Message):
    """
    Broadcast a message to all active chats.
    Usage: !broadcast Your message here
    """
    if len(message.command) < 2:
        await message.reply_text("❓ Usage: `!broadcast <message>`")
        return

    text = " ".join(message.command[1:])
    active = queue_manager.active_chats()

    if not active:
        await message.reply_text("ℹ️ No active chats right now.")
        return

    sent, failed = 0, 0
    for chat_id in active:
        try:
            await client.send_message(chat_id, f"📢 **Broadcast from owner:**\n\n{text}")
            sent += 1
        except Exception as e:
            logger.warning("Broadcast failed for %s: %s", chat_id, e)
            failed += 1

    await message.reply_text(
        f"✅ **Broadcast complete!**\n"
        f"📤 Sent: `{sent}` | ❌ Failed: `{failed}`"
    )


# ── !stats (sudo only) ────────────────────────────────────────────────────────
@Client.on_message(filters.command(["stats", "status"], prefixes=_PREFIX) & sudo_only)
async def stats(client: Client, message: Message):
    """Show bot statistics."""
    import platform
    import psutil

    active = len(queue_manager.active_chats())
    py_ver = platform.python_version()

    try:
        cpu  = psutil.cpu_percent(interval=1)
        ram  = psutil.virtual_memory()
        ram_used = round(ram.used / 1024 / 1024)
        ram_total = round(ram.total / 1024 / 1024)
    except Exception:
        cpu, ram_used, ram_total = "N/A", "N/A", "N/A"

    me = await client.get_me()
    await message.reply_text(
        f"📊 **Bot Statistics**\n\n"
        f"🤖 Bot: @{me.username}\n"
        f"🎵 Active streams: `{active}`\n"
        f"🐍 Python: `{py_ver}`\n"
        f"💻 CPU usage: `{cpu}%`\n"
        f"🧠 RAM: `{ram_used} MB / {ram_total} MB`\n"
        f"👑 Owner: `{Config.SUDOERS}`\n"
        f"📢 Force-Join: `{Config.FORCE_JOIN_CHANNEL}`\n"
        f"🎚 Quality: `{Config.QUALITY}`\n"
        f"📹 Mode: `{Config.STREAM_MODE}`\n"
    )


# ── !update / !restart (sudo only) ────────────────────────────────────────────
@Client.on_message(filters.command(["update", "restart"], prefixes=_PREFIX) & sudo_only)
async def update_restart(client: Client, message: Message):
    """Pull latest git changes and restart the bot."""
    msg = await message.reply_text("🔄 Pulling updates from GitHub …")

    import subprocess
    result = subprocess.run(["git", "pull"], capture_output=True, text=True)
    output = result.stdout.strip() or result.stderr.strip() or "No output."

    await msg.edit_text(
        f"🔄 **Git Pull Output:**\n```\n{output[:1000]}\n```\n\n"
        "♻️ Restarting bot …"
    )
    os.execv(sys.executable, [sys.executable] + sys.argv)


# ── !ban / !unban (sudo only) ─────────────────────────────────────────────────
@Client.on_message(filters.command(["ban"], prefixes=_PREFIX) & sudo_only)
async def ban_user(client: Client, message: Message):
    """Ban a user from using the bot. Usage: !ban [reply or user_id]"""
    target = None
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            target_id = int(message.command[1])
            target = await client.get_users(target_id)
        except Exception:
            await message.reply_text("❌ Invalid user ID.")
            return

    if not target:
        await message.reply_text("❓ Reply to a user or provide their ID.")
        return

    if target.id in Config.SUDOERS:
        await message.reply_text("⚠️ You can't ban a sudo user!")
        return

    # Store banned users in a simple file
    with open("banned_users.txt", "a") as f:
        f.write(f"{target.id}\n")

    await message.reply_text(
        f"🚫 **Banned!**\n"
        f"User: {target.mention}\n"
        f"ID: `{target.id}`"
    )


# ── !unban (sudo only) ────────────────────────────────────────────────────────
@Client.on_message(filters.command(["unban"], prefixes=_PREFIX) & sudo_only)
async def unban_user(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("❓ Usage: `!unban <user_id>`")
        return
    try:
        uid = int(message.command[1])
    except ValueError:
        await message.reply_text("❌ Invalid ID.")
        return

    try:
        with open("banned_users.txt", "r") as f:
            lines = f.readlines()
        with open("banned_users.txt", "w") as f:
            f.writelines(l for l in lines if l.strip() != str(uid))
        await message.reply_text(f"✅ User `{uid}` unbanned.")
    except FileNotFoundError:
        await message.reply_text("ℹ️ No banned users on record.")


# ── !lang (group admin) ───────────────────────────────────────────────────────
SUPPORTED_LANGS = ["en", "hi", "ar", "bn", "cn", "de", "fr", "ja", "nl", "ru", "te", "tr"]

@Client.on_message(filters.command(["lang", "language"], prefixes=_PREFIX) & filters.group)
async def set_language(client: Client, message: Message):
    if not await force_join_check(client, message):
        return
    if not await is_group_admin(client, message.chat.id, message.from_user.id):
        await message.reply_text("⚠️ Only group admins can change the bot language.")
        return

    if len(message.command) < 2:
        langs = " | ".join(f"`{l}`" for l in SUPPORTED_LANGS)
        await message.reply_text(
            f"🗣 **Available Languages:**\n{langs}\n\n"
            f"Usage: `!lang en`  (current: `{Config.LANGUAGE}`)"
        )
        return

    lang = message.command[1].lower()
    if lang not in SUPPORTED_LANGS:
        await message.reply_text(f"❌ Unsupported language code: `{lang}`")
        return

    Config.LANGUAGE = lang
    await message.reply_text(f"✅ Language set to **{lang.upper()}**.")


# ── !admins (group admin) ─────────────────────────────────────────────────────
@Client.on_message(filters.command(["admins", "adminlist"], prefixes=_PREFIX) & filters.group)
async def list_admins(client: Client, message: Message):
    if not await force_join_check(client, message):
        return
    admins = []
    async for member in client.get_chat_members(message.chat.id, filter="administrators"):
        name = member.user.first_name if member.user else "Unknown"
        admins.append(f"• {name} (`{member.user.id}`)")

    await message.reply_text(
        f"👮 **Group Admins ({len(admins)}):**\n\n" + "\n".join(admins)
    )
