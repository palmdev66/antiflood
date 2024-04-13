from utils.database import connection as db
from aiogram import Bot
from config import TOKEN
from aiogram.enums.parse_mode import ParseMode
from datetime import datetime, timedelta
import time
from keyboards.inline import restart 

bot = Bot(token=TOKEN, parse_mode=ParseMode.MARKDOWN)

async def generate():
    try:
        conn = await db.connect()
        async with conn.cursor() as cur:
            await cur.execute("CREATE TABLE IF NOT EXISTS users (id INT PRIMARY KEY AUTO_INCREMENT, user_id BIGINT, trialed INT)")
            await cur.execute("""CREATE TABLE IF NOT EXISTS chats (
                            id INT PRIMARY KEY AUTO_INCREMENT, 
                            chat_id BIGINT,
                            admin_id BIGINT,
                            status INT DEFAULT 1,
                            mode INT DEFAULT 0,
                            action INT DEFAULT 0,
                            action_time INT DEFAULT 1,
                            notify INT DEFAULT 1,
                            status_2 INT DEFAULT 1,
                            mode_2 INT DEFAULT 0,
                            action_2 INT DEFAULT 0,
                            action_time_2 INT DEFAULT 1,
                            sub INT DEFAULT 0,
                            sub_until DATETIME,
                            zalgo INT DEFAULT 0,
                            chinese INT DEFAULT 0,
                            arabic INT DEFAULT 0,
                            words INT DEFAULT 0,
                            nightmode INT DEFAULT 0,
                            inviting INT DEFAULT 0,
                            antiflood INT DEFAULT 0,
                            gmt INT DEFAULT 3,
                            nightfrom TIME DEFAULT '00:00',
                            nightto TIME DEFAULT '07:00',
                            inviting_members INT DEFAULT 60,
                            inviting_seconds INT DEFAULT 30
                            )""")
            await cur.execute("CREATE TABLE IF NOT EXISTS words (id INT PRIMARY KEY AUTO_INCREMENT, chat_id BIGINT, admin_id BIGINT, word TEXT, list INT)")
            await cur.execute("CREATE TABLE IF NOT EXISTS perms (id INT PRIMARY KEY AUTO_INCREMENT, chat_id BIGINT, message_id BIGINT, can_send_messages TEXT, can_send_audios TEXT, can_send_documents TEXT, can_send_photos TEXT, can_send_videos TEXT, can_send_video_notes TEXT, can_send_voice_notes TEXT, can_send_polls TEXT, can_send_other_messages TEXT, can_add_web_page_previews TEXT, can_change_info TEXT, can_invite_users TEXT, can_pin_messages TEXT, can_manage_topics TEXT, can_send_media_messages TEXT)")
            await cur.execute("CREATE TABLE IF NOT EXISTS whitelist (id INT PRIMARY KEY AUTO_INCREMENT, chat_id BIGINT, user_id BIGINT, username TEXT, count INT, until_date DATETIME)")
            await cur.execute("CREATE TABLE IF NOT EXISTS orders (id INT PRIMARY KEY AUTO_INCREMENT, user_id BIGINT, order_id BIGINT, sum INT, status INT, plan INT, merchant INT, date DATETIME, paylink TEXT, invoice_id TEXT, chat_id BIGINT)")
        conn.close()
    except:
        pass

async def restart_message():
    conn = await db.connect()
    async with conn.cursor() as cur:
        await cur.execute("SELECT user_id FROM users")
        result = await cur.fetchall()
    conn.close()
    kb = await restart()
    for user_id in result:
        try:
            await bot.send_message(user_id[0], "🔄 *Бот перезапущен!*\n\n👉🏻 *Используйте /start*", reply_markup=kb)
        except Exception as e:
            print(e)

