# Radhey Music Bot

Telegram bot built with **Telethon** + **PyTgCalls**, deployable on **Render**.

**Developer:** [#RADHEY](https://t.me/sunradhey) — **Channel:** [@xivasudev](https://t.me/xivasudev)

## Features
- `/play` — search & stream a song live in the group's voice chat
- `/skip`, `/pause`, `/resume`, `/mute`, `/unmute`, `/stop`, `/queue` — VC controls
- `/song <name>` — download and send a track directly (DM or group)
- Send any Instagram reel/post link (DM or group) — bot downloads and sends it back
- Force-subscribe gate: users must join `@sunradhey` and `@xivasudev` before using the bot
- `/stats`, `/broadcast` — owner-only tools
- Flask keep-alive endpoint on `/` for Render's health checks

## Why two Telegram logins?
Bots cannot join voice chats — that's a Telegram platform rule, not a limitation of this code.
So the bot uses:
1. **BOT_TOKEN** — handles all your commands.
2. **SESSION_STRING** — a real account ("assistant") that joins the group and streams audio.

## 1. Get your credentials
- `API_ID` / `API_HASH` — from https://my.telegram.org → API Development Tools
- `BOT_TOKEN` — create a bot with [@BotFather](https://t.me/BotFather)
- `OWNER_ID` — your numeric Telegram user ID, from [@userinfobot](https://t.me/userinfobot)
- `SESSION_STRING` — run locally (never on the server):
  ```
  pip install telethon
  python genstring.py
  ```
  Log in with the account you want to use as the voice-chat assistant, then copy the printed string.

## 2. Configure environment variables
Copy `.env.sample` to `.env` for local testing, or set these directly in Render's dashboard:

```
API_ID=
API_HASH=
BOT_TOKEN=
SESSION_STRING=
OWNER_ID=
SUDOERS=
FORCE_SUB_CHANNELS=sunradhey xivasudev
```

`FORCE_SUB_CHANNELS` is a space-separated list of channel usernames **without** the `@`. The bot must be admin in those channels to check membership.

## 3. Deploy on Render
1. Push this folder to a GitHub repo.
2. On Render: **New → Web Service → Docker** runtime, connect the repo.
3. Add the environment variables above in the Render dashboard.
4. Deploy. Render will build the included `Dockerfile` (Python 3.10 + ffmpeg).

## 4. Add the assistant to a group
Use the **➕ Add Assistant to Group** button from `/start`, or manually add the assistant account to any group where you want `/play` to work. It only needs to be a normal member.

## Local run
```
pip install -r requirements.txt
python bot.py
```

## Notes
- Instagram downloads depend on `yt-dlp`'s current Instagram support; some private/age-restricted content may fail.
- Downloaded files are deleted from disk immediately after being sent.
<!-- hacktoberfest update 20260709152357188573 -->
<!-- run 1 @ 20260709152416332966 -->
<!-- run 2 @ 20260709152429037406 -->
