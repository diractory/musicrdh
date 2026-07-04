import re
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError
import config

INSTAGRAM_REGEX = re.compile(
    r"(https?://(?:www\.)?instagram\.com/(?:reel|p|tv|stories)/[A-Za-z0-9_\-/]+)",
    re.IGNORECASE,
)


def extract_instagram_link(text: str):
    if not text:
        return None
    match = INSTAGRAM_REGEX.search(text)
    return match.group(1) if match else None


def format_duration(seconds: int) -> str:
    seconds = int(seconds or 0)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


async def is_group_admin(event) -> bool:
    if not event.is_group:
        return False
    try:
        perms = await event.client.get_permissions(event.chat_id, event.sender_id)
        return perms.is_admin or perms.is_creator
    except Exception:
        return False


async def get_missing_channels(client, user_id: int):
    missing = []
    for channel in config.FORCE_SUB_CHANNELS:
        try:
            entity = await client.get_entity(channel)
            await client(GetParticipantRequest(channel=entity, participant=user_id))
        except UserNotParticipantError:
            missing.append(channel)
        except Exception:
            missing.append(channel)
    return missing
