"""
╔══════════════════════════════════════════════════════════╗
║            core/handlers/start.py                       ║
║  /start and /help command handlers                      ║
╚══════════════════════════════════════════════════════════╝
"""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import Config
from core.forcejoin import force_join_check

START_TEXT = """
🎵 **Welcome to XivaSudev Music Bot!** 🎵

I'm a powerful music streaming bot for Telegram voice chats.

**Quick Commands:**
• `!play [song/link]` — Play a song
• `!radio [url]` — Stream a live radio
• `!playlist [yt link]` — Play a YouTube playlist
• `!queue` — Show current queue
• `!skip` — Skip to next song
• `!pause` / `!resume` — Pause / resume
• `!stop` — Stop and leave VC
• `!help` — Full command list

Join **@xivasudev** for updates and support!
"""

HELP_TEXT = """
🎵 **XivaSudev Music Bot — Commands** 🎵

**▶️ Playback**
• `!play` / `!p [song or URL]` — Play / add to queue
• `!radio` / `!stream [URL]` — Play a live stream
• `!playlist` / `!pl [playlist URL]` — Play whole YT playlist
• `!skip` / `!next` — Skip current song
• `!stop` / `!leave` — Stop and leave voice chat

**⏯ Controls**
• `!pause` / `!ps` — Pause stream
• `!resume` / `!rs` — Resume stream
• `!mute` / `!m` — Mute
• `!unmute` / `!um` — Unmute
• `!loop` / `!repeat` — Toggle loop mode
• `!shuffle` / `!mix` — Shuffle queue

**📋 Queue**
• `!queue` / `!list` — Show song queue
• `!export` / `!ep` — Export queue to file
• `!import` / `!ip` — Import queue from file

**⚙️ Settings (Admin)**
• `!mode` / `!switch` — Toggle audio/video mode
• `!lang [code]` — Change bot language
• `!update` / `!restart` — Update and restart bot

**🔧 Misc**
• `!ping` — Check bot latency
• `!start` / `!help` — Show this message
"""


@Client.on_message(filters.command(["start", "help"], prefixes=Config.PREFIX + ["/"]))
async def start_help(client: Client, message: Message):
    if not await force_join_check(client, message):
        return

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📢 Channel", url="https://t.me/xivasudev"),
            InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{(await client.get_me()).username}?startgroup=true"),
        ],
        [
            InlineKeyboardButton("❓ Help", callback_data="help_menu"),
        ]
    ])

    cmd = message.command[0].lower()
    text = HELP_TEXT if cmd == "help" else START_TEXT

    await message.reply_text(text, reply_markup=keyboard, disable_web_page_preview=True)


@Client.on_callback_query(filters.regex("^help_menu$"))
async def help_callback(client, callback_query):
    await callback_query.message.edit_text(HELP_TEXT, disable_web_page_preview=True)
    await callback_query.answer()


@Client.on_callback_query(filters.regex("^check_join$"))
async def check_join_callback(client, callback_query):
    """Called when user taps 'I Joined — Try Again' button."""
    user_id = callback_query.from_user.id
    from core.forcejoin import is_subscribed
    joined = await is_subscribed(client, user_id)
    if joined:
        await callback_query.message.edit_text(
            "✅ **Verified!**\n\nWelcome! You can now use the music bot.\nSend `!help` to get started."
        )
    else:
        await callback_query.answer(
            "❌ You haven't joined yet! Please join @xivasudev first.",
            show_alert=True,
        )
