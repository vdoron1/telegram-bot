import os
import random
import requests
import logging
from googleapiclient.discovery import build
from together_model import get_together_response
from dotenv import load_dotenv
from document_handler import create_vector_db, load_user_questions, save_user_question
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# Настройка логов
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Загружаем API-ключи
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CX")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

# Пути к данным
VECTOR_DB_PATH = "vector_db"

# Создаём эмбеддинги (Hugging Face)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


# 🔹 **Поиск в Google с кэшированием**
google_cache = {}

def google_search(query):
    """Поиск информации в Google с кэшированием запросов."""
    if query in google_cache:
        logging.info(f"✅ Используем кэшированный результат для запроса: {query}")
        return google_cache[query]

    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        res = service.cse().list(q=query, cx=GOOGLE_CX, num=3).execute()
        search_results = "\n\n".join([item["snippet"] for item in res.get("items", [])]) if "items" in res else None

        # Сохраняем в кэш
        google_cache[query] = search_results
        return search_results

    except Exception as e:
        logging.error(f"❌ Ошибка Google Search: {e}")
        return None


# 🔹 **Поиск ответа с учётом всех источников**
def rag_search(query: str) -> str:
    """Поиск ответа с учётом загруженных файлов, базы данных, Google и нейросети"""

    logging.info(f"🔎 Новый запрос: {query}")

    # Проверяем, есть ли векторная база
    if not os.path.exists(VECTOR_DB_PATH):
        logging.warning("⚠️ Векторная база отсутствует. Создаём...")
        create_vector_db()

    # 1️⃣ **Поиск в векторной базе**
    vector_db = FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)
    docs = vector_db.similarity_search(query, k=3)

    # Создаём промпт для нейросети
    prompt_base = (
        "Ты — интеллектуальный помощник. "
        "Ты должен дать осмысленный ответ на любой вопрос, даже если данных недостаточно. "
        "Используй максимум информации из контекста, если он есть. "
        "Если контекста нет — используй общие знания. "
        "Отвечай чётко, не более 4 предложений."
    )

    if docs:
        context = "\n\n".join([doc.page_content for doc in docs])
        prompt = f"{prompt_base}\n\nКонтекст:\n{context}\n\nВопрос: {query}\nОтвет:"
        response = get_together_response(prompt, max_tokens=200)

        logging.info("✅ Ответ найден в базе данных.")
        save_user_question(query, response)
        return response

    # 2️⃣ **Поиск в Google**
    search_results = google_search(query)
    if search_results:
        prompt = f"{prompt_base}\n\nИнформация из Google:\n{search_results}\n\nВопрос: {query}\nОтвет:"
        response = get_together_response(prompt, max_tokens=200)

        logging.info("✅ Ответ найден через Google.")
        save_user_question(query, response)
        return response

    # 3️⃣ **Ответ нейросети, если ничего не найдено**
    logging.warning(f"⚠️ Данных нет, использую нейросеть...")
    return get_together_response(f"{prompt_base}\n\nВопрос: {query}\nОтвет:", max_tokens=200)
