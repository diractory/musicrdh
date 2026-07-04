import os
import re
import uuid
import asyncio
import ssl
import urllib.request
import subprocess
import json
import config

os.makedirs(config.DOWNLOAD_DIR, exist_ok=True)

COOKIES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "instagram_cookies.txt")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def _ytdlp_available() -> bool:
    try:
        r = subprocess.run(["yt-dlp", "--version"], capture_output=True, timeout=5)
        return r.returncode == 0
    except Exception:
        return False


def _run_ytdlp_sync(args: list) -> tuple:
    result = subprocess.run(["yt-dlp"] + args, capture_output=True, text=True, timeout=180)
    return result.returncode, result.stdout, result.stderr


def clean_song_title(title: str) -> str:
    title = re.sub(r'\([^)]*\)', '', title)
    title = re.sub(r'\[[^\]]*\]', '', title)
    suffixes = [
        'official', 'audio', 'video', 'lyrics', 'music', 'hq', 'hd', '4k',
        'cover', 'remix', 'live', 'performance', 'version', 'track', 'song',
        'full', 'edit', 'extended', 'radio', 'mix', 'instrumental', 'acoustic',
        'slowed', 'reverb', 'bass boosted', 'remastered', 'visualizer', 'feat', 'ft',
    ]
    for s in suffixes:
        title = re.sub(rf'\s*[-–—]?\s*{s}\s*$', '', title, flags=re.IGNORECASE)
    title = re.sub(r'^[^\-–—]+\s*[-–—]\s*', '', title)
    if ' - ' in title:
        title = title.split(' - ')[-1].strip()
    return ' '.join(title.split()).strip()


async def search_and_download_audio(query: str) -> dict:
    # Spotify link → extract title from page
    if 'spotify.com' in query.lower():
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(query, headers={'User-Agent': UA})
            html = urllib.request.urlopen(req, context=ctx, timeout=10).read().decode('utf-8')
            match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
            if match:
                title = match.group(1).split('|')[0].strip()
                title = title.split('- song')[0].split('- single')[0].strip()
                query = title
        except Exception:
            pass

    uid = uuid.uuid4().hex
    out_template = os.path.join(config.DOWNLOAD_DIR, f"{uid}.%(ext)s")

    ydl_args = [
        f"ytsearch1:{query} audio",
        "--format", "bestaudio/best",
        "--postprocessor-args", "ffmpeg:-q:a 0",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "192K",
        "--embed-thumbnail",
        "--add-metadata",
        "--write-thumbnail",
        "--output", out_template,
        "--no-playlist",
        "--quiet",
        "--no-warnings",
        "--print-json",
        "--add-header", f"User-Agent:{UA}",
    ]

    loop = asyncio.get_event_loop()
    code, stdout, stderr = await loop.run_in_executor(None, _run_ytdlp_sync, ydl_args)

    info = {}
    if stdout.strip():
        try:
            info = json.loads(stdout.strip().split("\n")[-1])
        except Exception:
            pass

    # Find the downloaded mp3 file
    mp3_path = None
    for f in os.listdir(config.DOWNLOAD_DIR):
        if f.startswith(uid) and f.endswith(".mp3"):
            mp3_path = os.path.join(config.DOWNLOAD_DIR, f)
            break
    # fallback: any file with uid
    if not mp3_path:
        for f in os.listdir(config.DOWNLOAD_DIR):
            if f.startswith(uid):
                mp3_path = os.path.join(config.DOWNLOAD_DIR, f)
                break

    if not mp3_path or not os.path.exists(mp3_path):
        raise RuntimeError(f"yt-dlp failed: {stderr[:300] if stderr else 'file not found'}")

    # Find thumbnail
    thumb_path = None
    base = os.path.join(config.DOWNLOAD_DIR, uid)
    for ext in ['.jpg', '.jpeg', '.png', '.webp']:
        candidate = mp3_path.replace('.mp3', ext)
        if os.path.exists(candidate):
            thumb_path = candidate
            break

    raw_title = info.get("title", query)
    clean_title = clean_song_title(raw_title) or raw_title

    return {
        "path": mp3_path,
        "thumb": thumb_path,
        "title": clean_title,
        "duration": int(info.get("duration") or 0),
        "thumbnail": info.get("thumbnail"),
        "uploader": info.get("uploader") or info.get("channel") or "Unknown",
        "webpage_url": info.get("webpage_url", ""),
    }


async def download_instagram(url: str) -> dict:
    uid = uuid.uuid4().hex
    out_template = os.path.join(config.DOWNLOAD_DIR, f"{uid}.%(ext)s")

    args = [
        url,
        "--format", "best[ext=mp4]/best",
        "--output", out_template,
        "--no-playlist",
        "--quiet",
        "--no-warnings",
        "--print-json",
        "--add-header", f"User-Agent:{UA}",
    ]
    if os.path.exists(COOKIES_FILE):
        args += ["--cookies", COOKIES_FILE]

    loop = asyncio.get_event_loop()
    code, stdout, stderr = await loop.run_in_executor(None, _run_ytdlp_sync, args)

    info = {}
    if stdout.strip():
        try:
            info = json.loads(stdout.strip().split("\n")[-1])
        except Exception:
            pass

    # Find downloaded file
    final_path = None
    for f in os.listdir(config.DOWNLOAD_DIR):
        if f.startswith(uid):
            final_path = os.path.join(config.DOWNLOAD_DIR, f)
            break

    if not final_path or not os.path.exists(final_path):
        raise RuntimeError(f"yt-dlp instagram failed: {stderr[:300] if stderr else 'file not found'}")

    return {
        "path": final_path,
        "title": info.get("title") or "Instagram Media",
        "thumbnail": info.get("thumbnail"),
        "uploader": info.get("uploader") or "Instagram",
    }


def cleanup(*paths):
    for path in paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
