import logging
from core.utils.db import connect, close
from aiogram import Bot
from core.keyboards.inline.inline_keyboard import pay_button, main_keyboard

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_messages_to_active_subscribers(bot: Bot):
    conn = connect()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT telegram_user_id FROM users WHERE subscription_active = True")
        users = cursor.fetchall()

        for user in users:
            try:
                await bot.send_message(user[0], "Выбери действие", reply_markup=main_keyboard)
                logger.info(f"Сообщение отправлено пользователю с ID {user[0]}")
            except Exception as e:
                logger.error(f"Ошибка при отправке сообщения пользователю с ID {user[0]}: {e}")

    except Exception as e:
        logger.error(f"Ошибка при извлечении пользователей: {e}")
    finally:
        cursor.close()
        close(conn)


async def update_subscriptions(bot: Bot):
    conn = connect()
    cursor = conn.cursor()

    try:
        # Выбираем пользователей с активной подпиской
        cursor.execute(
            "SELECT telegram_user_id, subscription_days_count FROM users WHERE subscription_active = True AND subscription_days_count > 0")
        users = cursor.fetchall()

        for user_id, days in users:
            new_days = days - 1
            if new_days == 0:
                # Подписка закончилась
                cursor.execute(
                    "UPDATE users SET subscription_days_count = 0, subscription_active = False WHERE telegram_user_id = %s",
                    (user_id,))
                await bot.send_message(user_id,
                                       text=f"Ваша подписка закончилась. Купить новую вы можете по кнопке ниже",
                                       reply_markup=pay_button)
            elif new_days == 2:
                # Осталось 2 дня подписки
                await bot.send_message(user_id, "Ваша подписка закончится через 2 дня. Продлить можно по кнопке ниже",
                                       reply_markup=pay_button)
                cursor.execute("UPDATE users SET subscription_days_count = %s WHERE telegram_user_id = %s",
                               (new_days, user_id))
            else:
                # Обновляем количество дней подписки
                cursor.execute("UPDATE users SET subscription_days_count = %s WHERE telegram_user_id = %s",
                               (new_days, user_id))

            logger.info(f"Обновлена подписка пользователя {user_id}")

        conn.commit()

    except Exception as e:
        logger.error(f"Ошибка при обновлении подписок: {e}")
        conn.rollback()
    finally:
        cursor.close()
        close(conn)
