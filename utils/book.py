from aiogram.utils.markdown import hlink
from utils.database import api
from aiogram import Bot
from config import TOKEN
from aiogram.enums.parse_mode import ParseMode
from datetime import datetime

bot = Bot(token=TOKEN, parse_mode=ParseMode.MARKDOWN)

async def start(name, user_id):
    return(
        "Я удаляю сообщения со *СТОП-СЛОВАМИ*. Такие сообщения я *удаляю*, нарушителей могу *отправлять в бан*, либо просто *заглушать*. За собой удаляю сообщения!\n\n"
        "👇🏻 Выбери свою группу из списка для её настройки."
    )

async def expired():
    return(
        f"🚀 У тебя нет действующей подписки, используй пробный период, либо оплати подписку"
    )

async def subpay(step, merchant=0, plan=0):
    if step == "plans":
        return(
            f"🔶 Выберите тарифный план"
        )
    if step == "merchant":
        return(
            f"🔶 Выберите платежную систему"
        )
    if step == "link":
        merchant = int(merchant)
        plan = int(plan)
        if merchant == 1:
            merchant = "Банковская карта РФ"
        if merchant == 2:
            merchant = "Криптовалюта"
        if plan == 1:
            plan = "[390р.] 1 месяц"
        if plan == 2:
            plan = "[990р.] 3 месяца"
        if plan == 3:
            plan = "[1740р.] 6 месяцев"
        if plan == 4:
            plan = "[2940р.] 12 месяцев"
        return("🔶 Оплатите подписку\n\n"
               f"Тариф: *{plan}*\n"
               f"Метод оплаты: *{merchant}*\n\n"
               f"Время на оплату: *20 минут*\n"
               "Платежи проверяются автоматически"
               )

async def trial(user_id, chat_id):
    result = await api.set_trial(user_id, chat_id)
    return(
        f"✅ Пробная подписка на 14 дней успешно активирована!\n\n"
        f"Действует до: *{result.strftime('%d.%m.%Y')}*"
    )

async def hello():
    return(
        f"✅ Бот успешно добавлен в группу!\n\n"
        "Теперь администратор группы должен настроить его в личных сообщениях с ботом\n\n"
        "Приятного пользования! 🙂"
    )

async def chat(id, list=1):
    date = await api.get_subdate(id)
    chat = await api.get_chat(id)
    try:
        chat_data = await bot.get_chat(chat[1])
    except:
        await api.remove_chat(id)
        return False
    # words = await api.get_words(chat[1], list)
    # list = []
    # for word in words:
    #     list.append(word[0])
    return(
        f"🔶 Ваша группа\n\n"
        f"*{chat_data.full_name}* ({chat[1]})\n\n"
        f"Подписка действительна до: *{date.strftime('%d.%m.%Y')}*\n\n"
        # "Текущие стоп слова:\n"
        # f"*{', '.join(list)}*\n\n"
        "Все необходимые *настройки в меню ниже*. Если *необходимо пояcнение*, нажмите на ❓"
    )

async def whitelist(id):
    chat = await api.get_chat(id)
    chat_data = await bot.get_chat(chat[1])
    return(
        f"🔶 Белый список группы\n\n"
        f"*{chat_data.full_name}* [[{chat[1]}]]\n\n"
        "Для получения подробностей или удаления, *выберите нужного пользователя*"
    )

async def gmt(id):
    chat = await api.get_chat(id)
    if chat[21] > 0:
        timezone = f"+{chat[21]}"
    else:
        timezone = chat[21]
    return(
        f"🔶 Настройка часового пояса\n"
        f"Сейчас установлен пояс: UTC {timezone}\n\n"
        "Для изменения часового пояса, введите число\n\n```Примеры:\n+3\n-2\n+0```"
    )

async def time(id):
    chat = await api.get_chat(id)
    from_obj = datetime.strptime(str(chat[22]), "%H:%M:%S")
    fr = from_obj.strftime("%H:%M")
    to_obj = datetime.strptime(str(chat[23]), "%H:%M:%S")
    to = to_obj.strftime("%H:%M")
    return(
        f"🔶 Настройка временного промежутка ночного режима\n"
        f"Сейчас установлено: С {fr} до {to}\n\n"
        "Для изменения промежутка, введите время в формате ниже\n\n```Пример:\n00:00 07:00```"
    )

