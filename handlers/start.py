from telethon import events, Button
import config
import database
import state
from handlers.force_sub import force_sub, build_join_buttons
from utils.helpers import get_missing_channels

START_TEXT = (
    "**👋 Hey {name}!**\n\n"
    "I'm **Radhey Music Bot** — play music in VC, download songs, "
    "and grab Instagram reels just by sending a link.\n\n"
    "📌 Use /help to see all commands."
    "{credit}"
)

HELP_TEXT = (
    "**📖 All Commands**\n\n"
    "**🎵 Voice Chat (groups)**\n"
    "• `/play <song>` — join VC and stream\n"
    "• `/skip` — skip to next in queue\n"
    "• `/pause` — pause stream\n"
    "• `/resume` — resume stream\n"
    "• `/mute` — mute assistant in VC\n"
    "• `/unmute` — unmute assistant\n"
    "• `/stop` — stop and leave VC\n"
    "• `/queue` — show queue\n\n"
    "**🎧 Song Download**\n"
    "• `/song <name>` — get song as audio file (DM or group)\n\n"
    "**📸 Instagram**\n"
    "• Just send any Instagram reel/post link — I'll download it!\n\n"
    "**👑 Owner/Admin**\n"
    "• `/ban` — ban user (reply or @username)\n"
    "• `/unban` — unban user\n"
    "• `/kick` — kick user from group\n"
    "• `/banlist` — list all banned users\n"
    "• `/broadcast` — broadcast a message to all users\n"
    "• `/stats` — bot statistics\n\n"
    "**Misc**\n"
    "• `/ping` — check bot response time"
    "{credit}"
)


def register(bot):
    @bot.on(events.NewMessage(pattern=r"^/start(@\w+)?$"))
    async def start_handler(event):
        sender = await event.get_sender()
        database.add_user(sender.id, sender.first_name or "", sender.username or "")
        if event.is_group:
            chat = await event.get_chat()
            database.add_chat(chat.id, getattr(chat, "title", ""))
        missing = await get_missing_channels(bot, sender.id)
        if missing:
            from handlers.force_sub import FORCE_SUB_TEXT
            await event.reply(FORCE_SUB_TEXT, buttons=build_join_buttons(missing))
            return
        buttons = None
        if state.ASSISTANT_USERNAME:
            buttons = [
                [Button.url("➕ Add Assistant to Group", f"https://t.me/{state.ASSISTANT_USERNAME}?startgroup=true")],
                [Button.url("📢 Updates Channel", f"https://t.me/{config.CHANNEL_USERNAME}")],
            ]
        await event.reply(
            START_TEXT.format(name=sender.first_name or "there", credit=config.CREDIT_TEXT),
            buttons=buttons,
        )

    @bot.on(events.CallbackQuery(data=b"check_sub"))
    async def check_sub_callback(event):
        missing = await get_missing_channels(bot, event.sender_id)
        if missing:
            await event.answer("You still haven't joined all required channels.", alert=True)
            return
        await event.answer("✅ Access granted! Send /start again.", alert=True)
        try:
            await event.delete()
        except Exception:
            pass

    @bot.on(events.NewMessage(pattern=r"^/help(@\w+)?$"))
    @force_sub
    async def help_handler(event):
        await event.reply(HELP_TEXT.format(credit=config.CREDIT_TEXT))

    @bot.on(events.NewMessage(pattern=r"^/ping(@\w+)?$"))
    async def ping_handler(event):
        import time
        start = time.monotonic()
        msg = await event.reply("🏓 Pinging...")
        taken = (time.monotonic() - start) * 1000
        await msg.edit(f"**🏓 Pong!** `{taken:.2f} ms`{config.CREDIT_TEXT}")
