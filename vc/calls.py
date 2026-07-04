import asyncio
import config
from vc.assistant import assistant

pytgcalls = None
queues = {}
now_playing = {}

if config.VC_ENABLED:
    from pytgcalls import PyTgCalls
    from pytgcalls.types import MediaStream
    from pytgcalls.types.stream import StreamEnded
    from pytgcalls.exceptions import NoActiveGroupCall, NotInCallError

    pytgcalls = PyTgCalls(assistant)


def get_queue(chat_id: int) -> list:
    return queues.setdefault(chat_id, [])


async def join_and_play(chat_id: int, song: dict):
    from pytgcalls.types import MediaStream

    await pytgcalls.play(chat_id, MediaStream(song["path"]))
    now_playing[chat_id] = song


async def play_or_queue(chat_id: int, song: dict):
    if chat_id in now_playing and now_playing[chat_id]:
        get_queue(chat_id).append(song)
        return "queued", len(get_queue(chat_id))
    await join_and_play(chat_id, song)
    return "playing", 0


async def skip_track(chat_id: int):
    queue = get_queue(chat_id)
    if queue:
        song = queue.pop(0)
        await join_and_play(chat_id, song)
        return song
    now_playing.pop(chat_id, None)
    await pytgcalls.leave_call(chat_id)
    return None


async def stop_playback(chat_id: int):
    queues[chat_id] = []
    now_playing.pop(chat_id, None)
    await pytgcalls.leave_call(chat_id)


async def pause_playback(chat_id: int):
    await pytgcalls.pause_stream(chat_id)


async def resume_playback(chat_id: int):
    await pytgcalls.resume_stream(chat_id)


async def mute_playback(chat_id: int):
    await pytgcalls.mute_stream(chat_id)


async def unmute_playback(chat_id: int):
    await pytgcalls.unmute_stream(chat_id)


def register_stream_end_handler():
    if not config.VC_ENABLED:
        return

    from pytgcalls.types.stream import StreamEnded
    from utils.downloader import cleanup

    @pytgcalls.on_update()
    async def _on_update(_, update):
        if isinstance(update, StreamEnded):
            chat_id = update.chat_id
            finished = now_playing.pop(chat_id, None)
            if finished:
                cleanup(finished.get("path"))
            queue = get_queue(chat_id)
            if queue:
                song = queue.pop(0)
                await join_and_play(chat_id, song)
            else:
                try:
                    await pytgcalls.leave_call(chat_id)
                except Exception:
                    pass
