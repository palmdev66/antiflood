from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from filters.chat_type import ChatTypeFilter
from aiogram.types.chat_permissions import ChatPermissions
from utils import book
from aiogram.fsm.state import StatesGroup, State
from aiogram.enums import ChatMemberStatus
from aiogram.fsm.context import FSMContext
from utils.database import api
from keyboards import inline
from utils import imageparser, payment
from utils.database.api import bot
from bot import logging
import os, re
MESS_MAX_LENGTH = 4096

router = Router()
router.message.filter(
    ChatTypeFilter(chat_type=["private"])
)

class States(StatesGroup):
    words = State()
    whitelist = State()
    gmt = State()
    time = State()
    whitelistuser = State()

async def start(msg: Message, state: FSMContext):
    try:
        await state.clear()
        await msg.answer(f"Привет, *{msg.from_user.full_name}*!", reply_markup=inline.replymenu())
        await api.register(msg.from_user.id)
        text = await book.start(msg.from_user.full_name, msg.from_user.id)
        keyboard = await inline.start(msg.from_user.id)
        return await msg.answer(text, reply_markup=keyboard)
    except Exception as e:
        logging.exception(str(e) + f"| USERID: {msg.from_user.id}")

async def start_call(call: CallbackQuery, state: FSMContext):
    try:
        await state.clear()
        text = f"Привет, *{call.from_user.full_name}*!\n\n" + await book.start(call.from_user.full_name, call.from_user.id)
        keyboard = await inline.start(call.from_user.id)
        return await call.message.edit_text(text, reply_markup=keyboard)
    except Exception as e:
        logging.exception(str(e) + f"| USERID: {call.from_user.id}")

