# file-service/app.py

import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import Literal
from utils import process_file_and_save_db

app = FastAPI()

@app.post("/upload")
async def upload_file(user_id: str = Form(...), file: UploadFile = File(...)):
    try:
        content = await file.read()
        file_path = f"temp/{user_id}_{file.filename}"
        os.makedirs("temp", exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(content)

        # Определяем тип по расширению
        ext = file.filename.split(".")[-1].lower()

        if ext in ["pdf", "docx", "txt"]:
            success = process_file_and_save_db(file_path, user_id)
            if success:
                return {"status": "ok", "message": "Документ обработан и сохранён."}
            else:
                raise HTTPException(status_code=500, detail="Ошибка обработки файла")

        elif ext in ["xlsx"]:
            # Пока просто сохраняем, парсинг будет в schedule-service
            schedule_path = f"../schedules/schedule_{user_id}.xlsx"
            os.makedirs("../schedules", exist_ok=True)
            with open(schedule_path, "wb") as f:
                f.write(content)
            return {"status": "ok", "message": "Расписание сохранено."}

        else:
            raise HTTPException(status_code=400, detail="Неподдерживаемый формат файла")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки файла: {str(e)}")
