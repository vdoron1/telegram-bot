# rag-service/app.py

import os
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from together_llm import TogetherLLM

app = FastAPI()

VECTOR_DB_ROOT = "../vector_db"
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

class QueryRequest(BaseModel):
    user_id: str
    question: str

@app.post("/ask")
async def ask_question(req: QueryRequest):
    user_db_path = os.path.join(VECTOR_DB_ROOT, req.user_id)

    if not os.path.exists(user_db_path):
        raise HTTPException(status_code=404, detail="Векторная база для пользователя не найдена.")

    try:
        vectorstore = FAISS.load_local(user_db_path, embeddings=embedding_model, allow_dangerous_deserialization=True)
        retriever = vectorstore.as_retriever()

        llm = TogetherLLM()
        qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

        answer = qa_chain.run(req.question)
        return {"answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке запроса: {str(e)}")
