from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def exam_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="ОГЭ")],
            [KeyboardButton(text="ЕГЭ")]
        ],
        resize_keyboard=True
    )


def tasks_keyboard(tasks):
    keyboard = []
    for task in tasks:
        keyboard.append([KeyboardButton(text=task)])

    keyboard.append([KeyboardButton(text="⬅️ Назад")])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


def answers_keyboard():
    # Всегда 3 варианта: A, B, C
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="A"), KeyboardButton(text="B"), KeyboardButton(text="C")]
        ],
        resize_keyboard=True
    )
