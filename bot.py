import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from config import TOKEN
from handlers import group, user
from utils.database import api
from utils import datechecker as dc
from utils import payment as pay
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import warnings

warnings.filterwarnings("ignore")

async def scheduler():
    await api.generate()
    await api.restart_message()
    await dc.wls()
    await dc.subs()
    await dc.nightmode()
    await pay.check_payments()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(dc.wls, trigger='cron', hour='*')
    scheduler.add_job(dc.subs, trigger='cron', hour='*')
    scheduler.add_job(dc.nightmode, trigger='cron', minute='*')
    scheduler.add_job(pay.check_payments, 'interval', minutes=2)
    scheduler.start()

async def main():
    datelog = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M')
    filename = f"logs/{datelog}.log"
    logging.basicConfig(level=logging.WARNING, filename=filename, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    await scheduler()
    bot = Bot(token=TOKEN, parse_mode=ParseMode.MARKDOWN)
    dp = Dispatcher()
    dp.include_routers(user.router,
                       group.router
                       )

    await bot.delete_webhook(drop_pending_updates=True)
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())