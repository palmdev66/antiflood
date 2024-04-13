import time, asyncio, os
from aiogram import Router, F
from aiogram.types import Message, ChatMemberUpdated
from aiogram.filters import Command, IS_MEMBER, IS_NOT_MEMBER, ChatMemberUpdatedFilter
from aiogram.types.chat_permissions import ChatPermissions
from aiogram.enums import ChatMemberStatus
from filters.chat_type import ChatTypeFilter
from filters.antiflood import AntiFlood
from utils import book, checker, imageparser
from utils.database.api import bot
from utils.database import api
from datetime import datetime, timedelta
from collections import defaultdict

msg_storage = defaultdict(lambda: defaultdict(int))
joining_times = {}

router = Router()
router.message.middleware(AntiFlood())
router.message.filter(
    ChatTypeFilter(chat_type=["group", "supergroup"])
)

async def invite(msg: Message):
    bot_obj = await bot.get_me()
    bot_id = bot_obj.id
    text = await book.hello()
    chat_id = msg.chat.id
    try:
        await msg.delete()
    except:
        pass
    for chat_member in msg.new_chat_members:
        if chat_member.id == bot_id:
            try:
                chat_admins = await bot.get_chat_administrators(chat_id)
                for admin in chat_admins:
                    if admin.status == ChatMemberStatus.CREATOR:
                        await msg.answer(text)
                        await api.add_chat(chat_id, admin.user.id)
            except Exception as e:
                return print(e)
                
async def invite_event(event: ChatMemberUpdated):
    bot_obj = await bot.get_me()
    bot_id = bot_obj.id
    chat_id = event.chat.id
    chat_member = event.new_chat_member.user
    if chat_member.id != bot_id:
        name = chat_member.full_name
        username = chat_member.username

        if await api.checker("inviting", chat_id):
            global joining_times
            chat = await api.get_chat_by_id(event.chat.id)
            max_members = int(chat[24])
            max_seconds = int(chat[25])
            admin_id = chat[2]
            current_time = datetime.now()
            try:
                joining_times[event.chat.id] = [time for time in joining_times[event.chat.id] if current_time - time <= timedelta(seconds=max_seconds)]
            except:
                joining_times[event.chat.id] = []
                joining_times[event.chat.id] = [time for time in joining_times[event.chat.id] if current_time - time <= timedelta(seconds=max_seconds)]
            joining_times[event.chat.id].append(current_time)

            print(f"{len(joining_times[event.chat.id])}/{max_members} IN {max_seconds} [{event.chat.full_name}]")
            if len(joining_times[event.chat.id]) > max_members:
                await bot.send_message(admin_id, f"🚨 В вашу группу *{event.chat.full_name}* вступило *{len(joining_times)} пользователей* менее чем за *{max_seconds} секунд*!\n\n*Срочно предпримите* соответствующие *меры*!")

        if await api.checker("zalgo", chat_id):
            if await checker.check_zalgo(name):
                await checker.notify_nickname(chat_id, username, name, "zalgo")
                return await bot.ban_chat_member(chat_id, chat_member.id)
            
        if await api.checker("chinese", chat_id):
            if await checker.check_chinese(name):
                await checker.notify_nickname(chat_id, username, name, "chinese")
                return await bot.ban_chat_member(chat_id, chat_member.id)
            
        if await api.checker("arabic", chat_id):
            if await checker.check_arabic(name):
                await checker.notify_nickname(chat_id, username, name, "arabic")
                return await bot.ban_chat_member(chat_id, chat_member.id)
            
        if await api.checker("words", chat_id):
            if await checker.check_stop_word(name, chat_id):
                await checker.notify_nickname(chat_id, username, name, "words")
                return await bot.ban_chat_member(chat_id, chat_member.id)
            
async def hider(msg: Message):
    try:
        await msg.delete()
    except:
        pass

async def init(msg: Message):    
    # timecheck = await checker.nightmode(msg.chat.id)
    # if not timecheck:
    #     return await msg.delete()

    user_id = msg.from_user.id
    username = msg.from_user.username
    if msg.photo:
        src = f"./temp/{msg.photo[-1].file_id}.png"
        await msg.bot.download(file=msg.photo[-1].file_id, destination=src)
        text = await imageparser.get(src)
        caption = msg.caption
        if len(text.replace(" ", "")) < 3:
            text = await imageparser.getHash(src)
        os.remove(src)
        photo = True
    else:
        if "/start" in msg.text:
            return await msg.delete()
        text = msg.text
        caption = None
        photo = False
    chat_id = msg.chat.id
    unix = time.time()
    word = await checker.start(text, user_id, chat_id, username, photo, caption)
    if not word:
        return
    action = await checker.warn(chat_id, word[1])
    perms = ChatPermissions(can_send_messages=False)
    if action == "ban":
        await bot.ban_chat_member(chat_id, user_id)
    elif action == "mute_0":
        await bot.restrict_chat_member(chat_id, user_id, permissions=perms)
    elif action == "mute_1":
        unix += 3600
        await bot.restrict_chat_member(chat_id, user_id, permissions=perms, until_date=unix)
    elif action == "mute_3":
        unix += 10800
        await bot.restrict_chat_member(chat_id, user_id, permissions=perms, until_date=unix)
    elif action == "mute_24":
        unix += 86400
        await bot.restrict_chat_member(chat_id, user_id, permissions=perms, until_date=unix)
    elif action == "mute_48":
        unix += 172800
        await bot.restrict_chat_member(chat_id, user_id, permissions=perms, until_date=unix)
    await checker.notify(chat_id, user_id, username, word[0], text, action)
    return await msg.delete()

async def kill(msg: Message):
    if not msg.reply_to_message:
        return
    user_id = msg.reply_to_message.from_user.id
    sender = msg.from_user.id
    chat = msg.chat.id

    member = await bot.get_chat_member(chat, sender)
    if member.user.first_name == "Group" and member.user.username == "GroupAnonymousBot":
        await bot.ban_chat_member(chat, user_id)
        await bot.delete_message(chat, msg.reply_to_message.message_id)
        await msg.delete()
    elif member.status == ChatMemberStatus.ADMINISTRATOR or member.status == ChatMemberStatus.CREATOR:
        await bot.ban_chat_member(chat, user_id)
        await bot.delete_message(chat, msg.reply_to_message.message_id)
        await msg.delete()

async def mute(msg: Message):
    if not msg.reply_to_message:
        return
    user_id = msg.reply_to_message.from_user.id
    sender = msg.from_user.id
    chat = msg.chat.id

    member = await bot.get_chat_member(chat, sender)
    if member.user.first_name == "Group" and member.user.username == "GroupAnonymousBot":
        perms = ChatPermissions(can_send_messages=False)
        await bot.restrict_chat_member(chat, user_id, permissions=perms)
        await bot.delete_message(chat, msg.reply_to_message.message_id)
        await msg.delete()
    elif member.status == ChatMemberStatus.ADMINISTRATOR or member.status == ChatMemberStatus.CREATOR:
        perms = ChatPermissions(can_send_messages=False)
        await bot.restrict_chat_member(chat, user_id, permissions=perms)
        await bot.delete_message(chat, msg.reply_to_message.message_id)
        await msg.delete()
    
router.message.register(invite, F.new_chat_members)
router.chat_member.register(invite_event, ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
router.message.register(hider, F.left_chat_member | F.new_chat_title | F.new_chat_photo | F.delete_chat_photo)
router.message.register(kill, Command("kill"))
router.message.register(mute, Command("m"))
router.edited_message.register(init, F.text | F.photo)
router.message.register(init, F.text | F.photo)