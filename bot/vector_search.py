
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import os

# Путь к файлу PDF
DATA_PATH = "data/справки.pdf"

# Загружаем PDF-документы
def load_documents():
    loader = PyPDFLoader(DATA_PATH)
    documents = loader.load()
    return documents

# Используем Hugging Face Embeddings вместо OpenAI
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Создаём векторное хранилище
vectorstore = FAISS.from_documents(load_documents(), embedding=embeddings)

def search_materials(query: str) -> str:
    """Ищем информацию в загруженных учебных материалах."""
    docs = vectorstore.similarity_search(query, k=2)
    return "\n\n".join([doc.page_content for doc in docs]) if docs else "😕 Ничего не найдено."
