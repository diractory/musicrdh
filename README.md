# 🎵 XivaSudev Music Bot

A feature-rich Telegram Music Bot built on [AsmSafone/MusicPlayer](https://github.com/AsmSafone/MusicPlayer).
Streams YouTube, live radio, playlists — with **Force-Join** for [@xivasudev](https://t.me/xivasudev)
and a **built-in self-ping** so it stays alive on Render free tier — no UptimeRobot needed.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🔒 Force-Join | Users must join **@xivasudev** to use the bot |
| ⚡ Fast streaming | Starts playing while downloading |
| 🎵 Sources | YouTube, live radio, playlists, m3u8 links |
| 📋 Queue | Per-group queue with shuffle, loop, export/import |
| 🛡 Admin commands | Broadcast, ban/unban, stats, restart |
| 🔁 Self-ping | Flask server + self-ping every 4 min — no UptimeRobot needed |
| 🌍 Multi-language | en, hi, ar, bn, cn, de, fr, ja, nl, ru, te, tr |
| 🐳 Docker | Dockerfile included |
| ☁️ Render-ready | render.yaml included |

---

## 🚀 Quick Deploy (Render — Free)

1. Fork / upload this repo to GitHub
2. Go to [render.com](https://render.com) → **New Web Service** → connect your repo
3. Render auto-detects `render.yaml`
4. Add these **two secret environment variables** in the Render dashboard:
   - `SESSION` → your Pyrogram string session (see step below)
   - `RENDER_APP_URL` → `https://<your-app-name>.onrender.com`
5. Click **Deploy**

---

## 🔑 Generate SESSION String

The bot needs a **Pyrogram string session** from your **personal Telegram account**
(not the bot account) to stream audio in voice chats.

```bash
# Install deps first
pip3 install -r requirements.txt

# Run the generator
python3 genStr.py
```

Copy the output string and paste it as `SESSION=` in `.env` or Render env vars.

---

## 🖥 Self-Host (VPS / Ubuntu)

```bash
git clone https://github.com/YOUR_USERNAME/MusicPlayer
cd MusicPlayer

# One-liner install
bash startup.sh
```

Or manually:

```bash
sudo apt install git curl python3-pip ffmpeg -y
pip3 install -r requirements.txt
cp sample.env .env
# Edit .env — set SESSION at minimum
python3 main.py
```

---

## 🐳 Docker

```bash
docker build -t xivasudev-musicbot .
docker run --env-file .env xivasudev-musicbot
```

---

## ⚙️ Configuration

All settings are in `.env` (copy from `sample.env`).

| Variable | Default | Description |
|---|---|---|
| `API_ID` | *set* | Telegram API ID |
| `API_HASH` | *set* | Telegram API Hash |
| `BOT_TOKEN` | *set* | Bot token from @BotFather |
| `SESSION` | **required** | Pyrogram string session |
| `SUDOERS` | `8192070400` | Owner / sudo user IDs |
| `FORCE_JOIN_CHANNEL` | `@xivasudev` | Required channel |
| `QUALITY` | `high` | `high` / `medium` / `low` |
| `STREAM_MODE` | `audio` | `audio` / `video` |
| `ADMINS_ONLY` | `False` | Only admins can !play |
| `RENDER_APP_URL` | — | Your Render app URL (enables self-ping) |

---

## 📋 Commands

### Playback
| Command | Description |
|---|---|
| `!play` / `!p [song/link]` | Play a song or add to queue |
| `!radio` / `!stream [url]` | Stream a live radio |
| `!playlist` / `!pl [url]` | Play entire YouTube playlist |
| `!skip` / `!next` | Skip current song |
| `!stop` / `!leave` | Stop and leave VC |

### Controls
| Command | Description |
|---|---|
| `!pause` / `!ps` | Pause stream |
| `!resume` / `!rs` | Resume stream |
| `!mute` / `!m` | Mute |
| `!unmute` / `!um` | Unmute |
| `!loop` / `!repeat` | Toggle loop mode |
| `!shuffle` / `!mix` | Shuffle queue |
| `!mode` / `!switch` | Toggle audio/video |

### Queue
| Command | Description |
|---|---|
| `!queue` / `!list` | Show current queue |
| `!export` / `!ep` | Export queue to JSON file |
| `!import` / `!ip` | Import queue from JSON file |

### Admin (group admin or sudo)
| Command | Description |
|---|---|
| `!lang [code]` | Change bot language |
| `!admins` | List group admins |
| `!broadcast` | (sudo) Broadcast message to all chats |
| `!stats` | (sudo) Bot statistics |
| `!ban` / `!unban` | (sudo) Ban/unban users |
| `!update` / `!restart` | (sudo) Pull git & restart |

### Misc
| Command | Description |
|---|---|
| `!ping` | Check latency |
| `!start` / `!help` | Show help menu |

---

## 💜 Credits

- Framework: [AsmSafone/MusicPlayer](https://github.com/AsmSafone/MusicPlayer)
- Credits: @sayradhey / @slocas
- Owner: [@xivasudev](https://t.me/xivasudev)
