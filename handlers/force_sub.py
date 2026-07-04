from functools import wraps
from telethon import Button
import config
from utils.helpers import get_missing_channels

FORCE_SUB_TEXT = (
    "**🔒 Access Restricted**\n\n"
    "You must join our official channel(s) to use this bot.\n"
    "Join below then tap **I've Joined**."
)


def build_join_buttons(channels):
    rows = [[Button.url(f"📢 Join @{c}", f"https://t.me/{c}")] for c in channels]
    rows.append([Button.inline("✅ I've Joined", data="check_sub")])
    return rows


def force_sub(func):
    @wraps(func)
    async def wrapper(event, *args, **kwargs):
        client = event.client
        sender = await event.get_sender()
        if sender is None or sender.bot:
            return
        if not config.FORCE_SUB_CHANNELS:
            return await func(event, *args, **kwargs)
        missing = await get_missing_channels(client, sender.id)
        if missing:
            await event.reply(FORCE_SUB_TEXT, buttons=build_join_buttons(missing))
            return
        return await func(event, *args, **kwargs)

    return wrapper
