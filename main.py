import asyncio
import random

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

from config import BOT_TOKEN
from sheets import SheetsLoader
from keyboards import exam_keyboard, tasks_keyboard, answers_keyboard

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

loader = SheetsLoader("OGE/EGE")
EXAMS = loader.get_exercises()

user_state = {}


@dp.message(CommandStart())
async def start(message: types.Message):
    user_state.clear()
    await message.answer(
        "Привет! Выбери экзамен:",
        reply_markup=exam_keyboard()
    )


@dp.message(lambda m: m.text in ["ОГЭ", "ЕГЭ"])
async def choose_exam(message: types.Message):
    user_id = message.from_user.id
    exam = "oge" if message.text == "ОГЭ" else "ege"

    user_state[user_id] = {"exam": exam}

    tasks = list(EXAMS[exam].keys())

    await message.answer(
        "Выбери задание:",
        reply_markup=tasks_keyboard(tasks)
    )


@dp.message(lambda m: m.text == "⬅️ Назад")
async def back(message: types.Message):
    user_state.pop(message.from_user.id, None)
    await message.answer(
        "Выбери экзамен:",
        reply_markup=exam_keyboard()
    )


@dp.message(lambda m: m.from_user.id in user_state and "current" not in user_state[m.from_user.id])
async def choose_task(message: types.Message):
    user_id = message.from_user.id
    exam = user_state[user_id]["exam"]
    task = message.text

    if task not in EXAMS[exam]:
        return

    exercise = random.choice(EXAMS[exam][task])
    user_state[user_id]["current"] = exercise

    text = (
        f"{exercise['question']}\n\n"
        f"A) {exercise['options'][0]}\n"
        f"B) {exercise['options'][1]}\n"
        f"C) {exercise['options'][2]}\n"
        f"D) {exercise['options'][3]}"
    )

    await message.answer(
        text,
        reply_markup=answers_keyboard()
    )


@dp.message(lambda m: m.text in ["A", "B", "C", "D"])
async def check_answer(message: types.Message):
    user_id = message.from_user.id
    state = user_state.get(user_id)

    if not state or "current" not in state:
        return

    correct = state["current"]["correct"]

    if message.text == correct:
        await message.answer("✅ Верно!")
    else:
        await message.answer(f"❌ Неверно. Правильный ответ: {correct}")

    state.pop("current")

    tasks = list(EXAMS[state["exam"]].keys())
    await message.answer(
        "Выбери следующее задание:",
        reply_markup=tasks_keyboard(tasks)
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())




