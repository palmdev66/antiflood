from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import Bot
from config import TOKEN
from aiogram.enums.parse_mode import ParseMode
from utils.database import api
from datetime import datetime

bot = Bot(token=TOKEN, parse_mode=ParseMode.MARKDOWN)

# Старт
async def start(user_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    me = await bot.get_me()
    chats = await api.get_chats(user_id)

    for chat in chats:
        try:
            chat_data = await bot.get_chat(chat[1])
            kb.add(
                InlineKeyboardButton(text=chat_data.full_name, callback_data=f"chat_{chat[0]}")
            )
        except:
            await api.remove_chat(chat[0])

    kb.adjust(2)

    kb.row(
            InlineKeyboardButton(text="🔗 Добавить бота в группу", url=f"https://t.me/{me.username}?startgroup=1")
        )
    
    kb.row(
            InlineKeyboardButton(text="Какие права выдавать боту ❓", callback_data=f"help_add")
        )

    return kb.as_markup(resize_keyboard=True)

# Вайтлист чата
async def whitelist(id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    chat = await api.get_chat(id)
    whitelist = await api.get_whitelist(chat[1])

    for item in whitelist:
        kb.add(
            InlineKeyboardButton(text=f"@{item[3]}", callback_data=f"wl_info_{item[0]}")
        )

    kb.adjust(2)

    kb.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data=f"chat_{id}")
    )

    return kb.as_markup(resize_keyboard=True)

# Подписка
async def subscription() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row( 
        InlineKeyboardButton(text="💳 Оплатить подписку", callback_data=f"sub_plans")
    )

    kb.row(
        InlineKeyboardButton(text="☁️ Пробный период", callback_data=f"sub_trial")
    )

    return kb.as_markup(resize_keyboard=True)

# покупка подписки
async def subpay(step, paylink=0) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    if step == "plans":
        kb.row( 
            InlineKeyboardButton(text="[390р.] 1 мес.", callback_data=f"sub_plan_1"),
            InlineKeyboardButton(text="[990р.] 3 мес.", callback_data=f"sub_plan_2")
        )

        kb.row( 
            InlineKeyboardButton(text="[1740р.] 6 мес.", callback_data=f"sub_plan_3"),
            InlineKeyboardButton(text="[2940р.] 12 мес.", callback_data=f"sub_plan_4")
        )

    if step == "merchant":

        kb.row( 
            InlineKeyboardButton(text="Банковская карта РФ", callback_data=f"sub_merch_1")
        )

        kb.row( 
            InlineKeyboardButton(text="Криптовалюта", callback_data=f"sub_merch_2")
        )

    if step == "link":

        kb.row( 
            InlineKeyboardButton(text="Перейти к оплате", url=paylink)
        )

    kb.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data=f"start")
    )

    return kb.as_markup(resize_keyboard=True)

# Вайтлист чата
async def whitelist_info(wl_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    whitelist = await api.get_whitelist_by_id(wl_id)
    chat = await api.get_chat_by_id(whitelist[1])

    kb.row(
        InlineKeyboardButton(text="❌ Удалить", callback_data=f"wl_del_{wl_id}_{chat[0]}")
    )

    kb.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data=f"chat_wl_{chat[0]}")
    )

    return kb.as_markup(resize_keyboard=True)

# Наказания
async def punishments(chat_id, user_id, onlyban=False) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    if onlyban == False:
        kb.row(
            InlineKeyboardButton(text="🔪 Зарезать", callback_data=f"ban_{chat_id}_{user_id}"),
            InlineKeyboardButton(text="🤐 Заткнуть навсегда", callback_data=f"mute_{chat_id}_{user_id}")
        )
    else: 
        kb.row(
            InlineKeyboardButton(text="🔪 Зарезать", callback_data=f"ban_{chat_id}_{user_id}")
        )

    kb.row(
        InlineKeyboardButton(text="✨ Скрыть оповещение", callback_data=f"hide")
    )

    return kb.as_markup(resize_keyboard=True)

async def hide() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(
        InlineKeyboardButton(text="✨ Скрыть оповещение", callback_data=f"hide")
    )

    return kb.as_markup(resize_keyboard=True)

