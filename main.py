import asyncio
import random

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

from config import BOT_TOKEN
from sheets import SheetsLoader
from keyboards import start_keyboard, tasks_keyboard, answers_keyboard

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Загружаем ВСЮ таблицу
loader = SheetsLoader("OGE/EGE")
DATA = loader.get_raw_rows()

# ОТЛАДКА: посмотрим, какие данные загрузились
print(f"=== ДЕБАГ ИНФОРМАЦИЯ ===")
print(f"Всего строк: {len(DATA)}")
if DATA:
    print("Первые 2 строки:")
    for i, row in enumerate(DATA[:2]):
        print(f"Строка {i+1}: exam='{row.get('exam')}', task='{row.get('task')}'")
    
    # Все уникальные значения exam
    all_exams = {row.get('exam', '').strip().lower() for row in DATA}
    print(f"Все exam в таблице: {all_exams}")
    
    # Все уникальные значения task
    all_tasks = {row.get('task', '').strip() for row in DATA}
    print(f"Все задачи в таблице: {all_tasks}")

user_state = {}


@dp.message(CommandStart())
async def start(message: types.Message):
    user_state.clear()
    await message.answer(
        "Привет! Выбери режим:",
        reply_markup=start_keyboard()
    )


@dp.message(lambda m: m.text in ["ОГЭ", "ЕГЭ", "Конкретные темы"])
async def choose_mode(message: types.Message):
    user_id = message.from_user.id
    mode = message.text

    user_state[user_id] = {"mode": mode}

    if mode == "Конкретные темы":
        # Ищем ВСЕ записи с exam="конкретная тема" (регистр не важен)
        tasks = sorted(
            {row["task"] for row in DATA 
             if str(row.get("exam", "")).strip().lower() == "конкретная тема"}
        )
    else:
        # Для ОГЭ/ЕГЭ
        exam_key = "oge" if mode == "ОГЭ" else "ege"
        tasks = sorted(
            {row["task"] for row in DATA 
             if str(row.get("exam", "")).strip().lower() == exam_key}
        )

    if not tasks:
        await message.answer("Нет заданий для этого режима")
        return

    await message.answer(
        "Выбери тему:",
        reply_markup=tasks_keyboard(tasks)
    )


@dp.message(lambda m: m.text == "Назад" or m.text == "⬅️ Назад")
async def back(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_state:
        del user_state[user_id]
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

    if mode == "Конкретные темы":
        exercises = [
            row for row in DATA
            if str(row.get("exam", "")).strip().lower() == "конкретная тема" 
            and str(row.get("task", "")).strip() == task
        ]
    else:
        exam_key = "oge" if mode == "ОГЭ" else "ege"
        exercises = [
            row for row in DATA
            if str(row.get("exam", "")).strip().lower() == exam_key
            and str(row.get("task", "")).strip() == task
        ]

    if not exercises:
        await message.answer("Пока что нет заданий по этой теме")
        return

    exercise = random.choice(exercises)
    state["current"] = exercise

    options = [o.strip() for o in exercise.get("options", "").split(";")]

    text = f"{exercise.get('question', '')}\n\n"
    for letter, option in zip(["A", "B", "C"], options):
        text += f"{letter}) {option}\n"

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

    correct = state["current"].get("answer", "").upper().strip()

    if message.text.upper() == correct:
        await message.answer("Верно!")
    else:
        await message.answer(f"Неверно. Правильный ответ: {correct}")

    state.pop("current", None)

    mode = state.get("mode", "")

    if mode == "Конкретные темы":
        tasks = sorted(
            {row["task"] for row in DATA 
             if str(row.get("exam", "")).strip().lower() == "конкретная тема"}
        )
    else:
        exam_key = "oge" if mode == "ОГЭ" else "ege"
        tasks = sorted(
            {row["task"] for row in DATA 
             if str(row.get("exam", "")).strip().lower() == exam_key}
        )

    await message.answer(
        "Выбери следующую тему:",
        reply_markup=tasks_keyboard(tasks)
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())



