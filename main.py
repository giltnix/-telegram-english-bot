import asyncio
import random

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

from config import BOT_TOKEN
from sheets import SheetsLoader
from keyboards import start_keyboard, tasks_keyboard, answers_keyboard


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

loader = SheetsLoader("OGE/EGE")
DATA = loader.get_exercises()

user_state = {}

MODE_MAP = {
    "ОГЭ": "oge",
    "ЕГЭ": "ege",
    "Конкретные темы": "Конкретная тема"
}


@dp.message(CommandStart())
async def start(message: types.Message):
    user_state.clear()
    await message.answer(
        "Привет! Выбери режим:",
        reply_markup=start_keyboard()
    )


@dp.message(lambda m: m.text in MODE_MAP)
async def choose_mode(message: types.Message):
    user_id = message.from_user.id
    mode = MODE_MAP[message.text]

    user_state[user_id] = {"mode": mode}

    tasks = list(DATA.get(mode, {}).keys())

    if not tasks:
        await message.answer("Нет заданий.")
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

    exercises = DATA.get(mode, {}).get(task)

    if not exercises:
        await message.answer("Нет заданий по этой теме.")
        return

    exercise = random.choice(exercises)
    state["current"] = exercise

    text = exercise["question"] + "\n\n"
    for i, letter in enumerate(["A", "B", "C"]):
        text += f"{letter}) {exercise['options'][i]}\n"

    await message.answer(text, reply_markup=answers_keyboard())


@dp.message(lambda m: m.text in ["A", "B", "C"])
async def check_answer(message: types.Message):
    user_id = message.from_user.id
    state = user_state.get(user_id)

    if not state or "current" not in state:
        return

    correct = state["current"]["correct"]

    if message.text == correct:
        await message.answer("Верно!")
    else:
        await message.answer(f"Неверно. Правильный ответ: {correct}")

    state.pop("current")

    mode = state["mode"]
    tasks = list(DATA.get(mode, {}).keys())

    await message.answer(
        "Выбери следующую тему:",
        reply_markup=tasks_keyboard(tasks)
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())







