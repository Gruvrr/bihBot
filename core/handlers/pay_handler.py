import json
from aiogram.types import CallbackQuery, LabeledPrice, PreCheckoutQuery, Message
from aiogram import Router, Bot
import time
from aiogram import F

from core.handlers.referal_link import update_refurl_info, get_ref_url
from core.utils.db import close, connect
from dotenv import load_dotenv
from os import getenv
from core.keyboards.inline.inline_keyboard import main_keyboard

load_dotenv()
pt = getenv("PROVIDER_TOKEN")
router = Router()


def generate_payload(user_id, payment_type):
    return f"{payment_type}-{user_id}-{int(time.time())}"


def update_user_subscription(user_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET subscription_purchases_count = subscription_purchases_count + 1 WHERE telegram_user_id = %s",
        (user_id,))

    cursor.execute(
        "UPDATE users SET subscription_days_count = subscription_days_count + 30 WHERE telegram_user_id = %s",
        (user_id,))
    cursor.execute("UPDATE users SET subscription_active = True WHERE telegram_user_id = %s", (user_id,))

    conn.commit()
    cursor.close()
    close(conn)


def add_payment_to_db(user_id, unique_payload, amount, currency="RUB"):
    conn = connect()
    cursor = conn.cursor()
    try:

        cursor.execute(
            "INSERT INTO payments (telegram_user_id, unique_payload, amount, status) VALUES (%s, %s, %s, 'Pending')",
            (user_id, unique_payload, amount))
        conn.commit()
    except Exception as e:

        raise
    finally:
        cursor.close()
        close(conn)


def update_payment_status_in_db(unique_payload, status):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE payments SET status = %s WHERE unique_payload = %s", (status, unique_payload))
    conn.commit()
    cursor.close()
    close(conn)


def get_subscription_days(user_id):
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT subscription_days FROM users WHERE telegram_user_id = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        close(conn)
        return result[0] if result else None
    except Exception as e:
        print(f"Error getting subscription_days: {e}")
        return None


@router.callback_query(lambda c: c.data == "pay")
async def order(callback: CallbackQuery, bot: Bot):
    user_id: int = callback.from_user.id
    unique_payload = generate_payload(user_id, "subscribe")
    amount: int = 50000  # копейки
    currency: str = "RUB"
    add_payment_to_db(user_id, unique_payload, amount, currency)
    try:
        provider_data = {
            "receipt": {
                "items": [{
                    "description": "Подписка на медитации",
                    "quantity": "1.00",
                    "amount": {
                        "value": "500.00",  # Укажите здесь цену за единицу товара или услуги
                        "currency": "RUB"
                    },
                    "vat_code": 6  # НДС. Укажите актуальную ставку НДС, если она применима
                }],
                "customer": {
                    "email": "mail@mail.ru"  # Здесь должен быть email покупателя
                }
            }
        }
        await bot.send_invoice(
            chat_id=callback.from_user.id,
            title="Подписка на медитации",
            description="Абонемент 30 дней",
            provider_token=pt,
            currency="rub",
            prices=[
                LabeledPrice(
                    label="Цена",
                    amount=50000
                )
            ],
            need_name=True,
            need_phone_number=True,
            need_email=True,
            send_email_to_provider=True,
            send_phone_number_to_provider=True,
            is_flexible=False,
            disable_notification=False,
            protect_content=True,
            reply_markup=None,
            request_timeout=8,
            provider_data=json.dumps(provider_data),
            payload=unique_payload

        )
    except Exception as _ex:
        print("ERROR EXCEPTION ", _ex)
    finally:
        print("All GOOD")


@router.pre_checkout_query()
async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    try:
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    except Exception as _ex:
        print("ERROR EXCEPTION: ", type(_ex).__name__, _ex.args)
    finally:
        print("Обработка платежа успешно!")


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    unique_payload = message.successful_payment.invoice_payload
    payload_parts = unique_payload.split("-")
    payment_type = payload_parts[0]
    user_id = payload_parts[1]
    # Обновляем статус платежа в базе данных
    if payment_type == "subscribe":
        update_payment_status_in_db(unique_payload, 'Successful')
        update_user_subscription(user_id)

        msg = (
            f"Спасибо за оплату {message.successful_payment.total_amount // 100} {message.successful_payment.currency}."
            f"\r\nОплата прошла успешно!")
        await message.answer(msg)
        await message.answer(f"Выбери интересующее действие", reply_markup=main_keyboard)
    elif payment_type == "referral":
        update_payment_status_in_db(unique_payload, 'Successful')
        update_refurl_info(user_id)
        msg = (
            f"Спасибо за оплату {message.successful_payment.total_amount // 100} {message.successful_payment.currency}."
            f"\nОплата прошла успешно!")
        await message.answer(msg)
        await message.answer(text=f"Вот ваша реферальная ссылка.\n"
                                  f"Скопируйте ее и отправьте человеку, которому хотите подарить 14 дней бесплатного пользования ботом")
        await message.answer(text=f"{get_ref_url(user_id)}")
