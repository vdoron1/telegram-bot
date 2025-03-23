# file-service/utils.py

import os
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings


def process_file_and_save_db(filepath: str, user_id: str) -> bool:
    try:
        ext = filepath.split(".")[-1].lower()

        if ext == "pdf":
            loader = PyPDFLoader(filepath)
        elif ext == "docx":
            loader = Docx2txtLoader(filepath)
        elif ext == "txt":
            loader = TextLoader(filepath)
        else:
            return False

        documents = loader.load()

        # Чистим и делим
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_documents(documents)

        # Векторизуем
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        db = FAISS.from_documents(chunks, embedding=embeddings)

        save_path = f"../vector_db/{user_id}"
        os.makedirs(save_path, exist_ok=True)
        db.save_local(save_path)

        return True

    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")
        return False
