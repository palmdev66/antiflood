from utils.database import api
from utils.database.api import bot
from keyboards.inline import punishments, hide
import re, unicodedata, asyncio
from datetime import datetime, timedelta
from bot import logging

alldata = {}

async def start(text, user_id, chat_id, username, photo=False, caption=None):
    admins = await bot.get_chat_administrators(chat_id)
    for admin in admins:
        if admin.user.id == user_id:
            return
    
    member = await bot.get_chat_member(chat_id, user_id)
    if member.user.username == "GroupAnonymousBot":
        return
    
    links = []
    linkcount = 0
    for link in text:
        if "https:" in link.lower() or "http:" in link.lower():
            linkcount += 1
            links.append(link)
    if linkcount >= 4:
        return [', '.join(links), 3]
    
    whitelist = await api.get_whitelist(chat_id)
    whitelist = await api.get_whitelist(chat_id)
    if whitelist:
        for wl in whitelist:
            if user_id == wl[2]:
                now = datetime.now()  
                if user_id not in alldata:
                    alldata[user_id] = {'message_time': now}
                else:
                    past = alldata[user_id]['message_time'] + timedelta(seconds=3) 
                    alldata[user_id]['message_time'] = now
                    if past > datetime.now():
                        return
                await api.take_count_wl(user_id)
                await api.set_username(username, user_id)
                return
            elif username == wl[3]:
                now = datetime.now()  
                if user_id not in alldata:
                    alldata[user_id] = {'message_time': now}
                else:
                    past = alldata[user_id]['message_time'] + timedelta(seconds=3) 
                    alldata[user_id]['message_time'] = now
                    if past > datetime.now():
                        return
                await api.set_user_id(username, user_id)
                await api.take_count_wl(user_id)
                return
            
    msgwords = text.replace(",", " ").replace(".", " ").replace("\n", " ").split(" ")
    words = await api.get_all_words(chat_id)
    result = None
    if caption is None:
        msgwords = text.replace(",", " ").replace(".", " ").replace("\n", " ").split(" ")
    else:
        msgwords = caption.replace(",", " ").replace(".", " ").replace("\n", " ").split(" ")
    for word in words:
        list = word[1]
        word = word[0]
        mode = await api.get_chat_mode(chat_id, list)
        if photo:
            logging.exception(f"{word.lower()} in {text.lower()}")
            if word.lower() in text.lower():
                result = [word, list]
                break
        if mode == 1:
            if word.lower() in text.lower():
                result = [word, list]
                break
            if word in msgwords:
                result = [word, list]
                break
        if mode == 0:
            for msgword in msgwords:
                if word.lower() == msgword.lower():
                    result = [word, list]
                    break
            if word.lower() == text.lower():
                result = [word, list]
                break
    if not result:
        return None
    else:
        logging.info(f"WORD {result[0]} in LIST {result[1]} DETECTED")
        status_1, status_2 = await api.get_list_status(chat_id)
        if result[1] == 1:
            var = status_1
        else:
            var = status_2
        if var == 1:
            return result
                
async def warn(chat_id, list=1):
    chat = await api.get_chat_by_id(chat_id)
    list = int(list)
    if list != 1:
        action = chat[10]
        action_time = chat[11]
    else:
        action = chat[5]
        action_time = chat[6]
    if action == 0:
        return "delete"
    if action == 1:
        return "ban"
    if action == 2:
        if action_time == 0:
            return "mute_0"
        if action_time == 1:
            return "mute_1"
        if action_time == 3:
            return "mute_3"
        if action_time == 24:
            return "mute_24"
        if action_time == 48:
            return "mute_48"
        
async def notify(chat_id, user_id, username, word, text, action):
    kb = None
    chat = await api.get_chat_by_id(chat_id)
    chat_data = await bot.get_chat(chat[1])
    fullname = chat_data.full_name
    admin = chat[2]
    if not username:
        username = user_id
    else:
        username = f"@{username}"
    if chat[7] == 0:
        return
    match action:
        case "delete":
            warning = "*Сообщение было удалено*"
            kb = await punishments(chat_id, user_id)
        case "ban":
            warning = "*Пользователь был заблокирован*"
            kb = await hide()
        case "mute_0":
            warning = "*Пользователь был заглушен навсегда*"
            kb = await punishments(chat_id, user_id, True)
        case "mute_1":
            warning = "*Пользователь был заглушен на час*"
            kb = await punishments(chat_id, user_id)
        case "mute_3":
            warning = "*Пользователь был заглушен на 3 часа*"
            kb = await punishments(chat_id, user_id)
        case "mute_24":
            warning = "*Пользователь был заглушен на 24 часа*"
            kb = await punishments(chat_id, user_id)
        case "mute_48":
            warning = "*Пользователь был заглушен на 48 часов*"
            kb = await punishments(chat_id, user_id)
    msg = f"⚠️ Бот обнаружил стоп-слово в чате: *{fullname}*\n\nОтправитель: *{username}*\nСообщение: `{text}`\n\nНайденное слово: `{word}`\n\n*{warning}*"
    await bot.send_message(admin,msg,reply_markup=kb)

