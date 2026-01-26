import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from keyboards import start_keyboard, tasks_keyboard, answers_keyboard
from sheets import SheetsLoader  # твой loader для таблицы

bot = Bot(token="YOUR_BOT_TOKEN")
dp = Dispatcher()

# ---------------------
# Загрузка данных из таблицы
# ---------------------
# Должно возвращать список строк:
# [{'exam': 'oge', 'task': 'Грамматические навыки', 'question': '...', 'options': 'A;B;C', 'answer': 'A'}, ...]
DATA_RAW = SheetsLoader("OGE/EGE").get_exercises()

CONCRETE_TOPICS = ["Present", "Past", "Future", "Условные наклонения", "Модальные глаголы", "Косвенная речь"]

user_state = {}

# ---------------------
# Handlers
# ---------------------

@dp.message(CommandStart())
async def start(message: types.Message):
    user_state.clear()
    await message.answer("Привет! Выбери режим:", reply_markup=start_keyboard())

@dp.message(lambda m: m.text in ["ОГЭ", "ЕГЭ", "Конкретные темы"])
async def choose_mode(message: types.Message):
    user_id = message.from_user.id
    mode = message.text
    user_state[user_id] = {"mode": mode}

    if mode == "Конкретные темы":
        tasks = CONCRETE_TOPICS
    else:
        # Берём все темы из DATA_RAW по выбранному exam
        tasks = list({row['task'] for row in DATA_RAW if row['exam'] == mode.lower()})

    await message.answer("Выбери тему:", reply_markup=tasks_keyboard(tasks))

@dp.message(lambda m: m.text == "Назад")
async def back(message: types.Message):
    user_state.pop(message.from_user.id, None)
    await message.answer("Выбери режим:", reply_markup=start_keyboard())

@dp.message(lambda m: m.from_user.id in user_state and "current" not in user_state[m.from_user.id])
async def choose_task(message: types.Message):
    user_id = message.from_user.id
    state = user_state[user_id]
    mode = state["mode"]
    task = message.text

    if mode == "Конкретные темы":
        exercises = [row for row in DATA_RAW if row['exam'] == "Конкретная тема" and row['task'] == task]
    else:
        exercises = [row for row in DATA_RAW if row['exam'] == mode.lower() and row['task'] == task]

    if not exercises:
        await message.answer("Нет заданий по этой теме.")
        return

    exercise = random.choice(exercises)
    question = exercise['question']
    options = [opt.strip() for opt in exercise['options'].split(";")]
    correct = exercise['answer'].strip()

    state["current"] = {"question": question, "options": options, "correct": correct}

    text = question + "\n\n"
    for i, letter in enumerate(["A", "B", "C"]):
        text += f"{letter}) {options[i]}\n"

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
    if mode == "Конкретные темы":
        tasks = CONCRETE_TOPICS
    else:
        tasks = list({row['task'] for row in DATA_RAW if row['exam']
