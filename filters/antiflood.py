from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.types.chat_permissions import ChatPermissions
import time
from utils.database import api
from utils.database.api import bot, checker
from utils.checker import warn, notify_flood

alldata = {}
FLOOD_INTERVAL = 3
TRIGGER_COUNT = 3

class AntiFlood(BaseMiddleware):
  async def __call__(
    self,
    handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
    event: Message,
    data: Dict[str, Any]
    ) -> Any:
        await handler(event, data)
        user_id = event.from_user.id
        message_text = event.text
        chat_id = event.chat.id
        username = event.from_user.username
        if not await checker("antiflood", chat_id):
            return 
        if event.photo:
            return
        whitelist = await api.get_whitelist(chat_id)
        if whitelist:
            if user_id in whitelist:
                return
            elif username in whitelist:
                return
        global alldata
        user_id = event.from_user.id
        message_text = event.text
        
        now = time.time()

        if user_id not in alldata:
            alldata[user_id] = {'message_count': 1, 'last_message': message_text, 'message_time': now}
        else:
            if alldata[user_id]['last_message'] == message_text:
                alldata[user_id]['message_count'] += 1
                alldata[user_id]['message_time'] = now
            else:
                alldata[user_id] = {'message_count': 1, 'last_message': message_text}

        if alldata[user_id]['message_count'] >= TRIGGER_COUNT:
            getunix = now - alldata[user_id]['message_time']
            if getunix < FLOOD_INTERVAL:
                action = await warn(chat_id)
                perms = ChatPermissions(can_send_messages=False)
                try:
                    if action == "ban":
                        await bot.ban_chat_member(chat_id, user_id)
                    elif action == "mute_0":
                        await bot.restrict_chat_member(chat_id, user_id, permissions=perms)
                    elif action == "mute_1":
                        now += 3600
                        await bot.restrict_chat_member(chat_id, user_id, permissions=perms, until_date=now)
                    elif action == "mute_3":
                        now += 10800
                        await bot.restrict_chat_member(chat_id, user_id, permissions=perms, until_date=now)
                    elif action == "mute_24":
                        now += 86400
                        await bot.restrict_chat_member(chat_id, user_id, permissions=perms, until_date=now)
                    elif action == "mute_48":
                        now += 172800
                        await bot.restrict_chat_member(chat_id, user_id, permissions=perms, until_date=now)
                    await notify_flood(chat_id, event.from_user.username, event.from_user.full_name, action, message_text)
                except:
                    return
                try:
                    await bot.delete_message(chat_id, event.message_id)
                except:
                    pass
            else:
                alldata[user_id]['message_count'] = 0