from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def exam_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("ОГЭ"))
    kb.add(KeyboardButton("ЕГЭ"))
    return kb

def tasks_keyboard(tasks: list):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for task in tasks:
        kb.add(KeyboardButton(task))
    kb.add(KeyboardButton("⬅️ Назад"))
    return kb

def answers_keyboard(n_options: int):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    letters = ["A", "B", "C", "D", "E", "F"][:n_options]
    for letter in letters:
        kb.add(KeyboardButton(letter))
    return kb
