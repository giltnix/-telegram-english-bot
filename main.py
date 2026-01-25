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
    await message.answer(
        "Привет! Выбери экзамен ",
        reply_markup=exam_keyboard()
    )


@dp.message(lambda m: m.text in ["ОГЭ", "ЕГЭ"])
async def choose_exam(message: types.Message):
    exam = message.text.lower()
    user_state[message.from_user.id] = {"exam": exam}

    tasks = list(EXAMS.get(exam, {}).keys())
    await message.answer(
        "Выбери задание:",
        reply_markup=tasks_keyboard(tasks)
    )


@dp.message(lambda m: m.text == "⬅️ Назад")
async def back(message: types.Message):
    await message.answer(
        "Выбери экзамен:",
        reply_markup=exam_keyboard()
    )


@dp.message(lambda m: m.from_user.id in user_state and "task" not in user_state[m.from_user.id])
async def choose_task(message: types.Message):
    user_id = message.from_user.id
    exam = user_state[user_id]["exam"]
    task = message.text

    exercises = EXAMS.get(exam, {}).get(task)
    if not exercises:
        await message.answer("Нет заданий ")
        return

    exercise = random.choice(exercises)
    user_state[user_id]["task"] = task
    user_state[user_id]["current"] = exercise

    text = exercise["question"] + "\n\n"
    text += f"A) {exercise['options'][0]}\n"
    text += f"B) {exercise['options'][1]}\n"
    text += f"C) {exercise['options'][2]}\n"
    text += f"D) {exercise['options'][3]}"

    await message.answer(text, reply_markup=answers_keyboard())


@dp.message(lambda m: m.text in ["A", "B", "C", "D"])
async def check_answer(message: types.Message):
    user_id = message.from_user.id
    state = user_state.get(user_id)

    if not state or "current" not in state:
        return

    correct = state["current"]["correct"].upper()

    if message.text == correct:
        await message.answer(" Верно!")
    else:
        await message.answer(f" Неверно. Правильный ответ: {correct}")

    del state["task"]
    del state["current"]

    exam = state["exam"]
    tasks = list(EXAMS.get(exam, {}).keys())

    await message.answer(
        "Выбери следующее задание:",
        reply_markup=tasks_keyboard(tasks)
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
