"""
╔══════════════════════════════════════════════════════════════╗
║              🎵 config.py — XivaSudev Music Bot 🎵          ║
║         All settings loaded from environment / .env         ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
from typing import List

from dotenv import load_dotenv

load_dotenv()


class Config:
    # ── Telegram API ───────────────────────────────────────────────────────────
    API_ID: int    = int(os.environ.get("API_ID", 38165687))
    API_HASH: str  = os.environ.get("API_HASH", "1d6adcf8aed67d7f981d8e6089030158")

    # ── Bot Token ──────────────────────────────────────────────────────────────
    BOT_TOKEN: str = os.environ.get("BOT_TOKEN", "8852307164:AAHB1My-Q3KKzPDl2Dr44LoUStXhHJkNqXw")

    # ── User Session (Pyrogram String Session) ─────────────────────────────────
    SESSION: str   = os.environ.get("SESSION", "")

    # ── Owner / Sudo Users ─────────────────────────────────────────────────────
    SUDOERS: List[int] = [
        int(x)
        for x in os.environ.get("SUDOERS", "8192070400").split()
        if x.isdigit()
    ]

    # ── Force-Join ─────────────────────────────────────────────────────────────
    FORCE_JOIN_CHANNEL: str = os.environ.get("FORCE_JOIN_CHANNEL", "@xivasudev")

    # ── Stream ─────────────────────────────────────────────────────────────────
    QUALITY: str      = os.environ.get("QUALITY", "high")
    STREAM_MODE: str  = os.environ.get("STREAM_MODE", "audio")
    ADMINS_ONLY: bool = os.environ.get("ADMINS_ONLY", "False").lower() == "true"

    # ── Prefix & Language ──────────────────────────────────────────────────────
    PREFIX: List[str] = os.environ.get("PREFIX", "! /").split()
    LANGUAGE: str     = os.environ.get("LANGUAGE", "en")

    # ── Queue ──────────────────────────────────────────────────────────────────
    MAX_QUEUE_SIZE: int = int(os.environ.get("MAX_QUEUE_SIZE", 20))

    # ── Keep-Alive / Render ────────────────────────────────────────────────────
    RENDER_APP_URL: str = os.environ.get("RENDER_APP_URL", "").rstrip("/")
    PORT: int           = int(os.environ.get("PORT", 8080))

    # ── Spotify (optional) ────────────────────────────────────────────────────
    SPOTIFY_CLIENT_ID: str     = os.environ.get("SPOTIFY_CLIENT_ID", "")
    SPOTIFY_CLIENT_SECRET: str = os.environ.get("SPOTIFY_CLIENT_SECRET", "")

    # ── Bot personality ────────────────────────────────────────────────────────
    BOT_NAME: str    = "XivaSudev Music Bot"
    CHANNEL_URL: str = "https://t.me/xivasudev"
    CHANNEL_TAG: str = "@xivasudev"
