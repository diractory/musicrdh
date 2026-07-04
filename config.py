import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")
VC_ENABLED = bool(SESSION_STRING)

OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
SUDOERS = [int(x) for x in os.environ.get("SUDOERS", "").split() if x.strip().isdigit()]
if OWNER_ID and OWNER_ID not in SUDOERS:
    SUDOERS.append(OWNER_ID)

FORCE_SUB_CHANNELS = [
    c.strip() for c in os.environ.get("FORCE_SUB_CHANNELS", "sunradhey xivasudev").split()
    if c.strip()
]

PORT = int(os.environ.get("PORT", "8080"))
DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "downloads")
DB_PATH = os.environ.get("DB_PATH", "bot.db")

DEVELOPER_NAME = "#RADHEY"
DEVELOPER_LINK = "https://t.me/sunradhey"
CHANNEL_USERNAME = "xivasudev"

CREDIT_TEXT = f"\n\n**Developer :** [{DEVELOPER_NAME}]({DEVELOPER_LINK})\n**Channel :** @{CHANNEL_USERNAME}"
INSTA_CAPTION_TAG = "Dev ~ #rdh"

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise SystemExit("API_ID, API_HASH and BOT_TOKEN must be set as environment variables.")
