#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════╗
# ║              startup.sh — XivaSudev Music Bot               ║
# ║   Installs system deps + Python deps, then starts the bot   ║
# ║   Usage: bash startup.sh                                    ║
# ╚══════════════════════════════════════════════════════════════╝

set -e   # exit on first error

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║       🎵  XivaSudev Music Bot — Startup Script  🎵       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ── System dependencies ────────────────────────────────────────────────────────
echo "📦  Installing system packages (ffmpeg, git, curl) …"
sudo apt-get update -qq
sudo apt-get install -y ffmpeg git curl python3-pip -qq

# ── Python dependencies ────────────────────────────────────────────────────────
echo ""
echo "🐍  Upgrading pip …"
pip3 install --upgrade pip -q

echo ""
echo "📦  Installing Python requirements …"
pip3 install -r requirements.txt -q

# ── Copy sample.env if .env doesn't exist ─────────────────────────────────────
if [ ! -f ".env" ]; then
    echo ""
    echo "📄  Creating .env from sample.env …"
    cp sample.env .env
    echo "⚠️   IMPORTANT: Open .env and fill in your SESSION string!"
    echo "     Run:  python3 genStr.py  to generate it."
    echo ""
    read -p "Press ENTER after editing .env to continue …"
fi

# ── Start the bot ──────────────────────────────────────────────────────────────
echo ""
echo "🚀  Starting XivaSudev Music Bot …"
echo ""
python3 main.py
