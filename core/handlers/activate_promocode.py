import logging
from aiogram import types, Router
from aiogram.filters import state
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from core.utils.db import connect, close
from aiogram.types import CallbackQuery, Message

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = Router()


class Form(StatesGroup):
    waiting_for_ref_link = State()


@router.callback_query(lambda c: c.data == 'activate_promocode')
async def start_referral_check(callback: CallbackQuery, state: FSMContext):
    logger.info("Activating promocode")
    await state.set_state(Form.waiting_for_ref_link)
    await callback.message.answer("Пожалуйста, пришлите мне вашу реферальную ссылку.")


@router.message(Form.waiting_for_ref_link)
async def process_referral_link(message: Message, state: FSMContext):
    ref_link = message.text
    telegram_user_id = message.from_user.id
    logger.info(f"Processing referral link for user {telegram_user_id}")

    conn = connect()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE telegram_user_id = %s", (telegram_user_id,))
        result = cursor.fetchone()
        user_id = result[0] if result else None

        if user_id:
            cursor.execute("SELECT id FROM promocodes WHERE promocode = %s AND activate_status = False", (ref_link,))
            promocode_record = cursor.fetchone()

            if promocode_record:
                promocode_id = promocode_record[0]
                cursor.execute("SELECT create_user_id FROM promocodes WHERE id = %s", (promocode_id,))
                create_user_id = cursor.fetchone()

                if create_user_id and create_user_id[0] == user_id:
                    await message.answer(text=f"Вы являетесь создателем этого промокода. \nНевозможно активировать.")
                else:
                    cursor.execute("UPDATE promocodes SET activate_user_id = %s, activate_status = True WHERE id = %s",
                                   (user_id, promocode_id))
                    cursor.execute(
                        "UPDATE users SET subscription_days_count = subscription_days_count + 14, subscription_active = True WHERE id = %s",
                        (user_id,))

                    conn.commit()
                    logger.info(f"Promocode activated for user {user_id}")
                    await message.reply("Реферальная ссылка активирована.")
            else:
                logger.warning(f"Referral link not found for user {user_id}")
                await message.reply("Реферальная ссылка не найдена.")
        else:
            logger.warning(f"User not found for Telegram ID {telegram_user_id}")
            await message.reply("Пользователь с таким Telegram ID не найден.")

    except Exception as e:
        logger.error(f"[ERROR] {e}", exc_info=True)
        conn.rollback()
    finally:
        cursor.close()
        close(conn)
        await state.clear()