# ТРИАЛ ПОДПИСКА
async def trial(call: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        trialed = await api.status_trial(call.from_user.id)
        if trialed:
            return await call.answer("❌ Вы уже использовали пробную подписку!", show_alert=True)
        text = await book.trial(call.from_user.id, data["chatid"])
        keyboard = await inline.tomenu()
        return await call.message.edit_text(text, reply_markup=keyboard)
    except Exception as e:
            logging.exception(str(e) + f"| USERID: {call.from_user.id}")

# ПЛАНЫ ПОДПИСОК
async def sub_plans(call: CallbackQuery, state: FSMContext):
    try:
        text = await book.subpay("plans")
        keyboard = await inline.subpay("plans")
        return await call.message.edit_text(text, reply_markup=keyboard)
    except Exception as e:
        logging.exception(str(e) + f"| USERID: {call.from_user.id}")

# МЕРЧАНТЫ
async def sub_merchant(call: CallbackQuery, state: FSMContext):
    try:
        plan = call.data.split("_")[2]
        await state.update_data(plan=plan)
        text = await book.subpay("merchant")
        keyboard = await inline.subpay("merchant")
        return await call.message.edit_text(text, reply_markup=keyboard)
    except Exception as e:
        logging.exception(str(e) + f"| USERID: {call.from_user.id}")

# ССЫЛКА НА ОПЛАТУ
async def sub_payment(call: CallbackQuery, state: FSMContext):  
    try:
        merch = call.data.split("_")[2]
        await state.update_data(merchant=merch)
        data = await state.get_data()
        chat_id = data["chatid"]
        paylink = await payment.get_link(data["merchant"], data["plan"], call.from_user.id, chat_id)
        text = await book.subpay("link", merchant=data["merchant"], plan=data["plan"])
        keyboard = await inline.subpay("link", paylink)
        return await call.message.edit_text(text, reply_markup=keyboard)
    except Exception as e:
        logging.exception(str(e) + f"| USERID: {call.from_user.id}")

# СПИСОК ЧАТОВ
async def chat(call: CallbackQuery, state: FSMContext):
    try:
        chat_id = call.data.split("_")[1]
        subscriber = await api.check_sub(chat_id)
        await state.update_data(chatid=chat_id)
        if not subscriber:
            text = await book.expired()
            keyboard = await inline.subscription()
            return await call.message.edit_text(text, reply_markup=keyboard)
        data = await state.get_data()
        try:
            keyboard = await inline.chat(chat_id, data["list"])
            text = await book.chat(chat_id, data["list"])
        except:
            await state.update_data(list=1)
            text = await book.chat(chat_id, 1)
            keyboard = await inline.chat(chat_id, 1)
        if not text:
            keyboard = await inline.start(call.from_user.id)
            await call.message.edit_reply_markup(reply_markup=keyboard)
            await state.clear()
            return await call.answer("❌ Бот не находится в чате! Чат удален из списка", show_alert=True)
        return await call.message.edit_text(text, reply_markup=keyboard)
    except Exception as e:
        logging.exception(str(e) + f"| USERID: {call.from_user.id}")

# СПИСОК СТОПСЛОВ
async def chat_wordlist(call: CallbackQuery, state: FSMContext):
    try:
        try:
            chat_id = call.data.split("_")[2]
            chat = await api.get_chat(chat_id)
            MESS_MAX_LENGTH = 4096
            try:
                data = await state.get_data()
                lists = data["list"]
            except:
                lists = 1
            words = await api.get_words(chat[1], lists)
            list = []
            for word in words:
                list.append(word[0])
            text = ', '.join(list)
            for x in range(0, len(text), MESS_MAX_LENGTH):
                mess = text[x: x + MESS_MAX_LENGTH].replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`");
                await call.message.answer(mess)
            keyboard = await inline.back(chat_id)
            await call.message.answer("Вы можете вернуться в меню!", reply_markup=keyboard)
        except Exception as e:
             print(e)
    except Exception as e:
        logging.exception(str(e) + f"| USERID: {call.from_user.id}")

# ПОМОЩЬ
async def help(call: CallbackQuery, state: FSMContext):
    try:
        type = call.data.split("_")[1]
        text = await book.help(type)
        return await call.answer(text, show_alert=True)
    except Exception as e:
        logging.exception(str(e) + f"| USERID: {call.from_user.id}")

# Выбрать список чата
async def chat_list(call: CallbackQuery, state: FSMContext):
    try:
        chat_id = call.data.split("_")[2]
        value = call.data.split("_")[3]
        await state.update_data(list=value)
        keyboard = await inline.chat(chat_id, value)
        text = await book.chat(chat_id, value)
        try:
            return await call.message.edit_text(text=text, reply_markup=keyboard)
        except:
            ...
    except Exception as e:
            logging.exception(str(e) + f"| USERID: {call.from_user.id}")

# ВКЛ/ВЫКЛ
async def chat_toggle(call: CallbackQuery, state: FSMContext):
    try:
        chat_id = call.data.split("_")[3]
        value = call.data.split("_")[2]
        data = await state.get_data()
        await api.chat_edit(chat_id, "status", value, data["list"])
        keyboard = await inline.chat(chat_id, data["list"])
        try:
            return await call.message.edit_reply_markup(reply_markup=keyboard)
        except:
            ...
    except Exception as e:
            logging.exception(str(e) + f"| USERID: {call.from_user.id}")

# Инвайтинг настройка
async def inviting_set(call: CallbackQuery, state: FSMContext):
    try:
        chat_id = call.data.split("_")[3]
        value = call.data.split("_")[2]
        type = call.data.split("_")[1]
        data = await state.get_data()
        await api.chat_edit(chat_id, type, value, data["list"])
        keyboard = await inline.chat(chat_id, data["list"])
        try:
            return await call.message.edit_reply_markup(reply_markup=keyboard)
        except:
            ...
    except Exception as e:
            logging.exception(str(e) + f"| USERID: {call.from_user.id}")

# ИСКАТЬ ТОЧНО/ЧАСТЬ
async def chat_mode(call: CallbackQuery, state: FSMContext):
    try:
        chat_id = call.data.split("_")[3]
        value = call.data.split("_")[2]
        data = await state.get_data()
        await api.chat_edit(chat_id, "mode", value, data["list"])
        keyboard = await inline.chat(chat_id, data["list"])
        try:
            return await call.message.edit_reply_markup(reply_markup=keyboard)
        except:
            ...
    except Exception as e:
            logging.exception(str(e) + f"| USERID: {call.from_user.id}")

# ДЕЙСТВИЕ С СООБЩЕНИЕМ
async def chat_action(call: CallbackQuery, state: FSMContext):
    try:
        chat_id = call.data.split("_")[3]
        value = call.data.split("_")[2]
        data = await state.get_data()
        await api.chat_edit(chat_id, "action", value, data["list"])
        keyboard = await inline.chat(chat_id, data["list"])
        try:
            return await call.message.edit_reply_markup(reply_markup=keyboard)
        except:
            ...
    except Exception as e:
            logging.exception(str(e) + f"| USERID: {call.from_user.id}")

# СРОК МУТА
async def chat_time(call: CallbackQuery, state: FSMContext):
    try:
        chat_id = call.data.split("_")[3]
        value = call.data.split("_")[2]
        data = await state.get_data()
        await api.chat_edit(chat_id, "action_time", value, data["list"])
        keyboard = await inline.chat(chat_id, data["list"])
        try:
            return await call.message.edit_reply_markup(reply_markup=keyboard)
        except:
            ...
    except Exception as e:
            logging.exception(str(e) + f"| USERID: {call.from_user.id}")

# УВЕДОМЛЕНИЯ
async def chat_notify(call: CallbackQuery, state: FSMContext):
    try:
        chat_id = call.data.split("_")[3]
        value = call.data.split("_")[2]
        await api.chat_edit(chat_id, "notify", value)
        data = await state.get_data()
        keyboard = await inline.chat(chat_id, data["list"])
        try:
            return await call.message.edit_reply_markup(reply_markup=keyboard)
        except:
            ...
    except Exception as e:
            logging.exception(str(e) + f"| USERID: {call.from_user.id}")

# НОЧНОЙ РЕЖИМ
async def chat_night(call: CallbackQuery, state: FSMContext):
    try:
        chat_id = call.data.split("_")[3]
        value = call.data.split("_")[2]
        await api.chat_edit(chat_id, "nightmode", value)
        data = await state.get_data()
        keyboard = await inline.chat(chat_id, data["list"])
        try:
            return await call.message.edit_reply_markup(reply_markup=keyboard)
        except:
            ...
    except Exception as e:
            logging.exception(str(e) + f"| USERID: {call.from_user.id}")

# АНТИФЛУД
async def chat_antiflood(call: CallbackQuery, state: FSMContext):
    try:
        chat_id = call.data.split("_")[3]
        value = call.data.split("_")[2]
        await api.chat_edit(chat_id, "antiflood", value)
        data = await state.get_data()
        keyboard = await inline.chat(chat_id, data["list"])
        try:
            return await call.message.edit_reply_markup(reply_markup=keyboard)
        except:
            ...
    except Exception as e:
            logging.exception(str(e) + f"| USERID: {call.from_user.id}")

# ИНВАЙТИНГ
async def chat_inviting(call: CallbackQuery, state: FSMContext):
    try:
        chat_id = call.data.split("_")[3]
        value = call.data.split("_")[2]
        await api.chat_edit(chat_id, "inviting", value)
        data = await state.get_data()
        keyboard = await inline.chat(chat_id, data["list"])
        try:
            return await call.message.edit_reply_markup(reply_markup=keyboard)
        except:
            ...
    except Exception as e:
            logging.exception(str(e) + f"| USERID: {call.from_user.id}")

# НАСТРОЙКА ФИЛЬТРОВ
async def chat_filters(call: CallbackQuery, state: FSMContext):
    try:
        type = call.data.split("_")[1]
        chat_id = call.data.split("_")[3]
        value = call.data.split("_")[2]
        await api.chat_edit(chat_id, type, value)
        data = await state.get_data()
        keyboard = await inline.chat(chat_id, data["list"])
        try:
            return await call.message.edit_reply_markup(reply_markup=keyboard)
        except:
            ...
    except Exception as e:
            logging.exception(str(e) + f"| USERID: {call.from_user.id}")

# ИЗМЕНЕНИЕ ЧАСОВОГО ПОЯСА
async def gmt(call: CallbackQuery, state: FSMContext):
    try:
        chat_id = call.data.split("_")[2]
        keyboard = await inline.back(chat_id)
        text = await book.gmt(chat_id)
        await state.set_state(States.gmt)
        await state.update_data(chat_id=chat_id)
        return await call.message.edit_text(text, reply_markup=keyboard)
    except Exception as e:
            logging.exception(str(e) + f"| USERID: {call.from_user.id}")

async def gmt_run(msg: Message, state: FSMContext):
    try:
        data = await state.get_data()
        list = data["list"]
        chat_id = data["chat_id"]
        keyboard = await inline.back(chat_id)
        if not msg.text.startswith(("-", "+")):
            return await msg.answer("❌ Введите верный формат часового пояса!", reply_markup=keyboard)
        await api.chat_edit(chat_id, "gmt", msg.text)
        await state.clear()
        await state.update_data(list=list)
        return await msg.answer(f"✅ Часовой пояс успешно изменен на *UTC {msg.text}*", reply_markup=keyboard)
    except Exception as e:
            logging.exception(str(e) + f"| USERID: {msg.from_user.id}")

# Настройка временного промежутка времени
async def time(call: CallbackQuery, state: FSMContext):
    try:
        chat_id = call.data.split("_")[2]
        keyboard = await inline.back(chat_id)
        text = await book.time(chat_id)
        await state.set_state(States.time)
        await state.update_data(chat_id=chat_id)
        return await call.message.edit_text(text, reply_markup=keyboard)
    except Exception as e:
            logging.exception(str(e) + f"| USERID: {call.from_user.id}")

async def time_run(msg: Message, state: FSMContext):
    try:
        data = await state.get_data()
        list = data["list"]
        chat_id = data["chat_id"]
        keyboard = await inline.back(chat_id)
        if not bool(re.match(r'\d{2}:\d{2} \d{2}:\d{2}', msg.text)):
            return await msg.answer("❌ Введите верный формат промежутка времени!\n\n```Пример:\n00:00 07:00```", reply_markup=keyboard)
        await api.chat_edit(chat_id, "time", msg.text)
        await state.clear()
        await state.update_data(list=list)
        times = msg.text.split(" ")
        return await msg.answer(f"✅ Временной промежуток изменен! С *{times[0]}* до *{times[1]}*", reply_markup=keyboard)
    except Exception as e:
            logging.exception(str(e) + f"| USERID: {msg.from_user.id}")

# ДОБАВЛЕНИЕ/ИЗМЕНЕНИЕ СЛОВ
async def chat_words(call: CallbackQuery, state: FSMContext):
    try:
        chat_id = call.data.split("_")[3]
        action = call.data.split("_")[2]
        keyboard = await inline.back(chat_id)
        text = await book.words(action)
        await state.set_state(States.words)
        await state.update_data(action=action, chat_id=chat_id)
        return await call.message.edit_text(text, reply_markup=keyboard)
    except Exception as e:
            logging.exception(str(e) + f"| USERID: {call.from_user.id}")

async def chat_words_run(msg: Message, state: FSMContext):
    try:
        data = await state.get_data()
        list = data["list"]
        chat_id = data["chat_id"]
        action = data["action"]
        keyboard = await inline.back(chat_id)
        if msg.photo:
            type = 1
            src = f"./temp/{msg.photo[-1].file_id}.png"
            await msg.bot.download(file=msg.photo[-1].file_id, destination=src)
            text = await imageparser.get(src)
            if len(text.replace(" ", "")) < 3:
                type = 2
                text = await imageparser.getHash(src)
            os.remove(src)
        else:
            type = 3
            text = msg.text
        await api.edit_words(chat_id, action, text, msg.from_user.id, list)
        await state.clear()
        await state.update_data(list=list)
        try:
            getchat = await bot.get_chat(msg.chat.id)
            fullname = getchat.full_name
        except:
            pass
        if type == 3:
            return await msg.answer(f"✅ Слова успешно добавлены в стоп-слова группы *{fullname}*", reply_markup=keyboard)
        elif type == 2:
            return await msg.answer(f"✅ Шифр фотографии добавлен в стоп-слова группы *{fullname}*", reply_markup=keyboard)
        elif type == 1:
            return await msg.answer(f"✅ Слова на фотографии добавлен в стоп-слова группы *{fullname}*", reply_markup=keyboard)
    except Exception as e:
            logging.exception(str(e) + f"| USERID: {msg.from_user.id}")

# БАН
async def ban(call: CallbackQuery, state: FSMContext):
    try:
        chat_id = call.data.split("_")[1]
        user_id = call.data.split("_")[2]
        keyboard = await inline.restart()
        await bot.ban_chat_member(chat_id, user_id)
        return await call.message.edit_text("✅ Пользователь успешно заблокирован!", reply_markup=keyboard)
    except Exception as e:
        return await call.message.edit_text("❌ Произошла ошибка при выдаче наказания!\n\nСкорее всего пользователь является администратором", reply_markup=keyboard)
        
# МУТ
async def mute(call: CallbackQuery, state: FSMContext):
    try:
        chat_id = call.data.split("_")[1]
        user_id = call.data.split("_")[2]
        keyboard = await inline.restart()
        perms = ChatPermissions(can_send_messages=False)
        await bot.restrict_chat_member(chat_id, user_id, permissions=perms)
        return await call.message.edit_text("✅ Пользователь успешно заглушен навсегда!", reply_markup=keyboard)
    except Exception as e:
        return await call.message.edit_text("❌ Произошла ошибка при выдаче наказания!\n\nСкорее всего пользователь является администратором", reply_markup=keyboard)

# СКРЫТЬ СООБЩЕНИЕ
async def hide(call: CallbackQuery, state: FSMContext):
    try:
        return await call.message.delete()
    except Exception as e:
        logging.exception(str(e) + f"| USERID: {call.from_user.id}")

# БЕЛЫЙ СПИСОК
async def chat_whitelist(call: CallbackQuery, state: FSMContext):
    try:
        chat_id = call.data.split("_")[2]
        keyboard = await inline.whitelist(chat_id)
        text = await book.whitelist(chat_id)
        return await call.message.edit_text(text, reply_markup=keyboard)
    except Exception as e:
            logging.exception(str(e) + f"| USERID: {call.from_user.id}")

async def chat_whitelist_info(call: CallbackQuery, state: FSMContext):
    try:
        wl_id = call.data.split("_")[2]
        keyboard = await inline.whitelist_info(wl_id)
        text = await book.whitelist_info(wl_id)
        return await call.message.edit_text(text, reply_markup=keyboard)
    except Exception as e:
            logging.exception(str(e) + f"| USERID: {call.from_user.id}")

async def chat_whitelist_add(call: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(States.whitelist)
        chat_id = call.data.split("_")[3]
        await state.update_data(chat_id=chat_id)
        keyboard = await inline.whitelist_plans(chat_id)
        text = await book.whitelist_plans()
        return await call.message.edit_text(text, reply_markup=keyboard)
    except Exception as e:
            logging.exception(str(e) + f"| USERID: {call.from_user.id}")

async def chat_whitelist_user(call: CallbackQuery, state: FSMContext):
    try:
        count = call.data.split("_")[2]
        await state.update_data(count=count)
        await state.set_state(States.whitelistuser)
        data = await state.get_data()
        keyboard = await inline.back(data["chat_id"])
        text = await book.whitelist_user()
        return await call.message.edit_text(text, reply_markup=keyboard)
    except Exception as e:
            logging.exception(str(e) + f"| USERID: {call.from_user.id}")

async def chat_whitelist_run(msg: Message, state: FSMContext):
    try:
        data = await state.get_data()
        chat_id = data["chat_id"]
        chat = await api.get_chat(chat_id)
        if not msg.forward_from:
            if not msg.photo:
                if msg.text[0] == "@":
                    user_id = 0
                    username = msg.text.replace("@", "")
                    full_name = msg.text
                else:
                    return await msg.answer("❌ Неверный формат сообщения!\n\nСкорее всего у пользователя стоит *ограничение на пересылку сообщений* в *настройках приватности*\n\nОтправьте его *имя пользователя в формате*: \n@username")
            else:
                return await msg.answer("❌ Неверный формат сообщения!\n\nСкорее всего у пользователя стоит *ограничение на пересылку сообщений* в *настройках приватности*\n\nОтправьте его *имя пользователя в формате*: \n@username")
        else:
            user_id = msg.forward_from.id
            username = msg.forward_from.username
            full_name = msg.forward_from.full_name
            member = await bot.get_chat_member(chat[1], user_id)
            if member.status == ChatMemberStatus.LEFT or member.status == ChatMemberStatus.KICKED:
                return await msg.answer("❌ Пользователя нет в чате!")
        count = data["count"]
        keyboard = await inline.back(chat_id)
        await api.edit_whitelist(chat_id, user_id, username, count)
        await state.clear()
        await state.update_data(list=data["list"])
        try:
            getchat = await bot.get_chat(msg.chat.id)
            fullname = getchat.full_name
        except:
            ...
        return await msg.answer(f'Пользователь: *{full_name}*\n\nГруппа: "*{fullname}*"\n\n ✅ Успешно добавлен в белый список группы!', reply_markup=keyboard)
    except Exception as e:
            logging.exception(str(e) + f"| USERID: {msg.from_user.id}")

async def chat_whitelist_del(call: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        wl_id = call.data.split("_")[2]
        await api.edit_whitelist(wl_id=wl_id)
        await state.clear()
        await state.update_data(list=data["list"])
        await call.answer("✅ Успешно удалено!", show_alert=True)
        chat_id = call.data.split("_")[3]
        keyboard = await inline.whitelist(chat_id)
        text = await book.whitelist(chat_id)
        return await call.message.edit_text(text, reply_markup=keyboard)
    except Exception as e:
            logging.exception(str(e) + f"| USERID: {call.from_user.id}")

async def restart(msg: Message):
    try:
        if msg.from_user.id in [594901492, 719374867, 6612770574]:
            await msg.answer("🛠️ *Перезапускаюсь..*")
            os.system("sudo systemctl restart bot")
    except:
        pass

    
router.message.register(start, Command("start"))
router.message.register(restart, Command("restart"))
router.message.register(start, F.text == "🏠 В главное меню")
router.callback_query.register(help, F.data.startswith("help_"))
router.callback_query.register(start_call, F.data == "start")

router.callback_query.register(trial, F.data == "sub_trial")

router.callback_query.register(sub_plans, F.data == "sub_plans")
router.callback_query.register(sub_merchant, F.data.startswith("sub_plan_"))
router.callback_query.register(sub_payment, F.data.startswith("sub_merch_"))

router.callback_query.register(chat_toggle, F.data.startswith("chat_toggle_"))
router.callback_query.register(chat_mode, F.data.startswith("chat_mode_"))
router.callback_query.register(chat_action, F.data.startswith("chat_action_"))
router.callback_query.register(chat_time, F.data.startswith("chat_time_"))
router.callback_query.register(chat_notify, F.data.startswith("chat_notify_"))
router.callback_query.register(chat_list, F.data.startswith("chat_list_"))
router.callback_query.register(chat_words, F.data.startswith("chat_words_"))
router.callback_query.register(chat_wordlist, F.data.startswith("chat_wordlist_"))
router.callback_query.register(chat_night, F.data.startswith("chat_night_"))
router.callback_query.register(chat_inviting, F.data.startswith("chat_inviting_"))
router.callback_query.register(chat_antiflood, F.data.startswith("chat_antiflood_"))
router.callback_query.register(chat_filters, F.data.startswith("filter_"))
router.callback_query.register(inviting_set, F.data.startswith("inv_"))
router.message.register(chat_words_run, States.words, F.text)
router.message.register(chat_words_run, States.words, F.photo)

router.callback_query.register(gmt, F.data.startswith("gmt_edit_"))
router.message.register(gmt_run, States.gmt, F.text)
router.callback_query.register(time, F.data.startswith("time_edit_"))
router.message.register(time_run, States.time, F.text)

router.callback_query.register(mute, F.data.startswith("mute_"))
router.callback_query.register(ban, F.data.startswith("ban_"))
router.callback_query.register(hide, F.data == "hide")

router.callback_query.register(chat_whitelist_info, F.data.startswith("wl_info_"))
router.callback_query.register(chat_whitelist_add, F.data.startswith("chat_wl_add_"))
router.callback_query.register(chat_whitelist, F.data.startswith("chat_wl_"))
router.callback_query.register(chat_whitelist_del, F.data.startswith("wl_del_"))
router.callback_query.register(chat_whitelist_user, States.whitelist, F.data.startswith("wl_count_"))
router.message.register(chat_whitelist_run, States.whitelistuser)


router.callback_query.register(chat, F.data.startswith("chat_"))