async def notify_nickname(chat_id, username, full_name, type):
    chat = await api.get_chat_by_id(chat_id)
    chat_data = await bot.get_chat(chat[1])
    fullname = chat_data.full_name
    admin = chat[2]
    if not username:
        username = full_name
    else:
        username = f"@{username}"
    if chat[7] == 0:
        return
    match type:
        case "zalgo":
            reason = f"*В имени *{full_name}* содержатся Zalgo-символы"
        case "arabic":
            reason = f"В имени *{full_name}* содержатся арабские символы"
        case "chinese":
            reason = f"В имени *{full_name}* содержатся китайские символы"
        case "words":
            reason = f"В имени *{full_name}* содержатся стоп-слова"
    msg = f"⚠️ Бот заблокировал пользователя в группе: *{fullname}*\n\nПользователь: *{username}*\n\nПричина: {reason}"
    kb = await hide()
    await bot.send_message(admin, msg, reply_markup=kb)

async def notify_flood(chat_id, username, full_name, type, text):
    chat = await api.get_chat_by_id(chat_id)
    chat_data = await bot.get_chat(chat[1])
    fullname = chat_data.full_name
    admin = chat[2]
    if not username:
        username = full_name
    else:
        username = f"@{username}"
    if chat[7] == 0:
        return
    match type:
        case "delete":
            punish = f"*Сообщение было удалено*"
        case "ban":
            punish = f"Пользователь был *заблокирован*"
        case "mute_1":
            punish = f"Пользователь был *заглушен на час*"
        case "mute_3":
            punish = f"Пользователь был *заглушен на 3 часа*"
        case "mute_24":
            punish = f"Пользователь был *заглушен на 24 часа*"
        case "mute_48":
            punish = f"Пользователь был *заглушен на 48 часов*"
        case "mute_0":
            punish = f"Пользователь был *заглушен навсегда*"
    msg = f"⚠️ Бот обнаружил флуд в группе: *{fullname}*\n\nПользователь: *{username}*\nТекст: *{text}*\n\n{punish}"
    kb = await hide()
    await bot.send_message(admin, msg, reply_markup=kb)

async def check_arabic(str):
    arabic_pattern = re.compile(r'[\u0600-\u06FF]+')
    return bool(arabic_pattern.search(str))
    
async def check_zalgo(str):
    for char in str:
        if unicodedata.name(char) and 'COMBINING' in unicodedata.name(char):
            return True
    return False

async def check_chinese(str):
    return bool(re.search(r'[\u4e00-\u9fff]', str))

async def check_stop_word(str, chat_id):
    words = await api.get_all_words(chat_id)
    word_index = 0
    for word in words:
        for char in str:
            if char == word[word_index]:
                word_index += 1
                if word_index == len(word):
                    return True
    return False

# async def nightmode(chat_id):
#     timezones = {
#         '-11' : 'Pacific/Midway',
#         '-10' : 'America/Adak',
#         '-9' : 'America/Anchorage',
#         '-8' : 'America/Yakutat',
#         '-7' : 'Asia/Novosibirsk',
#         '-6' : 'America/Guatemala',
#         '-5' : 'America/Detroit',
#         '-4' : 'America/Aruba',
#         '-3' : 'America/Bahia',
#         '-2' : 'America/Nuuk',
#         '-1' : 'Atlantic/Azores',
#         '0' : 'Africa/Bissau',
#         '+1' : 'Africa/Ceuta',
#         '+2' : 'Asia/Hebron',
#         '+3' : 'Antarctica/Syowa',
#         '+4' : 'Europe/Samara',
#         '+5' : 'Asia/Tashkent',
#         '+6' : 'Asia/Omsk',
#         '+7' : 'Asia/Bangkok',
#         '+8' : 'Asia/Irkutsk',
#         '+9' : 'Asia/Seoul',
#         '+10' : 'Asia/Vladivostok',
#         '+11' : 'Pacific/Guadalcanal',
#         '+12' : 'Pacific/Tarawa',
#         '+13' : 'Pacific/Apia',
#         '+14' : 'Pacific/Kiritimati'
#     }
#     chat = await api.get_chat_by_id(chat_id)
#     if chat[18] == 0:
#         return True
#     try:
#         if chat[21] > 0:
#             utc = f"+{chat[21]}"
#         else:
#             utc = str(chat[21])
#         timezone = timezones[utc]
#     except:
#         return True
    
#     from_obj = datetime.datetime.strptime(str(chat[22]), "%H:%M:%S")
#     fr = from_obj.strftime("%H:%M")

#     to_obj = datetime.datetime.strptime(str(chat[23]), "%H:%M:%S")
#     to = to_obj.strftime("%H:%M")

#     now = datetime.datetime.now() - datetime.timedelta(hours=3)
#     now_datetime = pytz.utc.localize(now).astimezone(pytz.timezone(timezone))
#     now_time = datetime.datetime.strptime(now_datetime.strftime('%H:%M'), '%H:%M')

#     start_time = datetime.datetime.strptime(fr, '%H:%M')
#     end_time = datetime.datetime.strptime(to, '%H:%M')

#     if start_time <= now_time <= end_time:
#         return False
#     else:
#         return True