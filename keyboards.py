from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def start_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("ОГЭ")],
            [KeyboardButton("ЕГЭ")],
            [KeyboardButton("Конкретные темы")]
        ],
        resize_keyboard=True
    )

def tasks_keyboard(tasks):
    keyboard = [[KeyboardButton(task)] for task in tasks]
    keyboard.append([KeyboardButton("Назад")])
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

def answers_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton("A"), KeyboardButton("B"), KeyboardButton("C")]],
        resize_keyboard=True
    )
