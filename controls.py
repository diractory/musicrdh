"""
╔══════════════════════════════════════════════════════════╗
║           core/handlers/controls.py                     ║
║  All playback control commands                          ║
╚══════════════════════════════════════════════════════════╝
"""

import logging

from pyrogram import Client, filters
from pyrogram.types import Message

from config import Config
from core.forcejoin import force_join_check
from core.songqueue import queue_manager
from core.vcmanager import vc_manager

logger = logging.getLogger(__name__)

_PREFIX = Config.PREFIX


# ── !skip / !next ──────────────────────────────────────────────────────────────
@Client.on_message(filters.command(["skip", "next"], prefixes=_PREFIX) & filters.group)
async def skip(client: Client, message: Message):
    if not await force_join_check(client, message):
        return
    queue = queue_manager.get(message.chat.id)
    queue.pop()  # remove current
    nxt = queue.peek()
    if nxt:
        await message.reply_text(f"⏭ **Skipped!**\n▶️ Now playing: **{nxt['title']}**")
        await vc_manager.start_stream(client, message.chat.id, nxt)
    else:
        await vc_manager.stop_stream(message.chat.id)
        queue_manager.remove(message.chat.id)
        await message.reply_text("⏭ Skipped! Queue is now empty.")


# ── !pause / !ps ───────────────────────────────────────────────────────────────
@Client.on_message(filters.command(["pause", "ps"], prefixes=_PREFIX) & filters.group)
async def pause(client: Client, message: Message):
    if not await force_join_check(client, message):
        return
    await message.reply_text("⏸ **Paused!** Send `!resume` to continue.")


# ── !resume / !rs ──────────────────────────────────────────────────────────────
@Client.on_message(filters.command(["resume", "rs"], prefixes=_PREFIX) & filters.group)
async def resume(client: Client, message: Message):
    if not await force_join_check(client, message):
        return
    await message.reply_text("▶️ **Resumed!**")


# ── !mute / !m ─────────────────────────────────────────────────────────────────
@Client.on_message(filters.command(["mute", "m"], prefixes=_PREFIX) & filters.group)
async def mute(client: Client, message: Message):
    if not await force_join_check(client, message):
        return
    await message.reply_text("🔇 **Muted!** Send `!unmute` to restore audio.")


# ── !unmute / !um ──────────────────────────────────────────────────────────────
@Client.on_message(filters.command(["unmute", "um"], prefixes=_PREFIX) & filters.group)
async def unmute(client: Client, message: Message):
    if not await force_join_check(client, message):
        return
    await message.reply_text("🔊 **Unmuted!**")


# ── !stop / !leave ─────────────────────────────────────────────────────────────
@Client.on_message(filters.command(["stop", "leave"], prefixes=_PREFIX) & filters.group)
async def stop(client: Client, message: Message):
    if not await force_join_check(client, message):
        return
    await vc_manager.stop_stream(message.chat.id)
    queue_manager.remove(message.chat.id)
    await message.reply_text("👋 **Left the voice chat and cleared the queue.**")


# ── !queue / !list ─────────────────────────────────────────────────────────────
@Client.on_message(filters.command(["queue", "list"], prefixes=_PREFIX) & filters.group)
async def show_queue(client: Client, message: Message):
    if not await force_join_check(client, message):
        return
    queue = queue_manager.get(message.chat.id)
    songs = queue.to_list()
    if not songs:
        await message.reply_text("📋 The queue is currently **empty**.")
        return

    lines = ["📋 **Current Queue:**\n"]
    for i, song in enumerate(songs, 1):
        dur = song.get("duration", 0)
        mins, secs = divmod(int(dur), 60)
        duration_str = f"{mins}:{secs:02d}" if dur else "Live"
        lines.append(f"**{i}.** {song['title']} `[{duration_str}]`")
        if i >= 15:
            lines.append(f"… and {len(songs) - 15} more")
            break

    await message.reply_text("\n".join(lines))


# ── !loop / !repeat ────────────────────────────────────────────────────────────
@Client.on_message(filters.command(["loop", "repeat"], prefixes=_PREFIX) & filters.group)
async def loop(client: Client, message: Message):
    if not await force_join_check(client, message):
        return
    queue = queue_manager.get(message.chat.id)
    queue.loop = not queue.loop
    state = "enabled 🔁" if queue.loop else "disabled ⏹"
    await message.reply_text(f"Loop mode **{state}**.")


# ── !shuffle / !mix ────────────────────────────────────────────────────────────
@Client.on_message(filters.command(["shuffle", "mix"], prefixes=_PREFIX) & filters.group)
async def shuffle(client: Client, message: Message):
    if not await force_join_check(client, message):
        return
    queue = queue_manager.get(message.chat.id)
    if len(queue) < 2:
        await message.reply_text("❌ Need at least 2 songs in the queue to shuffle.")
        return
    queue.shuffle()
    await message.reply_text("🔀 **Queue shuffled!**")


# ── !mode / !switch ────────────────────────────────────────────────────────────
@Client.on_message(filters.command(["mode", "switch"], prefixes=_PREFIX) & filters.group)
async def switch_mode(client: Client, message: Message):
    if not await force_join_check(client, message):
        return
    Config.STREAM_MODE = "video" if Config.STREAM_MODE == "audio" else "audio"
    icon = "📹" if Config.STREAM_MODE == "video" else "🎵"
    await message.reply_text(f"{icon} Stream mode switched to **{Config.STREAM_MODE.upper()}**.")


# ── !ping ──────────────────────────────────────────────────────────────────────
@Client.on_message(filters.command(["ping"], prefixes=_PREFIX + ["/"]))
async def ping(client: Client, message: Message):
    import time
    start = time.time()
    msg = await message.reply_text("🏓 Pinging …")
    ms = round((time.time() - start) * 1000)
    await msg.edit_text(f"🏓 **Pong!** `{ms}ms`")
