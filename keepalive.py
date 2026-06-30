"""
╔══════════════════════════════════════════════════════════════╗
║                      keepalive.py                           ║
║                                                              ║
║   Flask web server  +  self-ping loop                        ║
║   ✅  No UptimeRobot needed — the bot pings itself           ║
║   ✅  Works on Render free tier (pings every 4 minutes)      ║
║   ✅  /ping  /health  /  endpoints all available             ║
╚══════════════════════════════════════════════════════════════╝
"""

import logging
import os
import threading
import time
from datetime import datetime

import requests
from flask import Flask, jsonify

logger = logging.getLogger(__name__)

app = Flask(__name__)
_START_TIME = datetime.utcnow()


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def home():
    uptime = datetime.utcnow() - _START_TIME
    h, rem  = divmod(int(uptime.total_seconds()), 3600)
    m, s    = divmod(rem, 60)
    return jsonify({
        "status":  "🟢 alive",
        "bot":     "XivaSudev Music Bot 🎵",
        "channel": "@xivasudev",
        "uptime":  f"{h}h {m}m {s}s",
        "note":    "Self-ping active — no UptimeRobot needed!",
    })


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"ping": "pong", "ts": datetime.utcnow().isoformat()})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"health": "ok"}), 200


# ── Self-ping loop ─────────────────────────────────────────────────────────────

def _self_ping(url: str, interval: int = 240):
    """
    Sends GET /ping to our own URL every `interval` seconds (default 4 min).
    Render's free tier spins down after 15 min of inactivity —
    pinging every 4 min keeps it permanently awake. No external service needed!
    """
    time.sleep(20)   # give Flask a moment to fully start
    logger.info("🔁  Self-ping loop active → %s/ping  (every %ds)", url, interval)
    while True:
        try:
            r = requests.get(f"{url}/ping", timeout=10)
            if r.status_code == 200:
                logger.debug("🔁  Self-ping OK")
            else:
                logger.warning("⚠️   Self-ping HTTP %s", r.status_code)
        except Exception as exc:
            logger.warning("⚠️   Self-ping error: %s", exc)
        time.sleep(interval)


# ── Public entry point ─────────────────────────────────────────────────────────

def keep_alive():
    """
    Call once from main.py before starting the Telegram bot.

    1. Starts Flask on PORT (default 8080) in a background daemon thread.
    2. If RENDER_APP_URL is set, starts the self-ping loop in another thread.

    Set RENDER_APP_URL in your Render Environment Variables to your app URL,
    e.g.  https://xivasudev-musicbot.onrender.com
    """
    port        = int(os.environ.get("PORT", 8080))
    render_url  = os.environ.get("RENDER_APP_URL", "").rstrip("/")

    # Flask thread
    t_flask = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False),
        daemon=True,
        name="Flask-KeepAlive",
    )
    t_flask.start()
    logger.info("🌐  Keep-alive server started → http://0.0.0.0:%s", port)

    # Self-ping thread
    if render_url:
        t_ping = threading.Thread(
            target=_self_ping,
            args=(render_url,),
            daemon=True,
            name="Self-Ping",
        )
        t_ping.start()
    else:
        logger.warning(
            "RENDER_APP_URL is not set — self-ping disabled.\n"
            "Add RENDER_APP_URL to your Render environment variables\n"
            "to keep the bot alive without UptimeRobot."
        )
