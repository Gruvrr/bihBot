from datetime import datetime, time, timedelta
from aiogram import Bot, Router
from aiogram.types import CallbackQuery
import os
from core.utils.db import close, connect
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()
token = os.getenv("TOKEN")
router = Router()


@router.callback_query(lambda c: c.data == 'meditation')
async def send_meditation(callback: CallbackQuery):
    conn = connect()
    cursor = conn.cursor()
    telegram_user_id = callback.from_user.id
    cursor.execute("SELECT id FROM users WHERE telegram_user_id = %s", (telegram_user_id,))
    user_id = cursor.fetchone()
    try:
        if await check_send_time(user_id, callback, conn, cursor):
            cursor.close()
            conn.close()
            return
        while True:
            cursor.execute("SELECT MAX(sent_date) FROM usercontent WHERE user_id = %s", (user_id,))
            last_message_time = cursor.fetchone()[0]
            if last_message_time and last_message_time.date() == datetime.now().date() and datetime.now().time() < time(
                    6, 0):
                await callback.message.answer("Новое сообщение будет доступно после 6 утра.")
                return
            cursor.execute("SELECT chat_id, message_id FROM audio_message ORDER BY RANDOM() LIMIT 1")
            row = cursor.fetchone()
            if row:
                chat_id, message_id = row
                cursor.execute("SELECT id FROM usercontent WHERE content_id = %s AND user_id = %s",
                               (message_id, user_id))
                result = cursor.fetchone()
                if not result:
                    query = ("INSERT INTO usercontent (user_id, content_id) VALUES (%s, %s)")
                    cursor.execute(query, (user_id, message_id))

                    await callback.bot.forward_message(telegram_user_id, chat_id, message_id)
                    conn.commit()
                    break
            else:
                await callback.answer("Сейчас нет доступных медитаций.")
                break
    except Exception as e:
        await callback.answer("Произошла ошибка.")
        print("Ошибка при выборе аудио из базы данных:", e)
    finally:
        cursor.close()
        conn.close()


@router.callback_query(lambda c: c.data == 'affirmation')
async def send_affirmation(callback: CallbackQuery):
    conn = connect()
    cursor = conn.cursor()
    telegram_user_id = callback.from_user.id
    cursor.execute("SELECT id FROM users WHERE telegram_user_id = %s", (telegram_user_id,))
    user_id = cursor.fetchone()
    try:
        if await check_send_time(user_id, callback, conn, cursor):
            cursor.close()
            conn.close()
            return
        while True:
            cursor.execute("SELECT MAX(sent_date) FROM usercontent WHERE user_id = %s", (user_id,))
            last_message_time = cursor.fetchone()[0]
            if last_message_time and last_message_time.date() == datetime.now().date() and datetime.now().time() < time(
                    6, 0):
                await callback.message.answer("Новое сообщение будет доступно после 6 утра.")
                return
            cursor.execute("SELECT chat_id, message_id FROM video_message ORDER BY RANDOM() LIMIT 1")
            row = cursor.fetchone()
            if row:
                chat_id, message_id = row
                cursor.execute("SELECT id FROM usercontent WHERE content_id = %s AND user_id = %s",
                               (message_id, user_id))
                result = cursor.fetchone()
                if not result:
                    query = ("INSERT INTO usercontent (user_id, content_id) VALUES (%s, %s)")
                    cursor.execute(query, (user_id, message_id))

                    await callback.bot.forward_message(telegram_user_id, chat_id, message_id)
                    conn.commit()
                    break
            else:
                await callback.answer("Сейчас нет доступных аффирмаций.")
                break
    except Exception as e:
        await callback.answer("Произошла ошибка.")
        print("Ошибка при выборе видео из базы данных:", e)
    finally:
        cursor.close()
        conn.close()


@router.callback_query(lambda c: c.data == 'task')
async def send_task(callback: CallbackQuery):
    conn = connect()
    cursor = conn.cursor()
    telegram_user_id = callback.from_user.id
    cursor.execute("SELECT id FROM users WHERE telegram_user_id = %s", (telegram_user_id,))
    user_id = cursor.fetchone()
    try:
        if await check_send_time(user_id, callback, conn, cursor):
            cursor.close()
            conn.close()
            return
        while True:
            cursor.execute("SELECT MAX(sent_date) FROM usercontent WHERE user_id = %s", (user_id,))
            last_message_time = cursor.fetchone()[0]
            if last_message_time and last_message_time.date() == datetime.now().date() and datetime.now().time() < time(
                    6, 0):
                await callback.message.answer("Новое сообщение будет доступно после 6 утра.")
                return
            cursor.execute("SELECT chat_id, message_id FROM text_message ORDER BY RANDOM() LIMIT 1")
            row = cursor.fetchone()
            if row:
                chat_id, message_id = row
                cursor.execute("SELECT id FROM usercontent WHERE content_id = %s AND user_id = %s",
                               (message_id, user_id))
                result = cursor.fetchone()
                if not result:
                    query = ("INSERT INTO usercontent (user_id, content_id) VALUES (%s, %s)")
                    cursor.execute(query, (user_id, message_id))

                    await callback.bot.forward_message(telegram_user_id, chat_id, message_id)
                    conn.commit()
                    break
            else:
                await callback.answer("Сейчас нет доступных заданий.")
                break
    except Exception as e:
        await callback.answer("Произошла ошибка.")
        print("Ошибка при выборе задания из базы данных:", e)
    finally:
        cursor.close()
        conn.close()


@router.callback_query(lambda c: c.data == 'mood')
async def send_image(callback: CallbackQuery):
    conn = connect()
    cursor = conn.cursor()
    telegram_user_id = callback.from_user.id
    cursor.execute("SELECT id FROM users WHERE telegram_user_id = %s", (telegram_user_id,))
    user_id = cursor.fetchone()[0]

    try:
        if await check_send_time(user_id, callback, conn, cursor):
            cursor.close()
            conn.close()
            return
        while True:

            cursor.execute("SELECT chat_id, message_id FROM image_message ORDER BY RANDOM() LIMIT 1")
            row = cursor.fetchone()
            if row:
                chat_id, message_id = row
                cursor.execute("SELECT id FROM usercontent WHERE content_id = %s AND user_id = %s",
                               (message_id, user_id))
                result = cursor.fetchone()
                if not result:
                    query = ("INSERT INTO usercontent (user_id, content_id) VALUES (%s, %s)")
                    cursor.execute(query, (user_id, message_id))

                    await callback.bot.forward_message(telegram_user_id, chat_id, message_id)
                    conn.commit()
                    break
            else:
                await callback.answer("Настрой дня отсутствует в базе.")
                break
    except Exception as e:
        await callback.answer("Произошла ошибка.")
        print("Ошибка при выборе настроя дня из базы данных:", e)
    finally:
        cursor.close()
        conn.close()


async def check_send_time(user_id, callback, conn, cursor):
    try:
        cursor.execute("SELECT MAX(sent_date) FROM usercontent WHERE user_id = %s", (user_id,))
        last_message_time = cursor.fetchone()[0]
        if last_message_time and last_message_time.date() == datetime.now().date():
            next_day_6am = (last_message_time + timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)
            if datetime.now() < next_day_6am:
                await callback.answer("Новое сообщение будет доступно завтра после 6 утра.")
                return True
        return False
    except Exception as e:
        logging.error(f"Ошибка при проверке времени отправки: {e}")
        return True  # Возвращаем T
