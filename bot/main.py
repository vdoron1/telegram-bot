import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from rag_system import rag_search
from document_handler import create_vector_db

# Загружаем API-ключ
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ Ошибка: Не найден TELEGRAM_BOT_TOKEN в переменных среды!")
# Создаём бота
bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


# 🔹 **Команда /start**
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("👋 Привет! Отправьте файл (PDF, TXT, DOCX) или задайте вопрос!")


# 🔹 **Обработка вопросов**
@dp.message(F.text)
async def handle_message(message: Message):
    user_text = message.text
    response = rag_search(user_text)
    await message.answer(response)


# 🔹 **Обработка загрузки файлов**
@dp.message(F.document)
async def handle_file_upload(message: Message):
    document = message.document
    file_name = document.file_name

    # Сохраняем файл
    file_path = os.path.join("data", file_name)
    await bot.download(document.file_id, destination=file_path)

    await message.answer(f"✅ Файл `{file_name}` загружен. Теперь можете задавать вопросы по нему!")

    # Пересоздаём базу с новыми файлами
    create_vector_db()


# 🔹 **Запуск бота**
async def main():
    print("\n✅ Бот запущен! Теперь использует загруженные файлы, базу и Google.\n")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
