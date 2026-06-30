"""
╔══════════════════════════════════════════════════════════╗
║            core/handlers/play.py                        ║
║  !play, !radio, !playlist command handlers              ║
╚══════════════════════════════════════════════════════════╝
"""

import logging

from pyrogram import Client, filters
from pyrogram.types import Message

from config import Config
from core.forcejoin import force_join_check
from core.songqueue import queue_manager
from core.stream import get_stream_info, get_playlist_tracks, _is_youtube_playlist
from core.vcmanager import vc_manager

logger = logging.getLogger(__name__)


def _is_admin(member) -> bool:
    from pyrogram.enums import ChatMemberStatus
    return member.status in {
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER,
    }


async def check_admin_if_required(client: Client, message: Message) -> bool:
    """If ADMINS_ONLY is True, only group admins can use !play."""
    if not Config.ADMINS_ONLY:
        return True
    if message.from_user.id in Config.SUDOERS:
        return True
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if _is_admin(member):
        return True
    await message.reply_text("⚠️ Only group admins can use play commands.")
    return False


# ── !play / !p ─────────────────────────────────────────────────────────────────
@Client.on_message(filters.command(["play", "p"], prefixes=Config.PREFIX) & filters.group)
async def play_command(client: Client, message: Message):
    if not await force_join_check(client, message):
        return
    if not await check_admin_if_required(client, message):
        return

    if len(message.command) < 2:
        await message.reply_text("❓ Usage: `!play [song name or YouTube URL]`")
        return

    query = " ".join(message.command[1:])
    msg = await message.reply_text(f"🔍 Searching for **{query}** …")

    info = await get_stream_info(query, mode=Config.STREAM_MODE)
    if not info:
        await msg.edit_text("❌ Could not find the song. Try a different query.")
        return

    queue = queue_manager.get(message.chat.id)
    queue.add({**info, "requested_by": message.from_user.mention})

    if len(queue) == 1:
        # First song — start streaming
        await msg.edit_text(f"▶️ **Now Playing:**\n🎵 {info['title']}\n👤 {info['uploader']}\n⏱ Requested by {message.from_user.mention}")
        await vc_manager.start_stream(client, message.chat.id, info)
    else:
        pos = len(queue)
        await msg.edit_text(
            f"✅ **Added to Queue** [#{pos}]\n🎵 {info['title']}\n👤 {info['uploader']}"
        )


# ── !radio / !stream ───────────────────────────────────────────────────────────
@Client.on_message(filters.command(["radio", "stream"], prefixes=Config.PREFIX) & filters.group)
async def radio_command(client: Client, message: Message):
    if not await force_join_check(client, message):
        return

    if len(message.command) < 2:
        await message.reply_text("❓ Usage: `!radio [stream URL or radio link]`")
        return

    url = message.command[1]
    msg = await message.reply_text(f"📻 Loading live stream …")

    info = await get_stream_info(url, mode="audio")
    if not info:
        # treat raw URL as a direct stream
        info = {"title": "Live Stream", "url": url, "is_live": True, "duration": 0, "thumbnail": "", "webpage_url": url, "uploader": "Live"}

    info["is_live"] = True
    queue = queue_manager.get(message.chat.id)
    queue.add({**info, "requested_by": message.from_user.mention})

    if len(queue) == 1:
        await msg.edit_text(f"📻 **Now Streaming:**\n🎙 {info['title']}\nRequested by {message.from_user.mention}")
        await vc_manager.start_stream(client, message.chat.id, info)
    else:
        await msg.edit_text(f"✅ **Live stream added to queue** [#{len(queue)}]\n🎙 {info['title']}")


# ── !playlist / !pl ────────────────────────────────────────────────────────────
@Client.on_message(filters.command(["playlist", "pl"], prefixes=Config.PREFIX) & filters.group)
async def playlist_command(client: Client, message: Message):
    if not await force_join_check(client, message):
        return

    if len(message.command) < 2:
        await message.reply_text("❓ Usage: `!playlist [YouTube playlist URL]`")
        return

    url = message.command[1]
    if not _is_youtube_playlist(url):
        await message.reply_text("❌ Please provide a valid YouTube playlist URL.")
        return

    msg = await message.reply_text("📂 Loading playlist …")
    tracks = await get_playlist_tracks(url)

    if not tracks:
        await msg.edit_text("❌ Could not load the playlist.")
        return

    if len(tracks) > Config.MAX_QUEUE_SIZE:
        tracks = tracks[:Config.MAX_QUEUE_SIZE]

    queue = queue_manager.get(message.chat.id)
    was_empty = len(queue) == 0

    for track in tracks:
        queue.add({**track, "requested_by": message.from_user.mention})

    await msg.edit_text(
        f"✅ **Playlist Loaded!**\n"
        f"📂 Added **{len(tracks)}** tracks to queue.\n"
        f"Requested by {message.from_user.mention}"
    )

    if was_empty and queue.peek():
        first = queue.peek()
        await vc_manager.start_stream(client, message.chat.id, first)
