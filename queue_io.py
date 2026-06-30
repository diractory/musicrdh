"""
╔══════════════════════════════════════════════════════════════╗
║           core/handlers/queue_io.py                         ║
║   !export and !import queue to/from a JSON file             ║
╚══════════════════════════════════════════════════════════════╝
"""

import json
import logging
import os
import tempfile

from pyrogram import Client, filters
from pyrogram.types import Message

from config import Config
from core.forcejoin import force_join_check
from core.songqueue import queue_manager

logger = logging.getLogger(__name__)
_PREFIX = Config.PREFIX


# ── !export / !ep ──────────────────────────────────────────────────────────────
@Client.on_message(filters.command(["export", "ep"], prefixes=_PREFIX) & filters.group)
async def export_queue(client: Client, message: Message):
    if not await force_join_check(client, message):
        return

    queue = queue_manager.get(message.chat.id)
    songs = queue.to_list()

    if not songs:
        await message.reply_text("📋 Queue is empty — nothing to export.")
        return

    data = {"chat_id": message.chat.id, "songs": songs, "loop": queue.loop}
    json_str = json.dumps(data, indent=2, ensure_ascii=False)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", prefix="queue_", delete=False, encoding="utf-8"
    ) as f:
        f.write(json_str)
        tmp_path = f.name

    try:
        await message.reply_document(
            document=tmp_path,
            caption=(
                f"📤 **Queue Exported!**\n"
                f"🎵 `{len(songs)}` songs saved.\n"
                f"Send this file back with `!import` to restore the queue."
            ),
        )
    finally:
        os.unlink(tmp_path)


# ── !import / !ip ──────────────────────────────────────────────────────────────
@Client.on_message(filters.command(["import", "ip"], prefixes=_PREFIX) & filters.group)
async def import_queue(client: Client, message: Message):
    if not await force_join_check(client, message):
        return

    reply = message.reply_to_message
    if not reply or not reply.document:
        await message.reply_text(
            "❓ Reply to a JSON queue file (exported via `!export`) to import it."
        )
        return

    if not reply.document.file_name.endswith(".json"):
        await message.reply_text("❌ Invalid file type. Only `.json` files are accepted.")
        return

    msg = await message.reply_text("📥 Importing queue …")
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        tmp_path = f.name

    try:
        await client.download_media(reply, file_name=tmp_path)
        with open(tmp_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        songs = data.get("songs", [])
        if not songs:
            await msg.edit_text("❌ The file contains no songs.")
            return

        queue = queue_manager.get(message.chat.id)
        queue.clear()
        for song in songs:
            queue.add(song)
        queue.loop = data.get("loop", False)

        await msg.edit_text(
            f"✅ **Queue Imported!**\n"
            f"🎵 `{len(songs)}` songs loaded.\n"
            f"Use `!play` to start streaming, or `!queue` to see the list."
        )
    except (json.JSONDecodeError, KeyError) as e:
        await msg.edit_text(f"❌ Failed to parse the file: `{e}`")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
