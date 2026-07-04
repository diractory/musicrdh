from telethon import events
import config
import state
from handlers.force_sub import force_sub
from utils.downloader import search_and_download_audio, cleanup
from utils.helpers import format_duration, is_group_admin

VC_DISABLED_TEXT = (
    "**⚠️ Voice chat streaming is not configured.**\n"
    "The bot owner needs to set `SESSION_STRING` (see `genstring.py`)."
    f"{config.CREDIT_TEXT}"
)


async def admin_only_gate(event) -> bool:
    if event.sender_id in config.SUDOERS:
        return True
    if await is_group_admin(event):
        return True
    await event.reply(f"**🚫 Only group admins can use this command.**{config.CREDIT_TEXT}")
    return False


def register(bot):
    from vc import calls

    @bot.on(events.NewMessage(pattern=r"^/play(@\w+)?(\s+.+)?$"))
    @force_sub
    async def play_handler(event):
        if not config.VC_ENABLED:
            await event.reply(VC_DISABLED_TEXT)
            return
        if not event.is_group:
            await event.reply(f"**This command works in groups only.**{config.CREDIT_TEXT}")
            return
        if not state.ASSISTANT_USERNAME:
            await event.reply(f"**Assistant is not ready yet, try again shortly.**{config.CREDIT_TEXT}")
            return
        query = (event.pattern_match.group(2) or "").strip()
        if not query:
            await event.reply(f"**Usage:** `/play <song name>`{config.CREDIT_TEXT}")
            return
        status = await event.reply(f"🔎 **Searching for** `{query}` **...**")
        try:
            result = await search_and_download_audio(query)
        except Exception:
            await status.edit(f"❌ **Couldn't find or download that track.**{config.CREDIT_TEXT}")
            return
        song = {
            "path": result["path"],
            "title": result["title"],
            "duration": result["duration"],
            "requested_by": (await event.get_sender()).first_name,
        }
        try:
            state_result, position = await calls.play_or_queue(event.chat_id, song)
        except Exception:
            cleanup(result["path"])
            await status.edit(
                "❌ **Couldn't join the voice chat.**\n"
                "Make sure the assistant account is added to this group and a voice chat is available:\n"
                f"https://t.me/{state.ASSISTANT_USERNAME}?startgroup=true"
                f"{config.CREDIT_TEXT}"
            )
            return
        if state_result == "playing":
            await status.edit(
                f"▶️ **Now Playing:** {result['title']}\n"
                f"⏱ {format_duration(result['duration'])}"
                f"{config.CREDIT_TEXT}"
            )
        else:
            await status.edit(
                f"➕ **Queued at position {position}:** {result['title']}{config.CREDIT_TEXT}"
            )

    @bot.on(events.NewMessage(pattern=r"^/skip(@\w+)?$"))
    @force_sub
    async def skip_handler(event):
        if not config.VC_ENABLED or not event.is_group:
            return
        if not await admin_only_gate(event):
            return
        song = await calls.skip_track(event.chat_id)
        if song:
            await event.reply(f"⏭ **Now Playing:** {song['title']}{config.CREDIT_TEXT}")
        else:
            await event.reply(f"**Queue empty, left the voice chat.**{config.CREDIT_TEXT}")

    @bot.on(events.NewMessage(pattern=r"^/stop(@\w+)?$"))
    @force_sub
    async def stop_handler(event):
        if not config.VC_ENABLED or not event.is_group:
            return
        if not await admin_only_gate(event):
            return
        await calls.stop_playback(event.chat_id)
        await event.reply(f"⏹ **Stopped and left the voice chat.**{config.CREDIT_TEXT}")

    @bot.on(events.NewMessage(pattern=r"^/pause(@\w+)?$"))
    @force_sub
    async def pause_handler(event):
        if not config.VC_ENABLED or not event.is_group:
            return
        if not await admin_only_gate(event):
            return
        await calls.pause_playback(event.chat_id)
        await event.reply(f"⏸ **Paused.**{config.CREDIT_TEXT}")

    @bot.on(events.NewMessage(pattern=r"^/resume(@\w+)?$"))
    @force_sub
    async def resume_handler(event):
        if not config.VC_ENABLED or not event.is_group:
            return
        if not await admin_only_gate(event):
            return
        await calls.resume_playback(event.chat_id)
        await event.reply(f"▶️ **Resumed.**{config.CREDIT_TEXT}")

    @bot.on(events.NewMessage(pattern=r"^/mute(@\w+)?$"))
    @force_sub
    async def mute_handler(event):
        if not config.VC_ENABLED or not event.is_group:
            return
        if not await admin_only_gate(event):
            return
        await calls.mute_playback(event.chat_id)
        await event.reply(f"🔇 **Muted.**{config.CREDIT_TEXT}")

    @bot.on(events.NewMessage(pattern=r"^/unmute(@\w+)?$"))
    @force_sub
    async def unmute_handler(event):
        if not config.VC_ENABLED or not event.is_group:
            return
        if not await admin_only_gate(event):
            return
        await calls.unmute_playback(event.chat_id)
        await event.reply(f"🔊 **Unmuted.**{config.CREDIT_TEXT}")

    @bot.on(events.NewMessage(pattern=r"^/queue(@\w+)?$"))
    @force_sub
    async def queue_handler(event):
        if not config.VC_ENABLED or not event.is_group:
            return
        queue = calls.get_queue(event.chat_id)
        if not queue:
            await event.reply(f"**Queue is empty.**{config.CREDIT_TEXT}")
            return
        lines = [f"{i+1}. {s['title']}" for i, s in enumerate(queue)]
        await event.reply("**📋 Queue:**\n" + "\n".join(lines) + config.CREDIT_TEXT)
