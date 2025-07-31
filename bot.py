import os
import requests
from gpt import generate_gpt_response

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4-turbo")

async def telegram_webhook(data):
    message = data.get("message")
    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    user_text = message.get("text", "")

    reply = await generate_gpt_response(user_text, GPT_MODEL)
    send_message(chat_id, reply)

    return {"ok": True}

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)