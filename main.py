import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

from keyboards import start_keyboard, tasks_keyboard, answers_keyboard
from config import BOT_TOKEN   # BOT_TOKEN берётся из окружения


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# -----------------------
# ИМИТАЦИЯ ТАБЛИЦЫ
# -----------------------

DATA = [
    {
        "exam": "oge",
        "task": "Present Simple",
        "question": "She ___ to school every day.",
        "options": ["go", "goes", "went"],
        "answer": "B"
    },
    {
        "exam": "oge",
        "task": "Past Simple",
        "question": "Yesterday I ___ a movie.",
        "options": ["watch", "watched", "watching"],
        "answer": "B"
    },
    {
        "exam": "Конкретная тема",
        "task": "Условные наклонения",
        "question": "If I were you, I ___ this book.",
        "options": ["read", "will read", "would read"],
        "answer": "C"
    }
]

CONCRETE_TOPICS = [
    "Present Simple",
    "Past Simple",
    "Future Simple",
    "Условные наклонения"
]

user_state = {}

# -----------------------
# START
# -----------------------

@dp.message(CommandStart())
async def start(message: types.Message):
    user_state.clear()
    await message.answer(
        "Привет! Выбери режим 👇",
        reply_markup=start_keyboard()
    )

# -----------------------
# ВЫБОР РЕЖИМА
# -----------------------

@dp.message(lambda m: m.text in ["ОГЭ", "ЕГЭ", "Конкретные темы"])
async def choose_mode(message: types.Message):
    user_id = message.from_user.id
    mode = message.text

    user_state[user_id] = {"mode": mode}

    if mode == "Конкретные темы":
        tasks = CONCRETE_TOPICS
    else:
        tasks = list(
            {row["task"] for row in DATA if row["exam"] == mode.lower()}
        )

    await message.answer(
        "Выбери тему:",
        reply_markup=tasks_keyboard(tasks)
    )

# -----------------------
# НАЗАД
# -----------------------

@dp.message(lambda m: m.text == "Назад")
async def back(message: types.Message):
    user_state.pop(message.from_user.id, None)
    await message.answer(
        "Выбери режим:",
        reply_markup=start_keyboard()
    )

# -----------------------
# ВЫБОР ТЕМЫ
# -----------------------

@dp.message(lambda m: m.from_user.id in user_state and "current" not in user_state[m.from_user.id])
async def choose_task(message: types.Message):
    user_id = message.from_user.id
    mode = user_state[user_id]["mode"]
    task = message.text

    if mode == "Конкретные темы":
        pool = [
            row for row in DATA
            if row["exam"] == "Конкретная тема" and row["task"] == task
        ]
    else:
        pool = [
            row for row in DATA
            if row["exam"] == mode.lower() and row["task"] == task
        ]

    if not pool:
        await message.answer("По этой теме пока нет заданий 😔")
        return

    exercise = random.choice(pool)

    user_state[user_id]["current"] = exercise

    text = (
        f"{exercise['question']}\n\n"
        f"A) {exercise['options'][0]}\n"
        f"B) {exercise['options'][1]}\n"
        f"C) {exercise['options'][2]}"
    )

    await message.answer(text, reply_markup=answers_keyboard())

# -----------------------
# ПРОВЕРКА ОТВЕТА
# -----------------------

@dp.message(lambda m: m.text in ["A", "B", "C"])
async def check_answer(message: types.Message):
    user_id = message.from_user.id
    state = user_state.get(user_id)

    if not state or "current" not in state:
        return

    correct = state["current"]["answer"]

    if message.text == correct:
        await message.answer("✅ Верно!")
    else:
        await message.answer(f"❌ Неверно. Правильный ответ: {correct}")

    state.pop("current")

    mode = state["mode"]

    if mode == "Конкретные темы":
        tasks = CONCRETE_TOPICS
    else:
        tasks = list(
            {row["task"] for row in DATA if row["exam"] == mode.lower()}
        )

    await message.answer(
        "Выбери следующую тему:",
        reply_markup=tasks_keyboard(tasks)
    )

# -----------------------
# ЗАПУСК
# -----------------------

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


