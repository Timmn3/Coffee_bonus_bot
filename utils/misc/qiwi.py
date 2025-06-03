from pyqiwip2p import AioQiwiP2P
from data.config import QIWI_PRIV_KEY

# запрос на счет
async def payment(bill_id, amount):
    p2p = AioQiwiP2P(auth_key=QIWI_PRIV_KEY)
    async with p2p:
        # Выставим счет
        new_bill = await p2p.bill(bill_id=bill_id, amount=amount, lifetime=10)
        # print(new_bill.bill_id, new_bill.pay_url)
        # print((await p2p.check(bill_id=new_bill.bill_id)).status)
    return new_bill.pay_url

# какая сумма платежа
async def amount_of_payment(bill_id):
    p2p = AioQiwiP2P(auth_key=QIWI_PRIV_KEY)
    async with p2p:
        amount = (await p2p.check(bill_id=bill_id)).amount
    return amount

# Проверка статуса платежа
async def payment_verification(bill_id):
    p2p = AioQiwiP2P(auth_key=QIWI_PRIV_KEY)
    async with p2p:
        # Проверим статус выставленного счета
        try:
            status = (await p2p.check(bill_id=bill_id)).status
            return status
        except Exception as e:
            print(e)

        # REJECTED - ОТКЛОНЕН
        # WAITING - ОЖИДАНИЕ
        # EXPIRED - ИСТЕКШИЙ
        # PAID - ОПЛАЧЕННЫЙ


async def cancel_payment(bill_id):
    p2p = AioQiwiP2P(auth_key=QIWI_PRIV_KEY)
    async with p2p:
        # Клиент отменил заказ? Тогда и счет надо закрыть
        await p2p.reject(bill_id=bill_id)


