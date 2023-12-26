from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

router = Router()


@router.message(Command('main_menu'))
async def send_menu(message: Message):
    buttons = [
        [InlineKeyboardButton(text="Активировать промокод", callback_data="activate_promocode")],
        [InlineKeyboardButton(text="Сделать подарок", callback_data="pay_ref")],
        # Убедитесь, что вы вставите действительный URL вашего канала ниже
        [InlineKeyboardButton(text="Перейти в канал", url="https://t.me/+-f4XxVCNMVBlYWMy")],
        [InlineKeyboardButton(text="Контакты", url="http://mgmanufactory.tilda.ws/")]
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Выберите опцию:", reply_markup=markup)
