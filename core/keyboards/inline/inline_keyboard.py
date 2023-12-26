from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

user_gender_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Мужской", callback_data="male"),
    ],
    [
        InlineKeyboardButton(text="Женский", callback_data="female")
    ]
],
    resize_keyboard=True
)

registration_button = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Пройти регистрацию", callback_data="registration")
    ]
])


pay_button = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Оплатить подписку", callback_data="pay")
    ]
])


main_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Медитация", callback_data="meditation"),
        InlineKeyboardButton(text=f"Аффирмации", callback_data="affirmation")
    ],
    [
        InlineKeyboardButton(text="Задание дня", callback_data="task")
    ],
    [
        InlineKeyboardButton(text="Настрой дня", callback_data="mood")
    ]
])