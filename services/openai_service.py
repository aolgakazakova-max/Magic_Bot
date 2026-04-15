import logging
from typing import Any
import asyncio
import pandas as pd

from openai import AsyncOpenAI
from config import TOKEN_GPT_AI

logger = logging.getLogger(__name__)

MODEL = "gpt-4o-mini"

_client: AsyncOpenAI | None = None



def get_client() -> AsyncOpenAI:
    global _client

    if _client is None:
        _client = AsyncOpenAI(
            api_key=TOKEN_GPT_AI
        )

    return _client



def _normalize_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return " ".join(_normalize_text(v) for v in value)
    if value is None:
        return ""
    return str(value)



async def ask_gpt(
    user_message: Any,
    system_prompt: Any = "Ты полезный ассистент. Отвечай кратко и по делу",
    history: list[dict[str, Any]] | None = None
) -> str:

    try:
        messages = [
            {
                "role": "system",
                "content": _normalize_text(system_prompt)
            }
        ]

        if history:
            messages.extend([
                {
                    "role": item["role"],
                    "content": _normalize_text(item["content"])
                }
                for item in history
                if isinstance(item, dict) and "role" in item and "content" in item
            ])

        messages.append({
            "role": "user",
            "content": _normalize_text(user_message)
        })

        client = get_client()

        response = await client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )

        if not response.choices:
            return "❌ Пустой ответ GPT"

        return response.choices[0].message.content or "❌ Пустой ответ"

    except asyncio.CancelledError:
        raise

    except Exception as e:
        logger.exception(f"GPT error: {e}")
        return "❌ Ошибка GPT"



async def ai_analyze_dataframe(df: pd.DataFrame) -> str:

    try:
        client = get_client()

        df = df.head(30)  # ограничение (важно!)

        head = df.head().to_string()
        summary = df.describe(include="all").to_string()

        prompt = f"""
Ты профессиональный аналитик данных.

Проанализируй Excel данные:

=== ПЕРВЫЕ СТРОКИ ===
{head}

=== СТАТИСТИКА ===
{summary}

Дай:
1. Что это за данные
2. Основные тренды
3. Аномалии
4. Вывод

Пиши просто и по-русски.
"""

        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )

        if not response.choices:
            return "❌ GPT не вернул ответ"

        return response.choices[0].message.content or "❌ Пустой ответ"

    except Exception as e:
        logger.exception(f"Excel AI error: {e}")
        return "❌ Ошибка анализа Excel"