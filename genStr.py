"""
╔══════════════════════════════════════════════════════════════╗
║                      genStr.py                              ║
║   Run this ONCE to generate your Pyrogram STRING SESSION    ║
║   Usage:  python3 genStr.py                                 ║
╚══════════════════════════════════════════════════════════════╝
"""

from pyrogram import Client
from config import Config

print("\n" + "═" * 58)
print("  🎵  XivaSudev Music Bot — Session String Generator")
print("═" * 58)
print("\n  This will log in with YOUR Telegram account (not the bot).")
print("  The session string lets the bot stream audio in voice chats.\n")

with Client(
    name="session_gen",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
) as app:
    session = app.export_session_string()

print("\n" + "═" * 58)
print("  ✅  YOUR SESSION STRING (copy everything below):")
print("═" * 58)
print(f"\n{session}\n")
print("═" * 58)
print("  Paste this value as SESSION= in your .env file")
print("  or in Render Environment Variables.")
print("═" * 58 + "\n")
