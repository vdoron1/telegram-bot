# schedule-service/parser.py

import pandas as pd
import re
import os

def clean(text):
    if not isinstance(text, str):
        return ""
    return re.sub(r"\s+", " ", text.strip())

def parse_day_block(df, start_idx):
    day = clean(df.iloc[start_idx, 0])
    lessons = []
    i = start_idx + 1
    while i < len(df) and pd.notna(df.iloc[i, 0]) and not re.search(r"\d+ марта|апреля|мая|июня|понедельник|вторник|среда|четверг|пятница|суббота|воскресенье", str(df.iloc[i, 0])):
        time = clean(df.iloc[i, 0])
        subject = clean(df.iloc[i, 1])
        group = clean(df.iloc[i, 2])
        auditory = clean(df.iloc[i, 3])
        teacher = clean(df.iloc[i, 4])

        if subject:
            lessons.append({
                "time": time,
                "subject": subject,
                "group": group,
                "auditory": auditory,
                "teacher": teacher
            })
        i += 1
    return day, lessons, i

def parse_schedule_file(filepath):
    xl = pd.ExcelFile(filepath)
    schedule = {}

    for sheet in xl.sheet_names:
        df = xl.parse(sheet, header=None)
        df.fillna("", inplace=True)

        course_key = ""
        week_key = ""

        # Определяем курс и неделю по имени листа
        course_match = re.search(r"(\d) курс", sheet)
        week_match = re.search(r"(\d+ неделя)", sheet)
        session_match = re.search(r"Сессия", sheet, re.IGNORECASE)

        if session_match:
            course_key = sheet.strip()
            week_key = "Сессия"
        elif course_match:
            course_key = f"{course_match.group(1)} курс"
            week_key = week_match.group(1) if week_match else "Общая"
        else:
            course_key = sheet.strip()
            week_key = "Общая"

        if course_key not in schedule:
            schedule[course_key] = {}

        schedule[course_key][week_key] = {}

        i = 0
        while i < len(df):
            cell = clean(df.iloc[i, 0])
            if re.search(r"\d+ марта|апреля|мая|июня|понедельник|вторник|среда|четверг|пятница|суббота|воскресенье", cell):
                day, lessons, next_i = parse_day_block(df, i)
                if day and lessons:
                    schedule[course_key][week_key][day] = lessons
                i = next_i
            else:
                i += 1

    return schedule
