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
    for i in range(0, len(tasks), 2):
        row = []
        row.append(KeyboardButton(text=tasks[i]))
        if i + 1 < len(tasks):
            row.append(KeyboardButton(text=tasks[i + 1]))
        keyboard.append(row)
    
    keyboard.append([KeyboardButton(text="⬅️ Назад")])
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

def answers_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="A")],
            [KeyboardButton(text="B")],
            [KeyboardButton(text="C")]
        ],
        resize_keyboard=True
    )

def explanation_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📖 Объяснение")],  # ТОЧНО ТАКЖЕ КАК В ХЭНДЛЕРЕ
            [KeyboardButton(text="⬅️ Назад к темам")]
        ],
        resize_keyboard=True
    )
