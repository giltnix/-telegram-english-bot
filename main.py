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
EXAMS = loader.get_exercises()

# Состояние пользователей
user_state = {}

# Соответствие русских названий экзаменов ключам EXAMS
EXAM_MAP = {
    "ОГЭ": "oge",
    "ЕГЭ": "ege"
}


@dp.message(CommandStart())
async def start(message: types.Message):
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
        await message.answer("Задания для этого экзамена не найдены.")
        return

    await message.answer(
        "Выбери задание:",
        reply_markup=tasks_keyboard(tasks)
    )


@dp.message(lambda m: m.text == "Назад")
async def back(message: types.Message):
    user_state.pop(message.from_user.id, None)
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
        await message.answer("Нет заданий для этого задания.")
        return

    exercise = random.choice(exercises)
    user_state[user_id]["task"] = task
    user_state[user_id]["current"] = exercise

    # Формируем текст вопроса и вариантов
    text = exercise["question"] + "\n\n"
    letters = ["A", "B", "C", "D", "E", "F"]
    for i, option in enumerate(exercise["options"]):
        if i < len(letters):
            text += f"{letters[i]}) {option}\n"

    # Отправляем вопрос с клавиатурой вариантов
    await message.answer(
        text,
        reply_markup=answers_keyboard(len(exercise["options"]))
    )


@dp.message(lambda m: m.from_user.id in user_state)
async def check_answer(message: types.Message):
    user_id = message.from_user.id
    state = user_state.get(user_id)

    if not state or "current" not in state:
        return

    exercise = state["current"]
    correct = exercise["correct"].upper()
    user_answer = message.text.upper()

    if user_answer == correct:
        await message.answer("Верно!")
    else:
        await message.answer(f"Неверно. Правильный ответ: {correct}")

    # Убираем текущее упражнение
    state.pop("task", None)
    state.pop("current", None)

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




