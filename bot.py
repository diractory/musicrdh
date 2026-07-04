import time
import asyncio
import threading
from flask import Flask
from telethon import TelegramClient
import config
import state
from handlers import start, music, instagram, admin, music_vc

web_app = Flask(__name__)


@web_app.route("/")
def home():
    return {"status": "alive", "developer": "#RADHEY", "channel": "@xivasudev"}


def run_flask():
    web_app.run(host="0.0.0.0", port=config.PORT)


async def main():
    bot = TelegramClient("bot_session", config.API_ID, config.API_HASH)
    await bot.start(bot_token=config.BOT_TOKEN)
    me = await bot.get_me()
    state.BOT_USERNAME = me.username
    state.START_TIME = time.time()

    if config.VC_ENABLED:
        from vc.assistant import assistant
        from vc.calls import pytgcalls, register_stream_end_handler

        await assistant.start()
        assistant_me = await assistant.get_me()
        state.ASSISTANT_USERNAME = assistant_me.username
        register_stream_end_handler()
        await pytgcalls.start()
        print(f"Assistant connected as @{assistant_me.username}")
    else:
        print("SESSION_STRING not set, voice-chat streaming is disabled.")

    start.register(bot)
    music.register(bot)
    instagram.register(bot)
    admin.register(bot)
    music_vc.register(bot)

    print(f"Bot connected as @{me.username}")
    await bot.run_until_disconnected()


if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(main())