# Настройки чата
async def chat(id, list=1) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    chat = await api.get_chat(id)

    kb.row(
            InlineKeyboardButton(text="💬 Просмотреть стоп-слова", callback_data=f"chat_wordlist_{id}"),
    )

    if int(list) == 1:
        kb.row(
                InlineKeyboardButton(text="⭐️ Список 1", callback_data=f"chat_list_{id}_1"),
                InlineKeyboardButton(text="Список 2", callback_data=f"chat_list_{id}_2")
        )
        status = chat[3]
        mode = chat[4]
        action = chat[5]
        action_time = chat[6]
        
    elif int(list) == 2:
        kb.row(
                InlineKeyboardButton(text="Список 1", callback_data=f"chat_list_{id}_1"),
                InlineKeyboardButton(text="⭐️ Список 2", callback_data=f"chat_list_{id}_2")
        )     
        status = chat[8]
        mode = chat[9]
        action = chat[10]
        action_time = chat[11]
    kb.row(
        InlineKeyboardButton(text="Включен или выключен ❓", callback_data=f"help_toggle")
    )

    if status == 0:
        kb.row(
                InlineKeyboardButton(text="Включен", callback_data=f"chat_toggle_1_{id}"),
                InlineKeyboardButton(text="✅ Выключен", callback_data=f"chat_toggle_0_{id}")
        )
    else:
        kb.row(
                InlineKeyboardButton(text="✅ Включен", callback_data=f"chat_toggle_1_{id}"),
                InlineKeyboardButton(text="Выключен", callback_data=f"chat_toggle_0_{id}")
        )   

    kb.row(
            InlineKeyboardButton(text="Добавить/изменить стоп-слова или фото ❓", callback_data=f"help_words")
    )

    kb.row(
            InlineKeyboardButton(text="➕ Добавить", callback_data=f"chat_words_add_{id}"),
            InlineKeyboardButton(text="🔄 Заменить", callback_data=f"chat_words_edit_{id}")
    )

    kb.row(
            InlineKeyboardButton(text="Режим работы ❓", callback_data=f"help_mode")
    )

    if mode == 0:
        kb.row(
                InlineKeyboardButton(text="✅ 🖇️ Искать точно", callback_data=f"chat_mode_0_{id}"),
                InlineKeyboardButton(text="🖇️ Искать часть", callback_data=f"chat_mode_1_{id}")
        )
    else:
        kb.row(
                InlineKeyboardButton(text="🖇️ Искать точно", callback_data=f"chat_mode_0_{id}"),
                InlineKeyboardButton(text="✅ 🖇️ Искать часть", callback_data=f"chat_mode_1_{id}")
        )  

    kb.row(
            InlineKeyboardButton(text="Что делаем с нарушением ❓", callback_data=f"help_action")
    )

    if action == 0:
        kb.row(
                InlineKeyboardButton(text="✅ ✂️ Удаляем", callback_data=f"chat_action_0_{id}"),
                InlineKeyboardButton(text="🚷 Баним", callback_data=f"chat_action_1_{id}"),
                InlineKeyboardButton(text="🔇 Заглушаем", callback_data=f"chat_action_2_{id}")
        )
    elif action == 1:
        kb.row(
                InlineKeyboardButton(text="✂️ Удаляем", callback_data=f"chat_action_0_{id}"),
                InlineKeyboardButton(text="✅ 🚷 Баним", callback_data=f"chat_action_1_{id}"),
                InlineKeyboardButton(text="🔇 Заглушаем", callback_data=f"chat_action_2_{id}")
        )
    elif action == 2:
        kb.row(
                InlineKeyboardButton(text="✂️ Удаляем", callback_data=f"chat_action_0_{id}"),
                InlineKeyboardButton(text="🚷 Баним", callback_data=f"chat_action_1_{id}"),
                InlineKeyboardButton(text="✅ 🔇 Заглушаем", callback_data=f"chat_action_2_{id}")
        )
        if action_time == 1:
            kb.row(
                    InlineKeyboardButton(text="✅ 1 ч.", callback_data=f"chat_time_1_{id}"),
                    InlineKeyboardButton(text="3 ч.", callback_data=f"chat_time_3_{id}"),
                    InlineKeyboardButton(text="24 ч.", callback_data=f"chat_time_24_{id}"),
                    InlineKeyboardButton(text="48 ч.", callback_data=f"chat_time_48_{id}"),
                    InlineKeyboardButton(text="Навсегда", callback_data=f"chat_time_0_{id}")
            )
        elif action_time == 3:
            kb.row(
                    InlineKeyboardButton(text="1 ч.", callback_data=f"chat_time_1_{id}"),
                    InlineKeyboardButton(text="✅ 3 ч.", callback_data=f"chat_time_3_{id}"),
                    InlineKeyboardButton(text="24 ч.", callback_data=f"chat_time_24_{id}"),
                    InlineKeyboardButton(text="48 ч.", callback_data=f"chat_time_48_{id}"),
                    InlineKeyboardButton(text="Навсегда", callback_data=f"chat_time_0_{id}")
            )
        elif action_time == 24:
            kb.row(
                    InlineKeyboardButton(text="1 ч.", callback_data=f"chat_time_1_{id}"),
                    InlineKeyboardButton(text="3 ч.", callback_data=f"chat_time_3_{id}"),
                    InlineKeyboardButton(text="✅ 24 ч.", callback_data=f"chat_time_24_{id}"),
                    InlineKeyboardButton(text="48 ч.", callback_data=f"chat_time_48_{id}"),
                    InlineKeyboardButton(text="Навсегда", callback_data=f"chat_time_0_{id}")
            )
        elif action_time == 48:
            kb.row(
                    InlineKeyboardButton(text="1 ч.", callback_data=f"chat_time_1_{id}"),
                    InlineKeyboardButton(text="3 ч.", callback_data=f"chat_time_3_{id}"),
                    InlineKeyboardButton(text="24 ч.", callback_data=f"chat_time_24_{id}"),
                    InlineKeyboardButton(text="✅ 48 ч.", callback_data=f"chat_time_48_{id}"),
                    InlineKeyboardButton(text="Навсегда", callback_data=f"chat_time_0_{id}")
            )
        elif action_time == 0:
            kb.row(
                    InlineKeyboardButton(text="1 ч.", callback_data=f"chat_time_1_{id}"),
                    InlineKeyboardButton(text="3 ч.", callback_data=f"chat_time_3_{id}"),
                    InlineKeyboardButton(text="24 ч.", callback_data=f"chat_time_24_{id}"),
                    InlineKeyboardButton(text="48 ч.", callback_data=f"chat_time_48_{id}"),
                    InlineKeyboardButton(text="✅ Навсегда", callback_data=f"chat_time_0_{id}")
            )

    kb.row(
            InlineKeyboardButton(text="Белый список ❓", callback_data=f"help_whitelist")
    )

    kb.row(
            InlineKeyboardButton(text="📄 Список", callback_data=f"chat_wl_{id}"),
            InlineKeyboardButton(text="➕ Добавить", callback_data=f"chat_wl_add_{id}")
    )   

    kb.row(
            InlineKeyboardButton(text="Отчеты ❓", callback_data=f"help_notify")
    )

    if chat[7] == 0:
        kb.row(
                InlineKeyboardButton(text="Включить", callback_data=f"chat_notify_1_{id}"),
                InlineKeyboardButton(text="✅ Выключить", callback_data=f"chat_notify_0_{id}")
        )
    else:
        kb.row(
                InlineKeyboardButton(text="✅ Включить", callback_data=f"chat_notify_1_{id}"),
                InlineKeyboardButton(text="Выключить", callback_data=f"chat_notify_0_{id}")
        )

    kb.row(
            InlineKeyboardButton(text="Фильтр имён ❓", callback_data=f"help_filter")
    )

    if chat[14] == 0:
        zalgotext = "Zalgo-символы"
        zalgodata = f"filter_zalgo_1_{id}"
    else:
        zalgotext = "✅ Zalgo-символы"
        zalgodata = f"filter_zalgo_0_{id}"

    if chat[15] == 0:
        chinatext = "Китайские символы"
        chinadata = f"filter_chinese_1_{id}"
    else:
        chinatext = "✅ Китайские символы"
        chinadata = f"filter_chinese_0_{id}"

    kb.row(
        InlineKeyboardButton(text=zalgotext, callback_data=zalgodata),
        InlineKeyboardButton(text=chinatext, callback_data=chinadata)
    )

    if chat[16] == 0:
        arabictext = "Арабские символы"
        arabicdata = f"filter_arabic_1_{id}"
    else:
        arabictext = "✅ Арабские символы"
        arabicdata = f"filter_arabic_0_{id}"

    if chat[17] == 0:
        wordstext = "Стоп-слова"
        wordsdata = f"filter_words_1_{id}"
    else:
        wordstext = "✅ Стоп-слова"
        wordsdata = f"filter_words_0_{id}"

    kb.row(
        InlineKeyboardButton(text=arabictext, callback_data=arabicdata),
        InlineKeyboardButton(text=wordstext, callback_data=wordsdata)
    )

    kb.row(
            InlineKeyboardButton(text="Ночной режим ❓", callback_data=f"help_night")
    )

    if chat[18] == 0:
        kb.row(
                InlineKeyboardButton(text="Включен", callback_data=f"chat_night_1_{id}"),
                InlineKeyboardButton(text="✅ Выключен", callback_data=f"chat_night_0_{id}")
        )
    else:
        kb.row(
                InlineKeyboardButton(text="✅ Включен", callback_data=f"chat_night_1_{id}"),
                InlineKeyboardButton(text="Выключен", callback_data=f"chat_night_0_{id}")
        )
        if chat[21] > 0:
            timezone = f"+{chat[21]}"
        else:
            timezone = chat[21]
        kb.row(
            InlineKeyboardButton(text=f"⚙️ Настроить часовой пояс [UTC {timezone}]", callback_data=f"gmt_edit_{id}")
        )
        from_obj = datetime.strptime(str(chat[22]), "%H:%M:%S")
        fr = from_obj.strftime("%H:%M")
        to_obj = datetime.strptime(str(chat[23]), "%H:%M:%S")
        to = to_obj.strftime("%H:%M")
        kb.row(
            InlineKeyboardButton(text=f"⏰ Настроить промежуток времени [{fr} - {to}]", callback_data=f"time_edit_{id}")
        )

    kb.row(
            InlineKeyboardButton(text="Анти-инвайтинг ❓", callback_data=f"help_inviting")
    )

    if chat[19] == 0:
        kb.row(
                InlineKeyboardButton(text="Включен", callback_data=f"chat_inviting_1_{id}"),
                InlineKeyboardButton(text="✅ Выключен", callback_data=f"chat_inviting_0_{id}")
        )
    else:
        kb.row(
                InlineKeyboardButton(text="✅ Включен", callback_data=f"chat_inviting_1_{id}"),
                InlineKeyboardButton(text="Выключен", callback_data=f"chat_inviting_0_{id}")
        )
        if chat[25] == 30:
            time30 = "✅ 30 сек."
            time60 = "60 сек."
            time90 = "90 сек."
        elif chat[25] == 60:
            time30 = "30 сек."
            time60 = "✅ 60 сек."
            time90 = "90 сек."
        elif chat[25] == 90:
            time30 = "30 сек."
            time60 = "60 сек."
            time90 = "✅ 90 сек."
        kb.row(
            InlineKeyboardButton(text=time30, callback_data=f"inv_sec_30_{id}"),
            InlineKeyboardButton(text=time60, callback_data=f"inv_sec_60_{id}"),
            InlineKeyboardButton(text=time90, callback_data=f"inv_sec_90_{id}"),
        )
        if chat[24] == 30:
            users30 = "✅ 30 чел."
            users60 = "60 чел."
            users90 = "90 чел."
        elif chat[24] == 60:
            users30 = "30 чел."
            users60 = "✅ 60 чел."
            users90 = "90 чел."
        elif chat[24] == 90:
            users30 = "30 чел."
            users60 = "60 чел."
            users90 = "✅ 90 чел."
        kb.row(
            InlineKeyboardButton(text=users30, callback_data=f"inv_memb_30_{id}"),
            InlineKeyboardButton(text=users60, callback_data=f"inv_memb_60_{id}"),
            InlineKeyboardButton(text=users90, callback_data=f"inv_memb_90_{id}"),
        )

    kb.row(
            InlineKeyboardButton(text="Анти-флуд ❓", callback_data=f"help_antiflood")
    )

    if chat[20] == 0:
        kb.row(
                InlineKeyboardButton(text="Включен", callback_data=f"chat_antiflood_1_{id}"),
                InlineKeyboardButton(text="✅ Выключен", callback_data=f"chat_antiflood_0_{id}")
        )
    else:
        kb.row(
                InlineKeyboardButton(text="✅ Включен", callback_data=f"chat_antiflood_1_{id}"),
                InlineKeyboardButton(text="Выключен", callback_data=f"chat_antiflood_0_{id}")
        )

    kb.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="start")
    )

    return kb.as_markup(resize_keyboard=True)

