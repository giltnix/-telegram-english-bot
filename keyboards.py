from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def start_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="ОГЭ")],
            [KeyboardButton(text="ЕГЭ")],
            [KeyboardButton(text="Конкретные темы")]
        ],
        resize_keyboard=True
    )


def tasks_keyboard(tasks: list[str]) -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text=task)] for task in tasks]
    keyboard.append([KeyboardButton(text="Назад")])
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


def answers_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="A"), KeyboardButton(text="B"), KeyboardButton(text="C")]
        ],
        resize_keyboard=True
    )
