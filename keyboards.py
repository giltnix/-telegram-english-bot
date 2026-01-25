# keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def exam_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="ОГЭ", callback_data="exam:oge"),
                InlineKeyboardButton(text="ЕГЭ", callback_data="exam:ege")
            ]
        ]
    )

def tasks_keyboard(exam_key, EXAMS):
    buttons = []
    for task in EXAMS[exam_key].keys():
        buttons.append([InlineKeyboardButton(text=task.capitalize(), callback_data=f"task:{exam_key}:{task}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def options_keyboard(exam_key, task_key, ex_index, EXAMS):
    ex = EXAMS[exam_key][task_key][ex_index]
    buttons = []
    for opt in ex["options"]:
        buttons.append([InlineKeyboardButton(text=opt, callback_data=f"answer:{exam_key}:{task_key}:{ex_index}:{opt[0]}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def next_exercise_keyboard(exam_key, task_key):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➡️ Следующее задание", callback_data=f"next:{exam_key}:{task_key}")]
        ]
    )
