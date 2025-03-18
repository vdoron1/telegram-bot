import os
import json
import docx
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
#from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_community.vectorstores import FAISS

# Пути к данным
DATA_FOLDER = "data"
VECTOR_DB_PATH = "vector_db"
USER_QUESTIONS_FILE = "user_questions.json"

# Создаём эмбеддинги (Hugging Face)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


# 🔹 **Функция загрузки данных из файлов**
def load_files():
    docs = []

    if os.path.exists(DATA_FOLDER):
        for filename in os.listdir(DATA_FOLDER):
            file_path = os.path.join(DATA_FOLDER, filename)

            if filename.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
                docs.extend(loader.load())

            elif filename.endswith(".txt"):
                with open(file_path, "r", encoding="utf-8") as file:
                    text = file.read()
                    docs.append({"page_content": text})

            elif filename.endswith(".docx"):
                doc = docx.Document(file_path)
                text = "\n".join([p.text for p in doc.paragraphs])
                docs.append({"page_content": text})

    return docs


# 🔹 **Создание или обновление векторной базы**
def create_vector_db():
    print("🔹 Загружаем файлы в базу...")
    documents = load_files()

    if not documents:
        print("⚠️ Нет загруженных файлов для обработки.")
        return

    # Разбиваем текст на куски
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)

    # Создаём FAISS базу
    vector_db = FAISS.from_documents(texts, embedding=embeddings)
    vector_db.save_local(VECTOR_DB_PATH)
    print("✅ Векторная база обновлена!")


# 🔹 **Функция загрузки пользовательских вопросов**
def load_user_questions():
    """Загружает сохранённые вопросы пользователей."""
    if os.path.exists(USER_QUESTIONS_FILE):
        with open(USER_QUESTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


# 🔹 **Сохранение новых вопросов пользователей**
def save_user_question(question, answer):
    """Сохраняет вопросы пользователей в базу для обучения."""
    user_data = load_user_questions()
    user_data.append({"question": question, "answer": answer})

    with open(USER_QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)
