# bot-service/main.py

import os
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
FILE_SERVICE_URL = os.getenv("FILE_SERVICE_URL")
RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL")
SCHEDULE_SERVICE_URL = os.getenv("SCHEDULE_SERVICE_URL")

bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("👋 Привет! Я умный студенческий бот. Можешь загрузить файл, задать вопрос или посмотреть расписание.")

@dp.message(Command("расписание"))
async def get_schedule(message: Message):
    user_id = str(message.from_user.id)
    await message.answer("🔎 Уточни, пожалуйста, курс и неделю в формате: 1 курс, 6 неделя")

@dp.message(F.text.regexp(r"^\d курс,? \d неделя$"))
async def fetch_week_schedule(message: Message):
    user_id = str(message.from_user.id)
    parts = message.text.replace(",", "").split()
    course = f"{parts[0]} курс"
    week = f"{parts[1]} неделя"
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{SCHEDULE_SERVICE_URL}/get_week", params={"user_id": user_id, "course": course, "week": week}) as resp:
            if resp.status == 200:
                data = await resp.json()
                if not data:
                    await message.answer("❌ Расписание не найдено.")
                    return
                text = "<b>📅 Расписание:</b>\n"
                for day, lessons in data.items():
                    text += f"\n<b>{day}</b>\n"
                    for lesson in lessons:
                        text += f"🕐 {lesson['time']}: {lesson['subject']} ({lesson['group']}) — {lesson['teacher']} [{lesson['auditory']}]\n"
                await message.answer(text)
            else:
                await message.answer("⚠️ Ошибка при получении расписания.")

@dp.message(F.document)
async def handle_file(message: Message):
    document = message.document
    file = await bot.download(document)
    user_id = str(message.from_user.id)
    form = aiohttp.FormData()
    form.add_field("user_id", user_id)
    form.add_field("file", file, filename=document.file_name, content_type=document.mime_type)

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{FILE_SERVICE_URL}/upload", data=form) as resp:
            if resp.status == 200:
                result = await resp.json()
                await message.answer(f"✅ {result['message']}")
            else:
                await message.answer("⚠️ Ошибка при загрузке файла.")

@dp.message(F.text)
async def ask_rag(message: Message):
    user_id = str(message.from_user.id)
    question = message.text
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{RAG_SERVICE_URL}/ask", json={"user_id": user_id, "question": question}) as resp:
            if resp.status == 200:
                result = await resp.json()
                await message.answer(f"🤖 {result['answer']}")
            else:
                await message.answer("⚠️ Ошибка при обращении к RAG-системе.")

async def main():
    print("🤖 Telegram-бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
