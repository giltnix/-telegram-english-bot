import asyncio
import random

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

from config import BOT_TOKEN
from sheets import SheetsLoader
from keyboards import exam_keyboard, tasks_keyboard, answers_keyboard

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Загружаем упражнения
loader = SheetsLoader("OGE/EGE")
EXAMS = loader.get_exercises()  # формат: {"oge": {"Грамматические навыки": [...], ...}, "ege": {...}}

# Состояние пользователя
user_state = {}

# Соответствие кнопок текста к ключам EXAMS
EXAM_MAP = {
    "ОГЭ": "oge",
    "ЕГЭ": "ege"
}


@dp.message(CommandStart())
async def start(message: types.Message):
    user_state.clear()
    await message.answer(
        "Привет! Выбери экзамен:",
        reply_markup=exam_keyboard()
    )


@dp.message(lambda m: m.text in EXAM_MAP)
async def choose_exam(message: types.Message):
    user_id = message.from_user.id
    exam_key = EXAM_MAP[message.text]

    user_state[user_id] = {"exam": exam_key}

    tasks = list(EXAMS.get(exam_key, {}).keys())
    if not tasks:
        await message.answer("Для этого экзамена нет заданий.")
        return

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

    exercises = EXAMS.get(exam, {}).get(task)
    if not exercises:
        await message.answer("Нет заданий для этого задания.")
        return

    exercise = random.choice(exercises)
    user_state[user_id]["current"] = exercise

    # Текст вопроса с 3 вариантами
    text = exercise["question"] + "\n\n"
    letters = ["A", "B", "C"]
    for i in range(3):
        text += f"{letters[i]}) {exercise['options'][i]}\n"

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

    correct = state["current"]["correct"].upper()
    user_answer = message.text.upper()

    if user_answer == correct:
        await message.answer("Верно!")
    else:
        await message.answer(f"Неверно. Правильный ответ: {correct}")

    # Очистка текущего упражнения
    state.pop("current")

    # Предлагаем выбрать следующее задание
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






