import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def gpt(prompt):
    try:
        print(f"📤 GPT Запрос: {prompt}")
        response = await client.chat.completions.create(
            model=os.getenv("GPT_MODEL", "gpt-4-turbo"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        answer = response.choices[0].message.content
        print(f"📥 GPT Ответ: {answer}")
        return answer
    except Exception as e:
        print("❌ Ошибка GPT:", e)
        return "Ошибка обработки запроса."
