import asyncio
import random

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

from config import BOT_TOKEN
from sheets import SheetsLoader
from keyboards import start_keyboard, tasks_keyboard, answers_keyboard

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Загружаем ВСЮ таблицу
loader = SheetsLoader("OGE/EGE")
DATA = loader.get_raw_rows()
# DATA = list[dict] с ключами: exam, task, question, options, answer

user_state = {}


@dp.message(CommandStart())
async def start(message: types.Message):
    user_state.clear()
    await message.answer(
        "Привет! Выбери режим:",
        reply_markup=start_keyboard()
    )


@dp.message(lambda m: m.text in ["ОГЭ", "ЕГЭ", "Конкретные темы"])
async def choose_mode(message: types.Message):
    user_id = message.from_user.id
    mode = message.text

    user_state[user_id] = {"mode": mode}

    if mode == "Конкретные темы":
        tasks = sorted(
            {row["task"] for row in DATA if row["exam"] == "Конкретная тема"}
        )
    else:
        exam_key = mode.lower()
        tasks = sorted(
            {row["task"] for row in DATA if row["exam"] == exam_key}
        )

    if not tasks:
        await message.answer("Нет заданий для этого режима")
        return

    await message.answer(
        "Выбери тему:",
        reply_markup=tasks_keyboard(tasks)
    )


@dp.message(lambda m: m.text == "Назад")
async def back(message: types.Message):
    user_state.pop(message.from_user.id, None)
    await message.answer(
        "Выбери режим:",
        reply_markup=start_keyboard()
    )


@dp.message(lambda m: m.from_user.id in user_state and "current" not in user_state[m.from_user.id])
async def choose_task(message: types.Message):
    user_id = message.from_user.id
    state = user_state[user_id]
    mode = state["mode"]
    task = message.text

    if mode == "Конкретные темы":
        exercises = [
            row for row in DATA
            if row["exam"] == "Конкретная тема" and row["task"] == task
        ]
    else:
        exercises = [
            row for row in DATA
            if row["exam"] == mode.lower() and row["task"] == task
        ]

    if not exercises:
        await message.answer("Пока что нет заданий по этой теме")
        return

    exercise = random.choice(exercises)
    state["current"] = exercise

    options = [o.strip() for o in exercise["options"].split(";")]

    text = exercise["question"] + "\n\n"
    for letter, option in zip(["A", "B", "C"], options):
        text += f"{letter}) {option}\n"

    await message.answer(
        text,
        reply_markup=answers_keyboard()
    )


@dp.message(lambda m: m.text in ["A", "B", "C"])
async def check_answer(message: types.Message):
    user_id = message.from_user.id
    state = user_state.get(user_id)

    if not state or "current" not in state:
        return

    correct = state["current"]["answer"].upper()

    if message.text == correct:
        await message.answer("Верно!")
    else:
        await message.answer(f"Неверно. Правильный ответ: {correct}")

    state.pop("current")

    mode = state["mode"]

    if mode == "Конкретные темы":
        tasks = sorted(
            {row["task"] for row in DATA if row["exam"] == "Конкретная тема"}
        )
    else:
        tasks = sorted(
            {row["task"] for row in DATA if row["exam"] == mode.lower()}
        )

    await message.answer(
        "Выбери следующую тему:",
        reply_markup=tasks_keyboard(tasks)
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())



