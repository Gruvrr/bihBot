from aiogram.types import Message
from aiogram.filters.command import Command, CommandStart
from aiogram import Router, Bot
from core.keyboards.inline.inline_keyboard import registration_button, main_keyboard, pay_button
from core.utils.db import connect, close

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE telegram_user_id = %s", (user_id,))
    user_exists = cursor.fetchone()
    try:
        if not user_exists:
            cursor.execute(
                "INSERT INTO users (first_name, telegram_user_id, subscription_days_count, subscription_purchases_count,"
                " subscription_active) VALUES (%s, %s, %s, %s, %s)",
                (first_name, user_id, 0, 0, False)
            )
            conn.commit()
            close(conn)

            await message.answer(text=f"Привет, {first_name}.\n"
                                      f"Для того, чтобы продолжить пользоваться ботом, пройди короткую регистрацию.",
                                 reply_markup=registration_button)
        else:
            cursor.execute("SELECT last_name, subscription_active FROM users WHERE telegram_user_id = %s", (user_id,))
            last_name, sub_days = cursor.fetchone()
            if not last_name:
                await message.answer(text=f"Привет, {first_name}.\n"
                                          f"Для того, чтобы продолжить пользоваться ботом, пройди короткую регистрацию.",
                                     reply_markup=registration_button)

            else:
                if sub_days is True:
                    await message.answer(text=f"Сообщения приходят каждый день в 6 часов по мск")
                else:
                    await message.answer(text=f"У вас закончилась подписка. Оплатить новую вы можете по кнопке ниже",
                                         reply_markup=pay_button)
    except Exception as ex:
        print(f'[ERROR] {ex}')
    finally:
        print(f"All good")


@router.channel_post()
async def track_channel_posts(message: Message):
    if message.content_type == 'photo':
        await save_image_id(message.chat.id, message.message_id, message.content_type)
    elif message.content_type == 'video':
        await save_video_id(message.chat.id, message.message_id, message.content_type)
    elif message.content_type == 'audio' or message.content_type == 'voice':
        await save_audio_id(message.chat.id, message.message_id, message.content_type)
    elif message.content_type == 'text':
        await save_text_id(message.chat.id, message.message_id, message.content_type)


@router.message(Command('menu'))
async def main_menu(message: Message):
    await message.answer(f"выбери действие", reply_markup=main_keyboard)


async def save_text_id(chat_id, message_id, content_type):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO text_message (chat_id, message_id, content_type) VALUES (%s, %s, %s)",
                       (chat_id, message_id, content_type))
        conn.commit()
        print("Сообщение сохранено в базе данных.")
    except Exception as e:
        print("Ошибка при сохранении сообщения в базу данных:", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


async def save_image_id(chat_id, message_id, content_type):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO image_message (chat_id, message_id, content_type) VALUES (%s, %s, %s)",
                       (chat_id, message_id, content_type))
        conn.commit()
        print("Сообщение сохранено в базе данных.")
    except Exception as e:
        print("Ошибка при сохранении сообщения в базу данных:", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


async def save_video_id(chat_id, message_id, content_type):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO video_message (chat_id, message_id, content_type) VALUES (%s, %s, %s)",
                       (chat_id, message_id, content_type))
        conn.commit()
        print("Сообщение сохранено в базе данных.")
    except Exception as e:
        print("Ошибка при сохранении сообщения в базу данных:", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


async def save_audio_id(chat_id, message_id, content_type):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO audio_message (chat_id, message_id, content_type) VALUES (%s, %s, %s)",
                       (chat_id, message_id, content_type))
        conn.commit()
        print("Сообщение сохранено в базе данных.")
    except Exception as e:
        print("Ошибка при сохранении сообщения в базу данных:", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
