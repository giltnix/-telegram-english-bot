from config import BOT_TOKEN

print("BOT_TOKEN repr:", repr(BOT_TOKEN))
print("BOT_TOKEN len:", len(BOT_TOKEN))

bot = Bot(token=BOT_TOKEN)

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


def tasks_keyboard(tasks: list) -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text=task)] for task in tasks]
    keyboard.append([KeyboardButton(text="Назад")])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


def answers_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="A"),
                KeyboardButton(text="B"),
                KeyboardButton(text="C")
            ]
        ],
        resize_keyboard=True
    )
