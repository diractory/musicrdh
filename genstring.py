from telethon import TelegramClient
from telethon.sessions import StringSession

print("Run this on your own computer, never on a server.")
api_id = int(input("API_ID: ").strip())
api_hash = input("API_HASH: ").strip()

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("\nSESSION_STRING:\n")
    print(client.session.save())
    print("\nCopy the string above into your Render environment variables as SESSION_STRING.")
