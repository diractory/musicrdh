import re
from telethon import events
import config
from handlers.force_sub import force_sub
from utils.downloader import download_instagram, cleanup
from utils.helpers import extract_instagram_link

def register(bot):
    @bot.on(events.NewMessage(func=lambda e: bool(extract_instagram_link(e.raw_text))))
    @force_sub
    async def instagram_handler(event):
        link = extract_instagram_link(event.raw_text)
        status = await event.reply("⬇️ **Downloading from Instagram...**")
        try:
            result = await download_instagram(link)
        except Exception as e:
            err_short = str(e).split("\n")[0][:120]
            await status.edit(
                f"❌ **Instagram download failed**\n`{err_short}`"
                f"{config.CREDIT_TEXT}"
            )
            return
        await status.edit("⬆️ **Uploading...**")
        caption = f"**{result['title']}**\n\n**Dev ~ #rdh**{config.CREDIT_TEXT}"
        try:
            await bot.send_file(
                event.chat_id,
                result["path"],
                caption=caption,
                reply_to=event.message.id,
            )
        finally:
            cleanup(result["path"])
            try:
                await status.delete()
            except Exception:
                pass
