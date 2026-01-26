from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def start_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="ОГЭ")],
            [KeyboardButton(text="ЕГЭ")],
            [KeyboardButton(text="Конкретные темы")]
        ],
        resize_keyboard=True
    )


def tasks_keyboard(tasks: list):
    keyboard = []
    # Разбиваем задачи на строки по 2 кнопки
    for i in range(0, len(tasks), 2):
        row = [KeyboardButton(text=tasks[i])]
        if i + 1 < len(tasks):
            row.append(KeyboardButton(text=tasks[i + 1]))
        keyboard.append(row)
    
    # Добавляем кнопку Назад
    keyboard.append([KeyboardButton(text="Назад")])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


def answers_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="A"), KeyboardButton(text="B"), KeyboardButton(text="C")]
        ],
        resize_keyboard=True
    )
