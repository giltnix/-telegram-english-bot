from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def exam_keyboard():
    """Клавиатура выбора экзамена"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("ОГЭ"), KeyboardButton("ЕГЭ"))
    return kb

def tasks_keyboard(tasks: list):
    """Клавиатура с заданиями"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for task in tasks:
        kb.add(KeyboardButton(task))
    kb.add(KeyboardButton("Назад"))
    return kb

def answers_keyboard(n_options: int):
    """Динамическая клавиатура для вариантов ответа (A, B, C ...)"""
    letters = ["A", "B", "C", "D", "E", "F"][:n_options]  # максимум 6 вариантов
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for letter in letters:
        kb.add(KeyboardButton(letter))
    return kb

