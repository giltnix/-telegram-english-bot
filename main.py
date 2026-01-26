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
DATA_RAW = loader.get_exercises()  # Список всех строк из таблицы

user_state = {}

CONCRETE_TOPICS = ["Present", "Past", "Future", "Условные наклонения", "Модальные глаголы", "Косвенная речь"]

# Старт
@dp.message(CommandStart())
async def start(message: types.Message):
    user_state.clear()
    await message.answer("Привет! Выбери режим:", reply_markup=start_keyboard())

# Выбор режима
@dp.message(lambda m: m.text in ["ОГЭ", "ЕГЭ", "Конкретные темы"])
async def choose_mode(message: types.Message):
    user_id = message.from_user.id
    mode = message.text
    user_state[user_id] = {"mode": mode}

    if mode == "Конкретные темы":
        tasks = CONCRETE_TOPICS
    else:
        # Получаем темы из словаря для ОГЭ/ЕГЭ
        tasks = list(DATA_RAW.get(mode.lower(), {}).keys())

    await message.answer("Выбери тему:", reply_markup=tasks_keyboard(tasks))

# Назад
@dp.message(lambda m: m.text == "Назад")
async def back(message: types.Message):
    user_state.pop(message.from_user.id, None)
    await message.answer("Выбери режим:", reply_markup=start_keyboard())

# Выбор темы
@dp.message(lambda m: m.from_user.id in user_state and "current" not in user_state[m.from_user.id])
async def choose_task(message: types.Message):
    user_id = message.from_user.id
    state = user_state[user_id]
    mode = state["mode"]
    task = message.text

    # Конкретные темы — фильтруем строки
    if mode == "Конкретные темы":
        exercises = [row for row in DATA_RAW if row[0] == "Конкретная тема" and row[1] == task]
        if not exercises:
            await message.answer("Нет заданий по этой теме.")
            return

        exercise = random.choice(exercises)
        question = exercise[2]
        options = [opt.strip() for opt in exercise[3].split(";")]
        correct = exercise[4].strip()
    else:
        # ОГЭ/ЕГЭ — словари
        exercises = DATA_RAW.get(mode.lower(), {}).get(task, [])
        if not exercises:
            await message.answer("Нет заданий по этой теме.")
            return
        exercise = random.choice(exercises)
        question = exercise["question"]
        options = exercise["options"]
        correct = exercise["correct"]

    state["current"] = {
        "question": question,
        "options": options,
        "correct": correct
    }

    text = question + "\n\n"
    for i, letter in enumerate(["A", "B", "C"]):
        text += f"{letter}) {options[i]}\n"

    await message.answer(text, reply_markup=answers_keyboard())

# Проверка ответа
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
    if mode == "Конкретные темы":
        tasks = CONCRETE_TOPICS
    else:
        tasks = list(DATA_RAW.get(mode.lower(), {}).keys())

    await message.answer("Выбери следующую тему:", reply_markup=tasks_keyboard(tasks))

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