# Назад
async def back(id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data=f"chat_{id}")
    )

    return kb.as_markup(resize_keyboard=True)

# Рестарт
async def restart() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(
        InlineKeyboardButton(text="↪️ В главное меню", callback_data=f"start")
    )

    return kb.as_markup(resize_keyboard=True)

# В главное меню
async def tomenu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(
        InlineKeyboardButton(text="✨ В главное меню", callback_data=f"start")
    )

    return kb.as_markup(resize_keyboard=True)

# В главное меню
def replymenu():
    kb = [
        [KeyboardButton(text="🏠 В главное меню")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, one_time_keyboard=False, resize_keyboard=True)
    return keyboard

# Назад
async def whitelist_plans(id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(
        InlineKeyboardButton(text="1 шт.", callback_data=f"wl_count_1"),
        InlineKeyboardButton(text="3 шт.", callback_data=f"wl_count_3"),
        InlineKeyboardButton(text="10 шт.", callback_data=f"wl_count_10")
    )

    kb.row(
        InlineKeyboardButton(text="15 шт.", callback_data=f"wl_count_15"),
        InlineKeyboardButton(text="30 шт.", callback_data=f"wl_count_30"),
        InlineKeyboardButton(text="90 шт.", callback_data=f"wl_count_90")
    )

    kb.row(
        InlineKeyboardButton(text="60 шт. / 30 дн.", callback_data=f"wl_count_60"),
        InlineKeyboardButton(text="120 шт. / 60 дн.", callback_data=f"wl_count_120"),
        InlineKeyboardButton(text="180 шт. / 90 дн.", callback_data=f"wl_count_120")
    )

    kb.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data=f"chat_{id}")
    )

    return kb.as_markup(resize_keyboard=True)