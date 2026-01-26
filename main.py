import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from config import BOT_TOKEN
from sheets import SheetsLoader
from keyboards import start_keyboard, tasks_keyboard, answers_keyboard, explanation_keyboard

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Загружаем данные
loader = SheetsLoader("OGE/EGE")
DATA = loader.sheet.get_all_records()

print(f"✅ Загружено {len(DATA)} заданий")

user_state = {}

@dp.message(CommandStart())
async def start(message: types.Message):
    user_id = message.from_user.id
    user_state[user_id] = {}
    await message.answer(
        "Привет! Выбери режим:",
        reply_markup=start_keyboard()
    )

@dp.message(lambda m: m.text in ["ОГЭ", "ЕГЭ", "Конкретные темы"])
async def choose_mode(message: types.Message):
    user_id = message.from_user.id
    mode = message.text
    user_state[user_id] = {"mode": mode}
    
    # Формируем список тем
    if mode == "Конкретные темы":
        exam_filter = "конкретная тема"
    else:
        exam_filter = "oge" if mode == "ОГЭ" else "ege"
    
    tasks = sorted({
        row["task"] for row in DATA 
        if str(row.get("exam", "")).strip().lower() == exam_filter
    })
    
    if not tasks:
        await message.answer("Пока нет заданий для этого режима")
        return
    
    await message.answer(
        "Выбери тему:",
        reply_markup=tasks_keyboard(tasks)
    )

@dp.message(lambda m: m.text == "Назад" or m.text == "⬅️ Назад")
async def go_back(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_state:
        user_state[user_id] = {}
    await message.answer(
        "Выбери режим:",
        reply_markup=start_keyboard()
    )

@dp.message(lambda m: m.from_user.id in user_state and "current" not in user_state[m.from_user.id] and m.text not in ["ОГЭ", "ЕГЭ", "Конкретные темы", "Назад", "📖 Объяснение", "⬅️ Назад к темам"])
async def choose_task(message: types.Message):
    user_id = message.from_user.id
    state = user_state[user_id]
    mode = state["mode"]
    selected_task = message.text
    
    # Определяем фильтр для экзамена
    if mode == "Конкретные темы":
        exam_filter = "конкретная тема"
    else:
        exam_filter = "oge" if mode == "ОГЭ" else "ege"
    
    # Ищем задания
    exercises = [
        row for row in DATA
        if str(row.get("exam", "")).strip().lower() == exam_filter 
        and str(row.get("task", "")).strip() == selected_task
    ]
    
    if not exercises:
        await message.answer("Пока нет заданий по этой теме")
        return
    
    # Выбираем случайное задание
    exercise = random.choice(exercises)
    state["current"] = exercise
    
    # Формируем варианты ответов
    options_text = exercise.get("options", "")
    if options_text:
        options = [opt.strip() for opt in options_text.split(";")]
    else:
        options = ["Нет вариантов", "", ""]
    
    # Формируем текст вопроса
    text = f"{exercise.get('question', '')}\n\n"
    for letter, option in zip(["A", "B", "C"], options[:3]):  # Берем максимум 3 варианта
        if option:
            text += f"{letter}) {option}\n"
    
    await message.answer(text, reply_markup=answers_keyboard())

@dp.message(lambda m: m.text in ["A", "B", "C"])
async def check_answer(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_state or "current" not in user_state[user_id]:
        return
    
    state = user_state[user_id]
    correct = state["current"].get("answer", "").upper().strip()
    user_answer = message.text.upper()
    
    # Сохраняем ответ пользователя
    state["user_answer"] = user_answer
    
    if user_answer == correct:
        response = "Верно!"
    else:
        response = f"Неверно. Правильный ответ: {correct}"
    
    # Проверяем, есть ли объяснение
    explanation = state["current"].get("explanation", "").strip()
    
    if explanation:
        await message.answer(
            f"{response}\n\nХочешь посмотреть объяснение ответа?",
            reply_markup=explanation_keyboard()
        )
    else:
        await message.answer(response)
        # Возвращаем к выбору тем
        await return_to_topics(message, state)

@dp.message(lambda m: m.text == "📖 Объяснение")
async def show_explanation(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_state or "current" not in user_state[user_id]:
        await message.answer("Сначала ответь на вопрос!")
        return
    
    state = user_state[user_id]
    explanation = state["current"].get("explanation", "").strip()
    
    if explanation:
        await message.answer(
            f"📖 **Объяснение:**\n\n{explanation}",
            parse_mode="Markdown"
        )
    else:
        await message.answer("К сожалению, объяснение для этого задания отсутствует.")
    
    # После показа объяснения предлагаем вернуться к темам
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    await message.answer(
        "Что дальше?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="⬅️ Назад к темам")]],
            resize_keyboard=True
        )
    )

@dp.message(lambda m: m.text == "⬅️ Назад к темам")
async def back_to_topics(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_state:
        return
    
    state = user_state[user_id]
    await return_to_topics(message, state)

async def return_to_topics(message: types.Message, state: dict):
    """Возвращает к выбору тем"""
    mode = state.get("mode", "")
    
    # Очищаем текущее задание
    state.pop("current", None)
    state.pop("user_answer", None)
    
    if mode == "Конкретные темы":
        exam_filter = "конкретная тема"
    else:
        exam_filter = "oge" if mode == "ОГЭ" else "ege"
    
    tasks = sorted({
        row["task"] for row in DATA 
        if str(row.get("exam", "")).strip().lower() == exam_filter
    })
    
    await message.answer(
        "Выбери тему:",
        reply_markup=tasks_keyboard(tasks)
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



