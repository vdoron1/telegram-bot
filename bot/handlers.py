
from aiogram import types, Dispatcher
from bot.together_model import get_gpt_response

from bot.vector_search import search_materials

async def handle_message(message: types.Message):
    user_text = message.text.lower()

    if "найди" in user_text or "поиск" in user_text:
        result = search_materials(user_text)
        response = f"📖 Найдено в материалах:\n{result}" if result else "😕 Ничего не найдено."
    else:
        response = get_gpt_response(user_text)

    await message.reply(response)

def register_handlers(dp: Dispatcher):
    dp.message_handler()(handle_message)
