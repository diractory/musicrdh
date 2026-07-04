from telethon import events
from telethon.tl.types import DocumentAttributeAudio
import config
from handlers.force_sub import force_sub
from utils.downloader import search_and_download_audio, cleanup
from utils.helpers import format_duration


def register(bot):
    @bot.on(events.NewMessage(pattern=r"^/song(@\w+)?(\s+.+)?$"))
    @force_sub
    async def song_handler(event):
        query = (event.pattern_match.group(2) or "").strip()
        if not query:
            await event.reply(f"**Usage:** `/song <song name or spotify link>`{config.CREDIT_TEXT}")
            return

        status = await event.reply(f"🔎 **Searching:** `{query}`")
        try:
            result = await search_and_download_audio(query)
        except Exception as e:
            err = str(e).split("\n")[0][:150]
            await status.edit(f"❌ **Download failed**\n`{err}`{config.CREDIT_TEXT}")
            return

        await status.edit("⬆️ **Uploading...**")
        caption = (
            f"🎵 **{result['title']}**\n"
            f"👤 **{result['uploader']}**\n"
            f"⏱ **{format_duration(result['duration'])}**"
            f"{config.CREDIT_TEXT}"
        )

        try:
            thumb = result.get("thumb")
            await bot.send_file(
                event.chat_id,
                result["path"],
                thumb=thumb if thumb else None,
                caption=caption,
                reply_to=event.message.id,
                attributes=[
                    DocumentAttributeAudio(
                        duration=result["duration"],
                        title=result["title"],
                        performer=result["uploader"],
                    )
                ],
            )
        finally:
            cleanup(result["path"], result.get("thumb"))
            try:
                await status.delete()
            except Exception:
                pass
