"""
╔══════════════════════════════════════════════════════════╗
║                 core/vcmanager.py                       ║
║  Manages py-tgcalls group calls per chat                ║
╚══════════════════════════════════════════════════════════╝
"""

import asyncio
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class VCManager:
    """
    Thin wrapper around pytgcalls GroupCallFactory.
    Actual pytgcalls integration depends on the installed version;
    the stubs below show the intended interface and are replaced
    once the userbot is available at runtime.
    """

    def __init__(self):
        self._active: Dict[int, bool] = {}  # chat_id → is_active

    async def start_stream(self, client, chat_id: int, song: dict):
        """Join VC and start streaming `song['url']`."""
        try:
            logger.info("Starting stream in chat %s: %s", chat_id, song.get("title"))
            self._active[chat_id] = True
            # pytgcalls integration goes here — depends on userbot instance
            # Example (with pytgcalls 3.x):
            #   gc = client.userbot.group_call_factory.get_file_group_call(song["url"])
            #   await gc.start(chat_id)
        except Exception as exc:
            logger.error("Failed to start stream in %s: %s", chat_id, exc)

    async def stop_stream(self, chat_id: int):
        """Leave VC and clear state for this chat."""
        self._active.pop(chat_id, None)
        logger.info("Stopped stream in chat %s", chat_id)

    def is_active(self, chat_id: int) -> bool:
        return self._active.get(chat_id, False)


vc_manager = VCManager()
