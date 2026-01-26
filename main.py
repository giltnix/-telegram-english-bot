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
DATA = loader.get_exercises()  # Словари для ОГЭ/ЕГЭ и список для "Конкретная тема"

user_state = {}

# Маппинг кнопок
MODE_MAP = {
    "ОГЭ": "oge",
    "ЕГЭ": "ege",
    "Конкретные темы": "Конкретная тема"
}

# Кнопки выбора тем для Конкретных тем
CONCRETE_TOPICS = ["Present", "Past", "Future", "Условные наклонения", "Модальные глаголы", "Косвенная речь"]

# Старт
@dp.message(CommandStart())
async def start(message: types.Message):
    user_state.clear()
    await message.answer(
        "Привет! Выбери режим:",
        reply_markup=start_keyboard()
    )

# Выбор режима
@dp.message(lambda m: m.text in MODE_MAP)
async def choose_mode(message: types.Message):
    user_id = message.from_user.id
    mode = MODE_MAP[message.text]
    user_state[user_id] = {"mode": mode}

    # Для Конкретных тем выводим фиксированные кнопки
    if message.text == "Конкретные темы":
        tasks = CONCRETE_TOPICS
    else:
        # Для ОГЭ/ЕГЭ берём темы из словаря, как было
        tasks = list(DATA.get(mode, {}).keys())

    await message.answer("Выбери тему:", reply_markup=tasks_keyboard(tasks))

# Кнопка Назад
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

    # Конкретные темы — список строк
    if mode == "Конкретная тема":
        exercises = [row for row in DATA.get("Конкретная тема", []) if row["task"] == task]
    else:
        # ОГЭ/ЕГЭ — словари, как было
        exercises = DATA.get(mode, {}).get(task, [])

    if not exercises:
        await message.answer("Нет заданий по этой теме.")
        return

    # Случайное упражнение
    exercise = random.choice(exercises)
    state["current"] = exercise

    # Варианты и правильный ответ
    if mode == "Конкретная тема":
        options = [opt.strip() for opt in exercise["options"].split(";")]
        correct = exercise["answer"].strip()
    else:
        options = exercise["options"]
        correct = exercise["correct"]

    state["current"]["options"] = options
    state["current"]["correct"] = correct

    text = exercise["question"] + "\n\n"
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
    if mode == "Конкретная тема":
        tasks = CONCRETE_TOPICS
    else:
        tasks = list(DATA.get(mode, {}).keys())

    await message.answer("Выбери следующую тему:", reply_markup=tasks_keyboard(tasks))

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
