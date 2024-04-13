from yoomoney import Client
from yoomoney import Quickpay
from crystalpayio import CrystalPayIO
from random import randint
from utils.database import api
from datetime import datetime, timedelta
from config import CRYSTAL_NAME, CRYSTAL_SECRET, YOOMONEY_TOKEN, YOOMONEY_ADDRESS

crystal = CrystalPayIO(CRYSTAL_NAME, CRYSTAL_SECRET)
token = YOOMONEY_TOKEN

async def get_link(merchant, plan, user_id, chat_id):
    chat_id = await api.get_chat(chat_id)
    merchant = int(merchant)
    plan = int(plan)
    if plan == 1:
        sum = 390
    if plan == 2:
        sum = 990
    if plan == 3:
        sum = 1740
    if plan == 4:
        sum = 2940
    order_id = randint(11111111,99999999)
    if merchant == 1:
        quickpay = Quickpay(
            receiver=YOOMONEY_ADDRESS,
            quickpay_form="shop",
            targets="Оплата подписки в боте",
            paymentType="SB",
            sum=sum,
            label=order_id
            )
        await api.order(user_id, order_id, sum, plan, merchant, quickpay.redirected_url, chat_id=chat_id[1])
        return quickpay.redirected_url
    if merchant == 2:
        invoice = await crystal.invoice.create(
            sum, # Цена
            20, # Время жизни чека (в минутах)
            description=str(order_id),
            amount_currency="RUB" # Валюта
        )
        await api.order(user_id, order_id, sum, plan, merchant, invoice.url, invoice_id=invoice.id, chat_id=chat_id[1])
        return invoice.url

async def check_payments():
    orders = await api.get_orders()
    count = 0
    success = 0
    cancelled = 0
    if not orders:
        return
    for order in orders:
        count += 1

        if int(order[6]) == 1:
            client = Client(token)
            history = client.operation_history(label=order[2])
            if not history:
                return
            for operation in history.operations:
                success += 1
                await api.give_sub(order[1], order[5], order[0], order[10])
                
        if int(order[6]) == 2:
            invoice = await crystal.invoice.get(order[9])
            if invoice.state != "notpayed":
                success += 1
                await api.give_sub(order[1], order[5], order[0], order[10])
            
        now = datetime.now()
        expired = order[7] + timedelta(minutes=20)

        if expired < now:
            cancelled += 1
            await api.close_order(order[0], order[1])
    print(f"[Платежи] Всего: {count} | Подтверждено: {success} | Отменено: {cancelled}")