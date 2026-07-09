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
<!-- run 3 @ 20260709152441755260 -->
<!-- run 4 @ 20260709152453609970 -->
<!-- run 5 @ 20260709152506195074 -->
<!-- run 6 @ 20260709152519105216 -->
<!-- run 7 @ 20260709152532355494 -->
<!-- run 8 @ 20260709152544881694 -->
<!-- run 9 @ 20260709152557264025 -->
<!-- run 10 @ 20260709152609785881 -->
<!-- run 11 @ 20260709152623863646 -->
<!-- run 12 @ 20260709152636086626 -->
<!-- run 13 @ 20260709152648207009 -->
<!-- run 14 @ 20260709152700110615 -->
<!-- run 15 @ 20260709152712885280 -->
<!-- run 16 @ 20260709152724640773 -->
<!-- run 17 @ 20260709152736340957 -->
<!-- run 18 @ 20260709152748382718 -->
<!-- run 19 @ 20260709152800841205 -->
<!-- run 20 @ 20260709152813665558 -->
<!-- run 21 @ 20260709152827014684 -->
<!-- run 22 @ 20260709152840861498 -->
<!-- run 23 @ 20260709152855093893 -->
<!-- run 24 @ 20260709152908962749 -->
<!-- run 25 @ 20260709152922470374 -->
<!-- run 26 @ 20260709152935972212 -->
<!-- run 27 @ 20260709152948587251 -->
<!-- run 28 @ 20260709153002083599 -->
<!-- run 29 @ 20260709153015135143 -->
<!-- run 30 @ 20260709153028841968 -->
<!-- run 31 @ 20260709153043772545 -->
<!-- run 32 @ 20260709153057404344 -->
<!-- run 33 @ 20260709153111169040 -->
<!-- run 34 @ 20260709153125921130 -->
<!-- run 35 @ 20260709153140176267 -->
<!-- run 36 @ 20260709153154369078 -->
<!-- run 37 @ 20260709153208981930 -->
<!-- run 38 @ 20260709153223557636 -->
<!-- run 39 @ 20260709153237292666 -->
<!-- run 40 @ 20260709153251974024 -->
<!-- run 41 @ 20260709153306454248 -->
<!-- run 42 @ 20260709153319674682 -->
<!-- run 43 @ 20260709153333590185 -->
<!-- run 44 @ 20260709153345490622 -->
<!-- run 45 @ 20260709153357754707 -->
<!-- run 46 @ 20260709153411392200 -->
<!-- run 47 @ 20260709153429825621 -->
<!-- run 48 @ 20260709153443064655 -->
<!-- run 49 @ 20260709153455430155 -->
<!-- run 50 @ 20260709153507902472 -->
<!-- run 51 @ 20260709153520013755 -->
<!-- run 52 @ 20260709153532847393 -->
<!-- run 53 @ 20260709153545227002 -->
<!-- run 54 @ 20260709153557756560 -->
<!-- run 55 @ 20260709153610154158 -->
<!-- run 56 @ 20260709153622721425 -->
<!-- run 57 @ 20260709153635114287 -->
<!-- run 58 @ 20260709153647301206 -->
<!-- run 59 @ 20260709153659544971 -->
<!-- run 60 @ 20260709153712446181 -->
<!-- run 61 @ 20260709153724762903 -->
<!-- run 62 @ 20260709153737966468 -->
<!-- run 63 @ 20260709153750438222 -->
<!-- run 64 @ 20260709153803198233 -->
<!-- run 65 @ 20260709153816332915 -->
<!-- run 66 @ 20260709153827918375 -->
<!-- run 67 @ 20260709153839997225 -->
<!-- run 68 @ 20260709153852104045 -->
