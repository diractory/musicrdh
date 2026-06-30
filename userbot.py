"""
╔══════════════════════════════════════════════════════════════╗
║                  core/userbot.py                            ║
║   Pyrogram USER-account client for voice-chat streaming     ║
║   This is YOUR Telegram account, not the bot account.       ║
╚══════════════════════════════════════════════════════════════╝
"""

import logging

from pyrogram import Client
from config import Config

logger = logging.getLogger(__name__)


class UserBot(Client):
    """
    Pyrogram client running as a *user account*.
    Required by Telegram to join and stream inside voice chats.
    The SESSION env var holds the Pyrogram string session.
    """

    def __init__(self):
        super().__init__(
            name="XivaSudevUserBot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            session_string=Config.SESSION,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        logger.info(
            "✅  UserBot connected: %s (id=%s)", me.first_name, me.id
        )
        return self
