import os
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def ask_gpt(prompt):
    print("[DEBUG] Using OpenAI SDK version >=1.0.0 with GPT-4-Turbo model")
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Ты — полезный помощник."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[GPT ERROR] {str(e)}"
