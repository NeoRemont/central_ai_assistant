import os
from openai import OpenAI
from openai.types.chat import ChatCompletion

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_gpt(prompt):
    try:
        print("=== GPT Запрос ===")
        print("Промпт:", prompt)

        completion: ChatCompletion = client.chat.completions.create(
            model=os.getenv("GPT_MODEL", "gpt-4-turbo"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        answer = completion.choices[0].message.content
        print("=== GPT Ответ ===")
        print("Ответ:", answer)

        return answer
    except Exception as e:
        print("Ошибка GPT:", e)
        return "Ошибка обработки запроса."
