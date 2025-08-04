import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DEFAULT_MODEL = os.getenv("GPT_MODEL", "gpt-4o-mini")

def ask_gpt(prompt: str) -> str:
    try:
        resp = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return resp.choices[0].message.content
    except Exception as e:
        print("[ERROR][GPT]", e)
        return "Ошибка обработки запроса."