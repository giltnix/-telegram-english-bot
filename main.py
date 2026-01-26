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
DATA = loader.get_exercises()  # Список всех строк из таблицы

user_state = {}

MODE_MAP = {
    "ОГЭ": "oge",
    "ЕГЭ": "ege",
    "Конкретные темы": "Конкретная тема"
}

# Кнопки для выбора темы в "Конкретных темах"
CONCRETE_TOPICS = ["Present", "Past", "Future", "Условные наклонения", "Модальные глаголы", "Косвенная речь"]

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

    if message.text == "Конкретные темы":
        tasks = CONCRETE_TOPICS
    else:
        tasks = list(DATA.get(mode, {}).keys())

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

    if mode == "Конкретная тема":
        # Фильтруем список строк по выбранной теме
        exercises = [row for row in DATA if row["exam"] == "Конкретная тема" and row["task"] == task]
    else:
        exercises = DATA.get(mode, {}).get(task, [])

    if not exercises:
        await message.answer("Нет заданий по этой теме.")
        return

    # Берём случайное упражнение
    exercise = random.choice(exercises)
    state["current"] = exercise

    # Разбираем варианты
    options = [opt.strip() for opt in exercise["options"].split(";")]

    text = exercise["question"] + "\n\n"
    for i, letter in enumerate(["A", "B", "C"]):
        text += f"{letter}) {options[i]}\n"

    state["current"]["options"] = options  # сохраняем для проверки
    state["current"]["correct"] = exercise["answer"].strip()  # сохраняем правильный ответ

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

    # Снова показываем темы
    mode = state["mode"]
    if mode == "Конкретная тема":
        tasks = CONCRETE_TOPICS
    else:
        tasks = list(DATA.get(mode, {}).keys())

    await message.answer(
        "Выбери следующую тему:",
        reply_markup=tasks_keyboard(tasks)
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())