async def whitelist_plans():
    return(
        f"🔶 Добавление в белый список\n\n"
        "Выберите, какое *количество постов* будет *доступно пользователю*?"
    )

async def whitelist_user():
    return(
        f"🔶 Добавление в белый список\n\n"
        "Перешлите любое сообщение от пользователя, которого хотите добавить"
    )

async def whitelist_info(wl_id):
    whitelist = await api.get_whitelist_by_id(wl_id)
    chat = await api.get_chat_by_id(whitelist[1])
    chat_data = await bot.get_chat(chat[1])
    return(
        f"🔶 Информация о пользователе белого списка\n\n"
        f"Пользователь: @*{whitelist[3]}* ({whitelist[2]})\n"
        f"Количество постов: *{whitelist[4]}* осталось\n"
        f"Действителен до: *{whitelist[5].strftime('%d.%m.%Y')}*"
    )

async def words(type):
    if type == "add":
        return("🔸 Пришлите слова или фото с текстом, чтобы я мог их *добавить*\n\n"
        "Слова в строчку, через запятую. Каждое слово должно быть минимум из 3х символов, можно использовать эмодзи.\n\n"
        "Например:\n\n"
        "```продам, гараж, куплю, деньги```"
        )
    if type == "edit":
        return("🔸 Пришлите слова или фото с текстом, чтобы я мог их *заменить*\n\n"
        "Слова в строчку, через запятую. Каждое слово должно быть минимум из 3х символов, можно использовать эмодзи.\n\n"
        "Например:\n\n"
        "```продам, гараж, куплю, деньги```"
        )

async def help(type):
    match type:
        case "toggle":
            return(
                "🔸 Включен или выключен\n\n"
                "Вы можете включить или включить список стоп слов, который обрабатывает бот. Если список будет выключен - работа по нему будет прекращена."
            )
        case "words":
            return(
                "🔸 Добавить или изменить стоп-слова\n\n"
                "Вы можете ДОБАВИТЬ стоп слова, при этом все слова будут ДОБАВЛЕНЫ к текущим.\n\nПри ИЗМЕНЕНИИ - старый список будет стерт, а новый сохранен"
            )
        case "mode":
            return(
                "🔸 Режим работы\n\n"
                "ИСКАТЬ ТОЧНО - бот будет искать слова, которые точь-в-точь сходятся с указанными вами словами\n\nИСКАТЬ ЧАСТЬ - бот будет искать слова, в которых содержится указанные вами слова"
            )
        case "action":
            return(
                "🔸 Что делаем с нарушением\n\n"
                "Вы можете:\n"
                "— удалять сообщения\n"
                "— удалять сообщение и банить нарушителя\n"
                "— удалять сообщение и заглушать нарушителя на выбранное количество часов\n"
            )
        case "notify":
            return(
                "🔸 Отчеты\n\n"
                "Бот может отправлять отчет об удалении нарушения администратору (владельцу) группы в боте."
            )
        case "whitelist":
            return(
                "🔸 Белый список\n\n"
                "Бот не будет проверять сообщения людей, которых вы добавите в белый список"
            )
        case "add":
            return(
                "🔸 Разрешения для работы бота\n\n"
                "При приглашении бота в группу ОБЯЗАТЕЛЬНО выдайте ему права администратора чата!\n\nВ ином случае бот не будет функционировать, и прийдется добавлять его заново!"
            )
        case "filter":
            return(
                "🔸 Фильтр имён\n\n"
                "При вступлении пользователя в группу, бот проверяет имя пользователя по фильтрам, которые можно настроить ниже"
            )
        case "night":
            return(
                "🔸 Ночной режим\n\n"
                "Бот запретит всем писать сообщения в группу в промежутке определенного времени по определенному часовому поясу, настроить функцию можно после включения"
            )
        case "inviting":
            return(
                "🔸 Анти-инвайтинг\n\n"
                "Бот уведомит вас о большом наплыве вступающих людей, настроить функцию можно после включения"
            )
        case "antiflood":
            return(
                "🔸 Анти-флуд\n\n"
                "Бот накажет пользователя, который решил пофлудить, метод наказания можно выбрать выше"
            )
