# main.py
import asyncio
import random
from aiogram import Bot, Dispatcher, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import CommandStart

from config import BOT_TOKEN
from sheets import SheetsLoader
from keyboards import exam_keyboard, tasks_keyboard, options_keyboard, next_exercise_keyboard

# ------------- LOAD SHEET -----------------
loader = SheetsLoader("eng_upgrade.json", "OGE/EGE")
EXAMS = loader.get_exercises()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ------------- HANDLERS ------------------
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет! \nВыбери экзамен:", reply_markup=exam_keyboard())


@dp.callback_query(F.data.startswith("exam:"))
async def choose_exam(callback: CallbackQuery):
    exam_key = callback.data.split(":")[1]
    await callback.message.edit_text(
        f"Ты выбрал *{exam_key.upper()}*. Выбери задание:",
        reply_markup=tasks_keyboard(exam_key, EXAMS),
        parse_mode="Markdown"
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("task:"))
async def send_exercise(callback: CallbackQuery):
    _, exam_key, task_key = callback.data.split(":")
    ex_list = EXAMS[exam_key][task_key]
    ex_index = random.randint(0, len(ex_list) - 1)
    ex = ex_list[ex_index]

    text = f" *{task_key.capitalize()}*\n\n{ex['exercise']}"
    if ex["options"]:
        await callback.message.answer(text, reply_markup=options_keyboard(exam_key, task_key, ex_index, EXAMS), parse_mode="Markdown")
    else:
        await callback.message.answer(text, parse_mode="Markdown")

    await callback.answer()


@dp.callback_query(F.data.startswith("answer:"))
async def check_answer(callback: CallbackQuery):
    _, exam_key, task_key, ex_index, user_ans = callback.data.split(":")
    ex_index = int(ex_index)
    ex = EXAMS[exam_key][task_key][ex_index]
    correct = ex["answer"]

    if user_ans.upper() == correct.upper():
        text = " Верно!"
    else:
        text = f" Неверно.\nПравильный ответ: {correct}"

    await callback.message.answer(text, reply_markup=next_exercise_keyboard(exam_key, task_key))
    await callback.answer()


@dp.callback_query(F.data.startswith("next:"))
async def next_exercise(callback: CallbackQuery):
    _, exam_key, task_key = callback.data.split(":")
    ex_list = EXAMS[exam_key][task_key]
    ex_index = random.randint(0, len(ex_list) - 1)
    ex = ex_list[ex_index]

    text = f" *{task_key.capitalize()}*\n\n{ex['exercise']}"
    if ex["options"]:
        await callback.message.answer(text, reply_markup=options_keyboard(exam_key, task_key, ex_index, EXAMS), parse_mode="Markdown")
    else:
        await callback.message.answer(text, parse_mode="Markdown")

    await callback.answer()


# ------------- RUN ----------------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
