from fastapi import FastAPI, Request
import requests
import os
import openai

app = FastAPI()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-3.5-turbo")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

openai.api_key = OPENAI_API_KEY

@app.on_event("startup")
async def set_webhook():
    if TELEGRAM_BOT_TOKEN and WEBHOOK_URL:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
        requests.post(url, json={"url": WEBHOOK_URL})

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    message = data.get("message", {}).get("text", "")
    chat_id = data.get("message", {}).get("chat", {}).get("id")

    if message and chat_id:
        try:
            gpt_response = openai.ChatCompletion.create(
                model=GPT_MODEL,
                messages=[{"role": "user", "content": message}]
            )
            answer = gpt_response["choices"][0]["message"]["content"]
        except Exception as e:
            answer = "Ошибка GPT: " + str(e)

        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": answer}
        )

    return {"ok": True}
