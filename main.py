"""
╔══════════════════════════════════════════════════════════════════╗
║            🎵  XIVASUDEV MUSIC BOT  🎵                         ║
║                                                                  ║
║   Framework : AsmSafone/MusicPlayer                             ║
║   Owner     : @xivasudev  (ID: 8192070400)                      ║
║   Force-Join: @xivasudev                                        ║
║   Hosting   : Render.com  (Flask self-ping — no UptimeRobot)    ║
║                                                                  ║
║   Credits   : @AsmSafone / @sayradhey / @slocas                 ║
╚══════════════════════════════════════════════════════════════════╝
"""

import asyncio
import logging
import os
import sys

# ── Ensure an event loop exists in the main thread BEFORE anything else runs ──
# Fixes: RuntimeError: There is no current event loop in thread 'MainThread'
# (happens on Python 3.10+ where asyncio.get_event_loop() no longer
#  auto-creates a loop if one doesn't already exist)
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

from pyrogram import idle

from config import Config
from keepalive import keep_alive

# ── Logging ────────────────────────────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
os.makedirs("downloads", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s » %(message)s",
    datefmt="%d-%b-%Y %H:%M:%S",
    handlers=[
        logging.FileHandler("logs/musicbot.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("XivaSudevMusicBot")
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("pytgcalls").setLevel(logging.WARNING)

BANNER = """
╔══════════════════════════════════════════════════════════╗
║         🎵  XivaSudev Music Bot  Booting...  🎵          ║
║              Force-Join : @xivasudev                     ║
║              Owner ID   : 8192070400                     ║
╚══════════════════════════════════════════════════════════╝
"""


async def main():
    print(BANNER)

    # ── Pre-flight checks ──────────────────────────────────────────────────────
    if not Config.API_ID or not Config.API_HASH:
        logger.critical("❌  API_ID / API_HASH missing — check your .env file!")
        sys.exit(1)
    if not Config.SESSION:
        logger.critical(
            "❌  SESSION string is empty!\n"
            "   Generate one by running:  python3 genStr.py\n"
            "   Then paste it into your .env / Render environment variables."
        )
        sys.exit(1)

    # ── Start Flask keep-alive (self-ping, no UptimeRobot needed) ─────────────
    keep_alive()

    # ── Import clients after keep-alive ───────────────────────────────────────
    from core.userbot import UserBot
    from core.bot import MusicBot

    userbot = UserBot()
    await userbot.start()
    logger.info("✅  Userbot  : %s", (await userbot.get_me()).first_name)

    bot = MusicBot(userbot)
    await bot.start()
    bot_me = await bot.get_me()
    logger.info("✅  Music Bot: @%s", bot_me.username)

    logger.info("━" * 58)
    logger.info("🎵  Bot is LIVE!  Force-Join channel → @xivasudev")
    logger.info("━" * 58)

    await idle()

    await bot.stop()
    await userbot.stop()
    logger.info("👋  Bot stopped gracefully.")


if __name__ == "__main__":
    asyncio.run(main())
