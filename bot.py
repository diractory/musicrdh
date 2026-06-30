"""
╔══════════════════════════════════════════════════════════════╗
║                    core/bot.py                              ║
║   Main Pyrogram Bot client                                  ║
║   Auto-loads all plugin handlers from core/handlers/        ║
║   Force-Join @xivasudev enforced on every command           ║
╚══════════════════════════════════════════════════════════════╝
"""

import logging

from pyrogram import Client
from config import Config

logger = logging.getLogger(__name__)


class MusicBot(Client):
    """
    Pyrogram Client running as a BOT (uses BOT_TOKEN).
    All command handlers live in core/handlers/ and are
    auto-loaded by Pyrogram's plugins system.
    """

    def __init__(self, userbot):
        self.userbot = userbot

        super().__init__(
            name="XivaSudevMusicBot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(root="core/handlers"),
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        logger.info("✅  MusicBot started: @%s (id=%s)", me.username, me.id)
        return self
