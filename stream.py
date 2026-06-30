"""
╔══════════════════════════════════════════════════════════╗
║                  core/stream.py                         ║
║  Download / extract stream URLs via yt-dlp              ║
╚══════════════════════════════════════════════════════════╝
"""

import asyncio
import logging
import os
import re
from typing import Optional, Tuple

import yt_dlp

from config import Config

logger = logging.getLogger(__name__)

# ── Quality presets ────────────────────────────────────────────────────────────
QUALITY_MAP = {
    "high":   "bestaudio/best",
    "medium": "bestaudio[abr<=128]/best",
    "low":    "bestaudio[abr<=64]/best",
}

YDL_OPTS_AUDIO = {
    "format": QUALITY_MAP.get(Config.QUALITY, "bestaudio/best"),
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "geo_bypass": True,
    "nocheckcertificate": True,
}

YDL_OPTS_VIDEO = {
    "format": "bestvideo[ext=mp4]+bestaudio/best[ext=mp4]/best",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "geo_bypass": True,
    "nocheckcertificate": True,
}

YDL_OPTS_PLAYLIST = {
    "format": QUALITY_MAP.get(Config.QUALITY, "bestaudio/best"),
    "noplaylist": False,
    "quiet": True,
    "no_warnings": True,
    "geo_bypass": True,
    "extract_flat": True,  # Don't download, just get URLs
}


def _is_url(text: str) -> bool:
    return re.match(r"https?://", text.strip()) is not None


def _is_youtube_playlist(url: str) -> bool:
    return "list=" in url and ("youtube.com" in url or "youtu.be" in url)


async def get_stream_info(query: str, mode: str = "audio") -> Optional[dict]:
    """
    Given a search query or URL, return a dict with:
      - title, url, duration, thumbnail, is_live, webpage_url
    Returns None on failure.
    """
    opts = YDL_OPTS_VIDEO.copy() if mode == "video" else YDL_OPTS_AUDIO.copy()

    if not _is_url(query):
        opts["default_search"] = "ytsearch1"

    loop = asyncio.get_event_loop()
    try:
        info = await loop.run_in_executor(None, lambda: _extract(query, opts))
        if not info:
            return None
        return {
            "title": info.get("title", "Unknown"),
            "url": info.get("url") or info.get("webpage_url"),
            "duration": info.get("duration", 0),
            "thumbnail": info.get("thumbnail", ""),
            "is_live": info.get("is_live", False),
            "webpage_url": info.get("webpage_url", ""),
            "uploader": info.get("uploader", "Unknown"),
        }
    except Exception as exc:
        logger.error("Stream extraction error: %s", exc)
        return None


async def get_playlist_tracks(url: str) -> list:
    """Extract all track URLs from a YouTube playlist."""
    loop = asyncio.get_event_loop()
    try:
        data = await loop.run_in_executor(None, lambda: _extract(url, YDL_OPTS_PLAYLIST))
        if not data:
            return []
        entries = data.get("entries", [])
        tracks = []
        for entry in entries:
            if entry:
                tracks.append({
                    "title": entry.get("title", "Unknown"),
                    "url": entry.get("url") or f"https://youtube.com/watch?v={entry.get('id', '')}",
                    "duration": entry.get("duration", 0),
                    "thumbnail": entry.get("thumbnail", ""),
                    "is_live": False,
                    "webpage_url": entry.get("url", ""),
                    "uploader": entry.get("uploader", "Unknown"),
                })
        return tracks
    except Exception as exc:
        logger.error("Playlist extraction error: %s", exc)
        return []


def _extract(query: str, opts: dict) -> Optional[dict]:
    """Synchronous yt-dlp extraction (run in executor)."""
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if not info:
            return None
        # If it's a search result list, take the first entry
        if "entries" in info:
            entries = [e for e in info["entries"] if e]
            return entries[0] if entries else None
        return info
