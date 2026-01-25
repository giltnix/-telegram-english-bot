from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def exam_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура выбора экзамена"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("ОГЭ"))
    kb.add(KeyboardButton("ЕГЭ"))
    return kb

def tasks_keyboard(tasks: list) -> ReplyKeyboardMarkup:
    """Клавиатура с заданиями (динамически под задачи из таблицы)"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for task in tasks:
        kb.add(KeyboardButton(task))
    kb.add(KeyboardButton("⬅️ Назад"))
    return kb

def answers_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с вариантами ответа (A, B, C)"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("A"), KeyboardButton("B"), KeyboardButton("C"))
    return kb

