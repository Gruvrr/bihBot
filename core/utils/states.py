from aiogram.fsm.state import StatesGroup, State


class User(StatesGroup):
    gender = State()
    first_name = State()
    last_name = State()
    birth_date = State()
    phone_number = State()
    email = State()
    city = State()
