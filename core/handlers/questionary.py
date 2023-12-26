import time
import datetime
from datetime import datetime
from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
import re
from core.keyboards.inline.inline_keyboard import user_gender_keyboard, pay_button
from core.utils.states import User
from core.utils.db import close, connect

router = Router()

PHONE_REGEX = r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(?([0-9][0-9][0-9])\)?\s*(?:[.-]\s*)?)?([0-9][0-9][0-9])\s*(?:[.-]\s*)?([0-9][0-9][0-9][0-9]))'


@router.callback_query(lambda c: c.data == "registration")
async def new_profile(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text="Укажите ваш пол", reply_markup=user_gender_keyboard)


@router.callback_query(F.data.casefold().in_(["male", "female"]))
async def say_first_name(callback: CallbackQuery, state: FSMContext):
    gender = "мужской" if callback.data == "male" else "женский"
    print(gender)
    await state.update_data(gender=gender)
    await state.set_state(User.first_name)
    await callback.message.edit_text(text="Введите ваше имя")
    await callback.answer()


@router.message(User.first_name)
async def say_last_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await state.set_state(User.last_name)
    await message.answer(text="Введите вашу фамилию")


@router.message(User.last_name)
async def birth_day(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await state.set_state(User.birth_date)
    await message.answer(text="Введите вашу дату рождения в формате ДД.ММ.ГГГГ")


@router.message(User.birth_date)
async def phone_number(message: Message, state: FSMContext):
    text = message.text
    try:
        birth_date = datetime.strptime(text, '%d.%m.%Y')
    except ValueError:
        await message.reply("Некорректный формат даты. Пожалуйста, попробуйте еще раз.")
        return

    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    if 0 <= age <= 95:
        await state.update_data(birth_date=birth_date)
        await state.set_state(User.phone_number)
        await message.answer(text="Введите ваш номер телефона")
    else:
        await message.answer("Введите реалистичную дату рождения.")


@router.message(User.phone_number)
async def get_email(message: Message, state: FSMContext):
    if re.match(PHONE_REGEX, message.text):
        phone = message.text.replace('+', '')  # Удаляем знак "+"
        await state.update_data(phone_number=phone)
        await state.set_state(User.email)
        await message.answer(text="Введите ваш email")
    else:
        await message.answer("Введите корректный номер телефона.")


@router.message(User.email)
async def get_city(message: Message, state: FSMContext):
    if "@" in message.text:  # Простая проверка email на наличие символа "@"
        await state.update_data(email=message.text)
        await state.set_state(User.city)
        await message.answer(text="Введите ваш город")
    else:
        await message.answer("Введите корректный email")


@router.message(User.city)
async def res(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    data = await state.get_data()
    update_user_data(
        user_id=message.from_user.id,
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        birth_date=data.get("birth_date"),
        phone_number=data.get("phone_number"),
        email=data.get("email"),
        city=data.get("city")
    )
    await state.set_state(None)
    await message.answer(text=f"{message.from_user.first_name}, ты успешно прошел регистрацию в боте.\n"
                              f"Теперь тебе нужно оплатить подписку, нажав на кнопку ниже.", reply_markup=pay_button)


def update_user_data(user_id, first_name, last_name, birth_date, phone_number, email, city):
    conn = connect()
    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE users 
            SET first_name = %s, 
                last_name = %s, 
                birth_date = %s, 
                phone_number = %s, 
                email = %s, 
                city = %s
            WHERE telegram_user_id = %s
        """, (first_name, last_name, birth_date, phone_number, email, city, user_id))

        conn.commit()
    except Exception as e:
        print("Ошибка при обновлении данных пользователя:", e)
    finally:
        close(conn)
