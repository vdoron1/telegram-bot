import os
import requests
from dotenv import load_dotenv

# Загружаем API-ключ
load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

# Выбираем модель (см. https://api.together.xyz/models)
MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

HEADERS = {
    "Authorization": f"Bearer {TOGETHER_API_KEY}",
    "Content-Type": "application/json"
}

def get_together_response(prompt: str, max_tokens: int = 100) -> str:
    """Отправляет запрос в Together AI API и получает ответ от модели"""
    url = "https://api.together.xyz/v1/chat/completions"

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "top_p": 0.9
    }

    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()  # Проверяем ошибки API
        data = response.json()

        # Логируем полный ответ API (для отладки)
        print("🔹 Ответ API:", data)

        # Проверяем, есть ли "choices" в ответе
        if "choices" in data and len(data["choices"]) > 0:
            if "text" in data["choices"][0]:  # Новый формат API
                return data["choices"][0]["text"].strip()
            elif "message" in data["choices"][0]:  # Другой вариант API
                return data["choices"][0]["message"]["content"].strip()
            elif "output" in data:  # Возможно, ответ приходит здесь
                return data["output"].strip()
            else:
                return "⚠️ Ошибка: API не вернул текст."
        else:
            return "⚠️ Ошибка: API вернул пустой ответ."

    except requests.exceptions.RequestException as e:
        return f"⚠️ Ошибка API: {str(e)}"