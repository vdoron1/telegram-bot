# schedule-service/app.py

import os
from fastapi import FastAPI, HTTPException, Query
from parser import parse_schedule_file
import json

app = FastAPI()

SCHEDULE_DIR = "../schedules"

@app.get("/get")
async def get_schedule(user_id: str = Query(...)):
    file_path = os.path.join(SCHEDULE_DIR, f"schedule_{user_id}.xlsx")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Расписание не найдено.")
    try:
        schedule = parse_schedule_file(file_path)
        return schedule
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка парсинга: {str(e)}")

@app.get("/get_week")
async def get_week(user_id: str = Query(...), course: str = Query(...), week: str = Query(...)):
    file_path = os.path.join(SCHEDULE_DIR, f"schedule_{user_id}.xlsx")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден.")
    try:
        schedule = parse_schedule_file(file_path)
        return schedule.get(course, {}).get(week, {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")

@app.get("/get_day")
async def get_day(user_id: str = Query(...), course: str = Query(...), week: str = Query(...), day: str = Query(...)):
    file_path = os.path.join(SCHEDULE_DIR, f"schedule_{user_id}.xlsx")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден.")
    try:
        schedule = parse_schedule_file(file_path)
        return schedule.get(course, {}).get(week, {}).get(day, [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")
