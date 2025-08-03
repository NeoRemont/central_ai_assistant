import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_gpt(prompt):
    try:
        print("[DEBUG] GPT-4 Turbo prompt:", prompt)
        completion = client.chat.completions.create(
            model=os.getenv("GPT_MODEL", "gpt-4-turbo"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        answer = completion.choices[0].message.content
        print("[DEBUG] GPT-4 Turbo answer:", answer)
        return answer
    except Exception as e:
        print("[ERROR] GPT:", e)
        return "Ошибка обработки запроса."
