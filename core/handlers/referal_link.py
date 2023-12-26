import json
from aiogram.types import CallbackQuery, LabeledPrice, PreCheckoutQuery, Message
from aiogram import Router, Bot
import time
from aiogram import F
from dotenv import load_dotenv
from os import getenv
from core.keyboards.inline.inline_keyboard import main_keyboard
from core.utils.db import close, connect
import random
import string

load_dotenv()
pt = getenv("PROVIDER_TOKEN")
router = Router()


def generate_random_string(length=10):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for i in range(length))

    return random_string


def generate_payload(user_id, payment_type):
    return f"{payment_type}-{user_id}-{int(time.time())}"


def add_payment_to_db(user_id, unique_payload, amount, currency="RUB"):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO payments (telegram_user_id, unique_payload, amount, status) VALUES (%s, %s, %s, %s)",
            (user_id, unique_payload, amount, 'Pending'))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при добавлении записи в базу данных: {e}")
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


def update_refurl_info(telegram_user_id):
    conn = connect()
    cursor = conn.cursor()
    user_id = get_user_id(telegram_user_id)
    try:

        ref_url = generate_random_string()
        query = "INSERT INTO promocodes (create_user_id, promocode, activate_status) VALUES (%s, %s, %s)"
        cursor.execute(query, (user_id, ref_url, False))

        conn.commit()
    except Exception as e:
        print(f"[ERROR] {e}")
        conn.rollback()
    finally:
        cursor.close()
        close(conn)


def get_ref_url(telegram_user_id):
    conn = connect()
    cursor = conn.cursor()
    user_id = get_user_id(telegram_user_id)
    if user_id is None:
        print(f"No user found with telegram_user_id: {telegram_user_id}")
        return None

    try:
        query = "SELECT promocode FROM promocodes WHERE create_user_id = %s AND activate_status = False"
        cursor.execute(query, (user_id,))  # Обратите внимание на запятую, создающую кортеж
        result = cursor.fetchone()
        return result[0] if result else None

    except Exception as e:
        print(f"[ERROR] {e}")
        conn.rollback()
    finally:
        cursor.close()
        close(conn)


def get_user_id(telegram_user_id: int):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE telegram_user_id = %s", (telegram_user_id,))
        return cursor.fetchone()

    except Exception as _ex:
        print(f"[ERROR], {_ex}")
    finally:
        close(conn)
        cursor.close()


@router.callback_query(lambda c: c.data == "pay_ref")
async def order(callback: CallbackQuery, bot: Bot):
    telegram_user_id: int = callback.from_user.id
    amount: int = 10000
    unique_payload = generate_payload(telegram_user_id, "referral")
    add_payment_to_db(telegram_user_id, unique_payload, amount)
    try:
        provider_data = {
            "receipt": {
                "items": [{
                    "description": "Тут название для подписки",
                    "quantity": "1.00",
                    "amount": {
                        "value": "100.00",  # Укажите здесь цену за единицу товара или услуги
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
            title="Тут название оплаты для реф ссылки",
            description="Покупка реф ссылки за 1 рубль",
            provider_token=pt,
            currency="rub",
            prices=[
                LabeledPrice(
                    label="Цена",
                    amount=10000
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

# @router.message(F.successful_payment)
# async def successful_payment(message: Message):
#     # Обновляем статус платежа в базе данных
#     unique_payload = message.successful_payment.invoice_payload
#     update_payment_status_in_db(unique_payload, 'Successful')
#     user_id = message.from_user.id
#     update_refurl_info(user_id)
#     msg = (f"Спасибо за оплату {message.successful_payment.total_amount // 100} {message.successful_payment.currency}."
#            f"\nОплата прошла успешно!")
#     await message.answer(msg)
#     await message.answer(text=f"Вот ваша реферальная ссылка.\n"
#                               f"Скопируйте ее и отправьте человеку, которому хотите подарить 14 дней бесплатного пользования ботом")
#     await message.answer(text=f"{get_ref_url(user_id)}")