async def order(user_id, order_id, sum, plan, merchant, paylink, chat_id, invoice_id=0):
    conn = await db.connect()
    async with conn.cursor() as cur:
        now = datetime.now()
        await cur.execute("INSERT INTO orders (user_id, order_id, sum, status, plan, merchant, date, paylink, invoice_id, chat_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (user_id, order_id, sum, 0, plan, merchant, now, paylink, invoice_id, chat_id))
        await conn.commit()
    conn.close()   

async def get_orders():
    conn = await db.connect()
    async with conn.cursor() as cur:
        await cur.execute("SELECT * FROM orders WHERE status = 0")
        result = await cur.fetchall()
    conn.close()
    return result

async def give_sub(user_id, plan, id, chat_id):
    conn = await db.connect()
    async with conn.cursor() as cur:
        now = datetime.now()
        if int(plan) == 1:
            days = 30
        if int(plan) == 2:
            days = 90
        if int(plan) == 3:
            days = 180
        if int(plan) == 4:
            days = 365
        date = now + timedelta(days=days)
        await cur.execute("UPDATE orders SET status = 1 WHERE id = %s", (id))
        await cur.execute("UPDATE chats SET sub = 1, sub_until = %s WHERE chat_id = %s", (date, chat_id))
        await conn.commit()
        try:
            kb = await restart()
            await bot.send_message(user_id, f"✅ Ваша подписка на *{days} дней* активирована!\n\nДействует до: *{date.strftime('%d.%m.%Y')}*", reply_markup=kb)
        except:
            ...
    conn.close()  

async def close_order(id, user_id):
    conn = await db.connect()
    async with conn.cursor() as cur:
        await cur.execute("UPDATE orders SET status = 2 WHERE id = %s", (id))
        await conn.commit()
        # await bot.send_message(user_id, f"❌ Время на оплату платежа истекло!")
    conn.close()  

async def get_chats(user_id=None):
    conn = await db.connect()
    async with conn.cursor() as cur:
        if user_id is None:
            await cur.execute("SELECT * FROM chats")
        else:
            await cur.execute("SELECT * FROM chats WHERE admin_id = %s", (user_id))
        result = await cur.fetchall()
        conn.close()
        if not result:
            return []
        else:
            return result
        
async def get_list_status(chatid):
    conn = await db.connect()
    async with conn.cursor() as cur:
        await cur.execute("SELECT status, status_2 FROM chats WHERE chat_id = %s", (chatid))
        result = await cur.fetchone()
        conn.close()
        if not result:
            return []
        else:
            return [result[0], result[1]]
        
async def register(user_id):
    conn = await db.connect()
    async with conn.cursor() as cur:
        await cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id))
        result = await cur.fetchone()
        if not result:
            now = datetime.now()
            await cur.execute("INSERT INTO users (user_id, trialed) VALUES (%s, %s)", (user_id, 0))
            await conn.commit()
    conn.close()    

async def check_sub(chat_id):
    conn = await db.connect()
    async with conn.cursor() as cur:
        await cur.execute("SELECT sub FROM chats WHERE id = %s", (chat_id))
        result = await cur.fetchone()
        conn.close()
        if int(result[0]) == 0:
            return False
        else:
            return True

async def status_trial(user_id):
    conn = await db.connect()
    # id Max cold or James 
    if user_id in [594901492, 719374867, 6612770574]:
        return False
    async with conn.cursor() as cur:
        await cur.execute("SELECT trialed FROM users WHERE user_id = %s", (user_id))
        result = await cur.fetchone()
        conn.close()
        if int(result[0]) == 1:
            return True
        else:
            return False
        
async def get_subdate(chat_id):
    conn = await db.connect()
    async with conn.cursor() as cur:
        await cur.execute("SELECT sub_until FROM chats WHERE id = %s", (chat_id))
        result = await cur.fetchone()
        conn.close()
        return result[0]
    
async def get_chat_mode(chat_id, list):
    conn = await db.connect()
    async with conn.cursor() as cur:
        if int(list) == 1:
            await cur.execute("SELECT mode FROM chats WHERE chat_id = %s", (chat_id))
        if int(list) == 2:
            await cur.execute("SELECT mode_2 FROM chats WHERE chat_id = %s", (chat_id))
        result = await cur.fetchone()
        conn.close()
        return result[0]
        
