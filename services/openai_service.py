import logging
from typing import Any
import asyncio, ssl, certifi
from openai import AsyncOpenAI
from config import TOKEN_GPT_AI
import pandas as pd

logger = logging.getLogger(__name__)
MODEL = 'gpt-4o-mini'

_client: AsyncOpenAI | None = None

def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        _client = AsyncOpenAI(api_key=TOKEN_GPT_AI,)
    return _client

def _normalize_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return ''.join(_normalize_text(item) for item in value)
    if value is None:
        return ''
    return str(value)

async def ask_gpt(user_message: Any, system_prompt: Any = 'Ты полезный ассистент. Отвечай кратко и по делу',
                  history: list[dict[str, Any]] | None = None) -> str:
    try:
        system_text = _normalize_text(system_prompt)
        user_text = _normalize_text(user_message)
        messages = [{'role': 'system', 'content': system_text}]
        if history:
            messages.extend([{'role': item['role'], 'content': _normalize_text(item['content'])}
                             for item in history if isinstance(item, dict) and 'role' in item and 'content' in item])
        messages.append({'role': 'user', 'content': user_text})

        client = get_client()
        response = await client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=1000,
            temperature=0.8
        )

        if not response.choices:
            return 'Пустой ответ от GPT'
        answer = response.choices[0].message.content or ''
        return answer
    except asyncio.CancelledError:
        raise
    except Exception as e:
        logger.exception(f'Ошибка GPT: {e}')
        return 'Ошибка при обращении к GPT. Попробуй еще раз'



async def ai_analyze_dataframe(df: pd.DataFrame) -> str:
    try:
        client = get_client()

        # ограничим размер (очень важно!)
        df = df.head(50)

        summary = df.describe().to_string()
        head = df.head().to_string()

        prompt = f"""
                Ты профессиональный аналитик данных.

                Вот данные из Excel:

                Первые строки:
                {head}

                Статистика:
                {summary}

                Сделай:
                1. Что это за данные
                2. Основные тренды
                3. Аномалии (если есть)
                4. Краткие выводы

                Пиши простым и понятным языком на русском.
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
        logger.exception(f"Ошибка AI анализа: {e}")
        return "❌ Ошибка при анализе данных"