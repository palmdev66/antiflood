from datetime import datetime, timedelta
from utils.database import api
from utils.database.api import bot
import pytz
from aiogram.types.chat_permissions import ChatPermissions
import logging

async def wls():
    whitelists = await api.get_all_wl()
    count = 0
    deleted = 0
    if not whitelists:
        return
    for item in whitelists:
        current_date = datetime.now()
        if current_date > item[5]:
            await api.delete_wl(item[0])
            deleted += 1
        count += 1

async def subs():
    subscriptions = await api.get_subs()
    count = 0
    deleted = 0
    if not subscriptions:
        return
    for item in subscriptions:
        current_date = datetime.now()
        if current_date > item[13]:
            await api.desub(item[0])
            deleted += 1
        count += 1

async def nightmode():
    timezones = {
        '-11' : 'Pacific/Midway',
        '-10' : 'America/Adak',
        '-9' : 'America/Anchorage',
        '-8' : 'America/Yakutat',
        '-7' : 'Asia/Novosibirsk',
        '-6' : 'America/Guatemala',
        '-5' : 'America/Detroit',
        '-4' : 'America/Aruba',
        '-3' : 'America/Bahia',
        '-2' : 'America/Nuuk',
        '-1' : 'Atlantic/Azores',
        '0' : 'Africa/Bissau',
        '+1' : 'Africa/Ceuta',
        '+2' : 'Asia/Hebron',
        '+3' : 'Antarctica/Syowa',
        '+4' : 'Europe/Samara',
        '+5' : 'Asia/Tashkent',
        '+6' : 'Asia/Omsk',
        '+7' : 'Asia/Bangkok',
        '+8' : 'Asia/Irkutsk',
        '+9' : 'Asia/Seoul',
        '+10' : 'Asia/Vladivostok',
        '+11' : 'Pacific/Guadalcanal',
        '+12' : 'Pacific/Tarawa',
        '+13' : 'Pacific/Apia',
        '+14' : 'Pacific/Kiritimati'
    }
    chats = await api.get_chats()
    for chat in chats:
        try:
            print(f"CHECKING STARTED {chat[1]}")
            if chat[18] == 0:
                print(f"NIGHTMODE: RETURNED (OFF) {chat[1]}")
                return
            try:
                print(f"TRYING STR TIMEZONE {chat[1]}")
                if chat[21] > 0:
                    utc = f"+{chat[21]}"
                else:
                    utc = str(chat[21])
                timezone = timezones[utc]
                now = datetime.now() - timedelta(hours=3)
                now_datetime = pytz.utc.localize(now).astimezone(pytz.timezone(timezone))
                now_time = datetime.strptime(now_datetime.strftime('%H:%M'), '%H:%M')

                from_obj = datetime.strptime(str(chat[22]), "%H:%M:%S")
                fr = from_obj.strftime("%H:%M")
                trigger_start_time = datetime.strptime(fr, '%H:%M')
                
                to_obj = datetime.strptime(str(chat[23]), "%H:%M:%S")
                to = to_obj.strftime("%H:%M")
                trigger_end_time = datetime.strptime(to, '%H:%M')
            except Exception as e:
                print(str(e) + str(chat[1]))
                logging.exception(str(e) + str(chat[1]))
                return
            print(str(now_time), str(trigger_start_time) + str(chat[1]))
            if now_time == trigger_start_time:
                print(f"NIGHTMODE STARTED {chat[1]}")
                msg = await bot.send_message(chat[1], f"🌙 Уважаемые пользователи, чат закрывается с *{fr}* до *{to}* по местному времени!\n\n✨ Желаем вам *приятных сновидений!*")
                await api.set_perms(chat[1], msg.message_id)
                permissions = ChatPermissions(can_send_messages=False)
                return await bot.set_chat_permissions(chat[1], permissions=permissions)
            elif now_time == trigger_end_time:
                print(f"NIGHTMODE ENDED {chat[1]}")
                msg, perms = await api.get_perms(chat[1])
                if msg == 0 or perms == 0:
                    return
                try:
                    await bot.delete_message(chat[1], msg)
                except:
                    pass
                permissions = ChatPermissions(can_send_messages=perms[0],
                                              can_send_audios=perms[1],
                                              can_send_documents=perms[2],
                                              can_send_photos=perms[3],
                                              can_send_videos=perms[4],
                                              can_send_video_notes=perms[5],
                                              can_send_voice_notes=perms[6],
                                              can_send_polls=perms[7],
                                              can_send_other_messages=perms[8],
                                              can_add_web_page_previews=perms[9],
                                              can_change_info=perms[10],
                                              can_invite_users=perms[11],
                                              can_pin_messages=perms[12],
                                              can_manage_topics=perms[13]
                                              )
                return await bot.set_chat_permissions(chat[1], permissions=permissions)
            else:
                return
        except Exception as e:
            logging.exception(str(e))