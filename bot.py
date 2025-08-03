import os
import requests
from openai import OpenAI

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4-turbo")

client = OpenAI(api_key=OPENAI_API_KEY)

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

def handle_message(chat_id, text):
    try:
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[{"role": "user", "content": text}],
            temperature=0.7
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"Ошибка GPT: {e}"
    send_message(chat_id, answer)
