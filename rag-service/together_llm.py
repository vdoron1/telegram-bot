# rag-service/together_llm.py

from langchain.llms.base import LLM
from typing import Optional, List
import os
import requests
from dotenv import load_dotenv

load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

class TogetherLLM(LLM):
    model: str = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
    temperature: float = 0.7
    max_tokens: int = 300

    @property
    def _llm_type(self) -> str:
        return "together_custom"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        url = "https://api.together.xyz/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": 0.9
        }

        try:
            res = requests.post(url, headers=headers, json=payload)
            data = res.json()
            if "choices" in data and len(data["choices"]) > 0:
                if "text" in data["choices"][0]:
                    return data["choices"][0]["text"].strip()
                elif "message" in data["choices"][0]:
                    return data["choices"][0]["message"]["content"].strip()
            return "❌ Не удалось получить ответ от модели."
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