async def set_trial(user_id, chat_id):
    conn = await db.connect()
    async with conn.cursor() as cur:
        # id Max cold or James 
        if user_id in [594901492, 719374867, 6612770574]:
            trialdate = datetime.now() + timedelta(days=9999)
        else:
            trialdate = datetime.now() + timedelta(days=14)
        await cur.execute("UPDATE users SET trialed = 1 WHERE user_id = %s", (user_id))
        await cur.execute("UPDATE chats SET sub = 1, sub_until = %s WHERE id = %s", (trialdate, chat_id))
        await conn.commit()
    conn.close()
    return trialdate

async def add_chat(chat_id, admin_id):
    conn = await db.connect()
    async with conn.cursor() as cur:
        await cur.execute("SELECT * FROM chats WHERE chat_id = %s", (chat_id))
        result = await cur.fetchone()
        date = datetime.now()
        if not result:
            await cur.execute("INSERT INTO chats (chat_id, admin_id, sub_until) VALUES (%s, %s, %s)", (chat_id, admin_id, date))
            await conn.commit()
            try:
                kb = await restart()
                await bot.send_message(admin_id, "✨ Бот успешно добавлен в канал!\n\n↪️ Вернитесь главное меню для его настройки!", reply_markup=kb)
            except:
                ...

    conn.close()

async def get_chat(id):
    conn = await db.connect()
    async with conn.cursor() as cur:
        await cur.execute("SELECT * FROM chats WHERE id = %s", (id))
        result = await cur.fetchone()
        conn.close()
        return result
    
async def remove_chat(id):
    conn = await db.connect()
    async with conn.cursor() as cur:
        await cur.execute("DELETE FROM chats WHERE id = %s", (id))
        await conn.commit()
    conn.close()
    
async def get_chat_by_id(chat_id):
    conn = await db.connect()
    async with conn.cursor() as cur:
        await cur.execute("SELECT * FROM chats WHERE chat_id = %s", (chat_id))
        result = await cur.fetchone()
        conn.close()
        return result

async def get_words(chat_id, list):
    conn = await db.connect()
    async with conn.cursor() as cur:
        await cur.execute("SELECT word FROM words WHERE chat_id = %s AND list = %s", (chat_id, list))
        result = await cur.fetchall()
        conn.close()
        if not result:
            return []
        else:
            return result
        
async def get_all_words(chat_id):
    conn = await db.connect()
    async with conn.cursor() as cur:
        await cur.execute("SELECT word, list FROM words WHERE chat_id = %s", (chat_id))
        result = await cur.fetchall()
        conn.close()
        if not result:
            return []
        else:
            return result
        
async def get_whitelist(chat_id):
    conn = await db.connect()
    async with conn.cursor() as cur:
        await cur.execute("SELECT * FROM whitelist WHERE chat_id = %s", (chat_id))
        result = await cur.fetchall()
        conn.close()
        if not result:
            return []
        else:
            return result
        
async def get_all_wl():
    conn = await db.connect()
    async with conn.cursor() as cur:
        await cur.execute("SELECT * FROM whitelist")
        result = await cur.fetchall()
    conn.close()
    return result
    
async def get_subs():
    conn = await db.connect()
    async with conn.cursor() as cur:
        await cur.execute("SELECT * FROM chats WHERE sub = 1")
        result = await cur.fetchall()
    conn.close()
    return result
    
async def delete_wl(id):
    conn = await db.connect()
    async with conn.cursor() as cur:
        await cur.execute("SELECT * FROM whitelist WHERE id = %s", (id))
        result = await cur.fetchone()
        await cur.execute("DELETE FROM whitelist WHERE id = %s", (id))
        await conn.commit()
        chat_data = await bot.get_chat(result[1])
        await bot.send_message(result[2], f"Канал: *{chat_data.full_name}*\n\n⚠️ Ваш срок в белом списке закончился!")
    conn.close()

