from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def exam_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура выбора экзамена"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton(text="ОГЭ"))
    kb.add(KeyboardButton(text="ЕГЭ"))
    return kb

def tasks_keyboard(tasks: list) -> ReplyKeyboardMarkup:
    """Клавиатура с заданиями"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for task in tasks:
        kb.add(KeyboardButton(text=task))
    kb.add(KeyboardButton(text="⬅️ Назад"))
    return kb

def answers_keyboard(n_options: int) -> ReplyKeyboardMarkup:
    """Динамическая клавиатура для вариантов ответа"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    letters = ["A", "B", "C", "D", "E", "F"][:n_options]  # максимум 6 вариантов
    for letter in letters:
        kb.add(KeyboardButton(text=letter))
    return kb
