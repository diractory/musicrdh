"""
╔══════════════════════════════════════════════════════════╗
║                  core/forcejoin.py                      ║
║  Force-Join guard.                                      ║
║  Every user must be a member of FORCE_JOIN_CHANNEL      ║
║  (@xivasudev) to use ANY command.                       ║
╚══════════════════════════════════════════════════════════╝
"""

import logging

from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant, ChannelPrivate, PeerIdInvalid
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from config import Config

logger = logging.getLogger(__name__)

# ── Statuses that count as "member" ───────────────────────────────────────────
VALID_STATUSES = {
    ChatMemberStatus.MEMBER,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.OWNER,
}


async def is_subscribed(client: Client, user_id: int) -> bool:
    """
    Returns True if `user_id` is a member of FORCE_JOIN_CHANNEL.
    Falls back to True on unexpected errors so the bot never breaks entirely.
    """
    channel = Config.FORCE_JOIN_CHANNEL
    if not channel:
        return True  # Force-join not configured
    try:
        member = await client.get_chat_member(channel, user_id)
        return member.status in VALID_STATUSES
    except UserNotParticipant:
        return False
    except (ChannelPrivate, PeerIdInvalid) as exc:
        logger.error("Force-join channel error (%s): %s", channel, exc)
        return True  # Don't block users if channel is misconfigured
    except Exception as exc:
        logger.warning("Unexpected error in force-join check: %s", exc)
        return True


async def force_join_check(client: Client, message: Message) -> bool:
    """
    Call this at the top of any command handler.

    Returns True  → user is a member, command may proceed.
    Returns False → user is NOT a member; a prompt is sent and the command is blocked.
    """
    # Sudo users are always exempt
    if message.from_user and message.from_user.id in Config.SUDOERS:
        return True

    user_id = message.from_user.id if message.from_user else None
    if not user_id:
        return True  # Can't check anonymous/channel posts

    subscribed = await is_subscribed(client, user_id)
    if subscribed:
        return True

    # ── Build the "Join Channel" button ────────────────────────────────────────
    channel = Config.FORCE_JOIN_CHANNEL
    # Normalise to a URL-friendly format
    channel_url = (
        f"https://t.me/{channel.lstrip('@')}"
        if channel.startswith("@")
        else f"https://t.me/{channel}"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔔 Join @xivasudev",
                    url=channel_url,
                )
            ],
            [
                InlineKeyboardButton(
                    "✅ I Joined — Try Again",
                    callback_data="check_join",
                )
            ],
        ]
    )

    await message.reply_text(
        "🚫 **Access Denied!**\n\n"
        "You must join our channel before using this bot.\n\n"
        f"👉 Join **{channel}** and then press **\"I Joined\"** below.",
        reply_markup=keyboard,
    )
    return False