async def set_perms(chat_id, message_id):
    conn = await db.connect()
    chatinfo = await bot.get_chat(chat_id)
    permissions = chatinfo.permissions
    async with conn.cursor() as cur:
        await cur.execute("SELECT * FROM perms WHERE chat_id = %s", (chat_id, ))
        result = await cur.fetchone()
        if not result:
            await cur.execute("""INSERT INTO perms
                              (chat_id,
                              message_id,
                              can_send_messages,
                              can_send_audios,
                              can_send_documents,
                              can_send_photos,
                              can_send_videos,
                              can_send_video_notes,
                              can_send_voice_notes,
                              can_send_polls,
                              can_send_other_messages,
                              can_add_web_page_previews,
                              can_change_info,
                              can_invite_users,
                              can_pin_messages,
                              can_manage_topics,
                              can_send_media_messages)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                               (chat_id,
                                message_id,
                                str(permissions.can_send_messages),
                                str(permissions.can_send_audios),
                                str(permissions.can_send_documents),
                                str(permissions.can_send_photos),
                                str(permissions.can_send_videos),
                                str(permissions.can_send_video_notes),
                                str(permissions.can_send_voice_notes),
                                str(permissions.can_send_polls),
                                str(permissions.can_send_other_messages),
                                str(permissions.can_add_web_page_previews),
                                str(permissions.can_change_info),
                                str(permissions.can_invite_users),
                                str(permissions.can_pin_messages),
                                str(permissions.can_manage_topics),
                                str(permissions.can_send_media_messages)
                               )
                            )
        else:
            await cur.execute("""UPDATE perms SET
                    message_id = %s,
                    can_send_messages = %s,
                    can_send_audios = %s,
                    can_send_documents = %s,
                    can_send_photos = %s,
                    can_send_videos = %s,
                    can_send_video_notes = %s,
                    can_send_voice_notes = %s,
                    can_send_polls = %s,
                    can_send_other_messages = %s,
                    can_add_web_page_previews = %s,
                    can_change_info = %s,
                    can_invite_users = %s,
                    can_pin_messages = %s,
                    can_manage_topics = %s,
                    can_send_media_messages = %s
                    WHERE chat_id = %s
                    """,
                    (
                    message_id,
                    str(permissions.can_send_messages),
                    str(permissions.can_send_audios),
                    str(permissions.can_send_documents),
                    str(permissions.can_send_photos),
                    str(permissions.can_send_videos),
                    str(permissions.can_send_video_notes),
                    str(permissions.can_send_voice_notes),
                    str(permissions.can_send_polls),
                    str(permissions.can_send_other_messages),
                    str(permissions.can_add_web_page_previews),
                    str(permissions.can_change_info),
                    str(permissions.can_invite_users),
                    str(permissions.can_pin_messages),
                    str(permissions.can_manage_topics),
                    str(permissions.can_send_media_messages),
                    chat_id
                    )
                )
        await conn.commit()
    return conn.close()

async def get_perms(chat_id):
    conn = await db.connect()
    async with conn.cursor() as cur:
        await cur.execute("SELECT * FROM perms WHERE chat_id = %s", (chat_id, ))
        result = await cur.fetchone()
        conn.close()
        if not result:
            return [0, 0]
        else:
            perms = []
            for value in result:
                value = str(value)
                if value.lower() == 'false':
                    perms.append(False)
                elif value.lower() == 'true':
                    perms.append(True)
            return [result[2], perms]

async def desub(id):
    conn = await db.connect()
    async with conn.cursor() as cur:
        await cur.execute("SELECT * FROM chats WHERE id = %s", (id))
        result = await cur.fetchone()
        await cur.execute("UPDATE chats SET sub = 0 WHERE id = %s", (id))
        await conn.commit()
        await bot.send_message(result[2], f"⚠️ Ваша подписка на канал закончилась!")
    conn.close()
        
async def get_whitelist_by_id(id):
    conn = await db.connect()
    async with conn.cursor() as cur:
        await cur.execute("SELECT * FROM whitelist WHERE id = %s", (id))
        result = await cur.fetchone()
        conn.close()
        if not result:
            return []
        else:
            return result
        
async def get_whitelist_userid(user_id):
    conn = await db.connect()
    async with conn.cursor() as cur:
        await cur.execute("SELECT * FROM whitelist WHERE user_id = %s", (user_id))
        result = await cur.fetchall()
        conn.close()
        return result
    
async def set_user_id(username, user_id):
    conn = await db.connect()

    async with conn.cursor() as cur: 
        await cur.execute("UPDATE whitelist SET user_id = %s WHERE username = %s", (user_id, username))
        await conn.commit()
    conn.close()

async def set_username(username, user_id):
    try:
        conn = await db.connect()

        async with conn.cursor() as cur: 
            await cur.execute("UPDATE whitelist SET username = %s WHERE user_id = %s", (username, user_id))
            await conn.commit()
        conn.close()
    except:
        pass

async def take_count_wl(user_id):
    try:
        conn = await db.connect()
        async with conn.cursor() as cur: 
            await cur.execute("UPDATE whitelist SET count = count - 1 WHERE user_id = %s", (user_id))
            await conn.commit()
            await cur.execute("SELECT count FROM whitelist WHERE user_id = %s", (user_id))
            result = await cur.fetchone()
            print(result, user_id)
            if result[0] == 0:
                await cur.execute("DELETE FROM whitelist WHERE user_id = %s", (user_id))
                await conn.commit()
        conn.close()
    except:
        pass

async def edit_whitelist(id=0, userid=0, username=None, count=0, wl_id=0):
    conn = await db.connect()

    async with conn.cursor() as cur:
        try:
            if id != 0 and count != 0:
                if not username:
                    username = " "
                chat = await get_chat(id)
                chat_id = chat[1]
                count = int(count)
                username = username.replace("@", "")
                now = datetime.now()
                if count == 60:
                    date = now + timedelta(days=30)
                elif count == 120:
                    date = now + timedelta(days=60)
                elif count == 180:
                    date = now + timedelta(days=90)
                else:
                    date = now + timedelta(weeks=1000)
                await cur.execute("INSERT INTO whitelist (chat_id, user_id, username, count, until_date) VALUES (%s, %s, %s, %s, %s)", (chat_id, userid, username, count, date))
            if wl_id != 0:
                await cur.execute("DELETE FROM whitelist WHERE id = %s", (wl_id))
            await conn.commit()
        except Exception as e:
            print(e)
    conn.close()
        
async def chat_edit(id, action, value, list=1):
    conn = await db.connect()
    list = int(list)
    async with conn.cursor() as cur:
        try:
            match action:
                case "status":
                    if list == 1:
                        await cur.execute("UPDATE chats SET status = %s WHERE id = %s", (value, id))
                        await conn.commit()
                    if list == 2:
                        await cur.execute("UPDATE chats SET status_2 = %s WHERE id = %s", (value, id))
                        await conn.commit()
                case "mode":
                    if list == 1:
                        await cur.execute("UPDATE chats SET mode = %s WHERE id = %s", (value, id))
                        await conn.commit()
                    if list == 2:
                        await cur.execute("UPDATE chats SET mode_2 = %s WHERE id = %s", (value, id))
                        await conn.commit()
                case "action":
                    if list == 1:
                        await cur.execute("UPDATE chats SET action = %s WHERE id = %s", (value, id))
                        await conn.commit()
                    if list == 2:
                        await cur.execute("UPDATE chats SET action_2 = %s WHERE id = %s", (value, id))
                        await conn.commit()
                case "action_time":
                    if list == 1:
                        await cur.execute("UPDATE chats SET action_time = %s WHERE id = %s", (value, id))
                        await conn.commit()
                    if list == 2:
                        await cur.execute("UPDATE chats SET action_time_2 = %s WHERE id = %s", (value, id))
                        await conn.commit()
                case "notify":
                    await cur.execute("UPDATE chats SET notify = %s WHERE id = %s", (value, id))
                    await conn.commit()
                case "arabic":
                    await cur.execute("UPDATE chats SET arabic = %s WHERE id = %s", (value, id))
                    await conn.commit()
                case "zalgo":
                    await cur.execute("UPDATE chats SET zalgo = %s WHERE id = %s", (value, id))
                    await conn.commit()
                case "words":
                    await cur.execute("UPDATE chats SET words = %s WHERE id = %s", (value, id))
                    await conn.commit()
                case "chinese":
                    await cur.execute("UPDATE chats SET chinese = %s WHERE id = %s", (value, id))
                    await conn.commit()
                case "nightmode":
                    await cur.execute("UPDATE chats SET nightmode = %s WHERE id = %s", (value, id))
                    await conn.commit()
                case "inviting":
                    await cur.execute("UPDATE chats SET inviting = %s WHERE id = %s", (value, id))
                    await conn.commit()
                case "antiflood":
                    await cur.execute("UPDATE chats SET antiflood = %s WHERE id = %s", (value, id))
                    await conn.commit()
                case "gmt":
                    await cur.execute("UPDATE chats SET gmt = %s WHERE id = %s", (value, id))
                    await conn.commit()
                case "time":
                    times = value.split(" ")
                    await cur.execute("UPDATE chats SET nightfrom = %s, nightto = %s WHERE id = %s", (times[0], times[1], id))
                    await conn.commit()
                case "sec":
                    await cur.execute("UPDATE chats SET inviting_seconds = %s WHERE id = %s", (value, id))
                    await conn.commit()
                case "memb":
                    await cur.execute("UPDATE chats SET inviting_members = %s WHERE id = %s", (value, id))
                    await conn.commit()
        except:
            pass
    conn.close()

async def edit_words(id, action, msg, admin, list):
    conn = await db.connect()
    chat = await get_chat(id)
    chat_id = chat[1]

    arr = msg.split(",")

    async with conn.cursor() as cur:
        try:
            if action == "edit":
                await cur.execute("DELETE FROM words WHERE chat_id = %s AND list = %s", (chat_id, list))
                await conn.commit()
            for word in arr:
                try:
                    await cur.execute("SELECT * FROM words WHERE chat_id = %s AND list = %s AND word = %s", (chat_id, list, word))
                    result = await cur.fetchall()
                    if not result:
                        word = str(word).lstrip().rstrip()
                        if len(word.replace(" ", "")) > 2:
                            await cur.execute("INSERT INTO words (chat_id, admin_id, word, list) VALUES (%s, %s, %s, %s)", (chat_id, admin, word, list))
                except:
                    pass
            await conn.commit()
        except Exception as e:
            print(e)
    conn.close()

async def get_word(chat_id, word):
    conn = await db.connect()
    async with conn.cursor() as cur:
        await cur.execute("SELECT * FROM words WHERE chat_id = %s AND word = %s", (chat_id, word))
        result = await cur.fetchone()
        conn.close()
        return result
    
async def checker(type, chat_id):
    conn = await db.connect()
    async with conn.cursor() as cur:
        match type:
            case "arabic":
                await cur.execute("SELECT arabic FROM chats WHERE chat_id = %s", (chat_id, ))
            case "zalgo":
                await cur.execute("SELECT zalgo FROM chats WHERE chat_id = %s", (chat_id, ))
            case "chinese":
                await cur.execute("SELECT chinese FROM chats WHERE chat_id = %s", (chat_id, ))
            case "words":
                await cur.execute("SELECT words FROM chats WHERE chat_id = %s", (chat_id, ))
            case "inviting":
                await cur.execute("SELECT inviting FROM chats WHERE chat_id = %s", (chat_id, ))
            case "antiflood":
                await cur.execute("SELECT antiflood FROM chats WHERE chat_id = %s", (chat_id, ))
        result = await cur.fetchone()
        conn.close()
        if not result:
            return False
        elif result[0] == 1:
            return True
        else:
            return False