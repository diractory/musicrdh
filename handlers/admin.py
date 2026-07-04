from telethon import events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
import config
import database

OWNER_ONLY = f"**🚫 This command is for the bot owner only.**{config.CREDIT_TEXT}"
BANNED_SET = set()

def is_owner(sender_id):
    return sender_id in config.SUDOERS

async def resolve_target(event):
    if event.is_reply:
        msg = await event.get_reply_message()
        return await event.client.get_entity(msg.sender_id), msg.sender_id
    parts = event.raw_text.split(None, 1)
    if len(parts) < 2:
        return None, None
    target = parts[1].strip().lstrip("@")
    try:
        entity = await event.client.get_entity(target)
        return entity, entity.id
    except Exception:
        return None, None

def register(bot):

    @bot.on(events.NewMessage(pattern=r"^/stats(@\w+)?$"))
    async def stats_handler(event):
        if not is_owner(event.sender_id):
            await event.reply(OWNER_ONLY)
            return
        text = (
            "**📊 Bot Statistics**\n\n"
            f"👤 **Users:** `{database.users_count()}`\n"
            f"👥 **Chats:** `{database.chats_count()}`\n"
            f"🚫 **Banned Users:** `{len(BANNED_SET)}`"
            f"{config.CREDIT_TEXT}"
        )
        await event.reply(text)

    @bot.on(events.NewMessage(pattern=r"^/broadcast(@\w+)?$"))
    async def broadcast_handler(event):
        if not is_owner(event.sender_id):
            await event.reply(OWNER_ONLY)
            return
        if not event.is_reply:
            await event.reply(f"**Reply to a message with /broadcast to send it to all users.**{config.CREDIT_TEXT}")
            return
        source = await event.get_reply_message()
        status = await event.reply("📣 **Broadcasting...**")
        sent, failed = 0, 0
        for user_id in database.all_users():
            try:
                await bot.forward_messages(user_id, source.id, from_peer=event.chat_id)
                sent += 1
            except Exception:
                failed += 1
        await status.edit(
            f"**✅ Broadcast complete.**\n"
            f"**Sent:** `{sent}` | **Failed:** `{failed}`"
            f"{config.CREDIT_TEXT}"
        )

    @bot.on(events.NewMessage(pattern=r"^/ban(@\w+)?"))
    async def ban_handler(event):
        if not is_owner(event.sender_id):
            await event.reply(OWNER_ONLY)
            return
        entity, uid = await resolve_target(event)
        if not entity or not uid:
            await event.reply(f"**Usage:** Reply to a user or `/ban @username`{config.CREDIT_TEXT}")
            return
        if uid in config.SUDOERS:
            await event.reply(f"**❌ Cannot ban a sudo user.**{config.CREDIT_TEXT}")
            return
        BANNED_SET.add(uid)
        if event.is_group:
            try:
                rights = ChatBannedRights(until_date=None, view_messages=True)
                await bot(EditBannedRequest(event.chat_id, entity, rights))
            except Exception:
                pass
        name = getattr(entity, "first_name", None) or getattr(entity, "title", str(uid))
        await event.reply(f"**🚫 Banned:** {name} (`{uid}`){config.CREDIT_TEXT}")

    @bot.on(events.NewMessage(pattern=r"^/unban(@\w+)?"))
    async def unban_handler(event):
        if not is_owner(event.sender_id):
            await event.reply(OWNER_ONLY)
            return
        entity, uid = await resolve_target(event)
        if not entity or not uid:
            await event.reply(f"**Usage:** Reply to a user or `/unban @username`{config.CREDIT_TEXT}")
            return
        BANNED_SET.discard(uid)
        if event.is_group:
            try:
                rights = ChatBannedRights(until_date=None)
                await bot(EditBannedRequest(event.chat_id, entity, rights))
            except Exception:
                pass
        name = getattr(entity, "first_name", None) or getattr(entity, "title", str(uid))
        await event.reply(f"**✅ Unbanned:** {name} (`{uid}`){config.CREDIT_TEXT}")

    @bot.on(events.NewMessage(pattern=r"^/banlist(@\w+)?$"))
    async def banlist_handler(event):
        if not is_owner(event.sender_id):
            await event.reply(OWNER_ONLY)
            return
        if not BANNED_SET:
            await event.reply(f"**✅ No banned users.**{config.CREDIT_TEXT}")
            return
        lines = "\n".join(f"• `{uid}`" for uid in BANNED_SET)
        await event.reply(f"**🚫 Banned Users:**\n{lines}{config.CREDIT_TEXT}")

    @bot.on(events.NewMessage(pattern=r"^/kick(@\w+)?"))
    async def kick_handler(event):
        if not is_owner(event.sender_id):
            await event.reply(OWNER_ONLY)
            return
        if not event.is_group:
            await event.reply(f"**This command only works in groups.**{config.CREDIT_TEXT}")
            return
        entity, uid = await resolve_target(event)
        if not entity or not uid:
            await event.reply(f"**Usage:** Reply to a user or `/kick @username`{config.CREDIT_TEXT}")
            return
        try:
            rights = ChatBannedRights(until_date=None, view_messages=True)
            await bot(EditBannedRequest(event.chat_id, entity, rights))
            rights_unban = ChatBannedRights(until_date=None)
            await bot(EditBannedRequest(event.chat_id, entity, rights_unban))
        except Exception as e:
            await event.reply(f"**❌ Kick failed:** `{e}`{config.CREDIT_TEXT}")
            return
        name = getattr(entity, "first_name", None) or getattr(entity, "title", str(uid))
        await event.reply(f"**👢 Kicked:** {name} (`{uid}`){config.CREDIT_TEXT}")
