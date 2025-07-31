from fastapi import FastAPI, Request
import os
import openai
import httpx
import asyncio

app = FastAPI()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

openai.api_key = OPENAI_API_KEY

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/webhook")
async def telegram_webhook(req: Request):
    body = await req.json()
    message = body.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text")

    if not chat_id or not text:
        return {"status": "ignored"}

    try:
        gpt_response = await ask_gpt(text)
        await send_telegram_message(chat_id, gpt_response)
    except Exception as e:
        await send_telegram_message(chat_id, "Ошибка обработки запроса.")

    return {"status": "ok"}

async def ask_gpt(prompt: str) -> str:
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

async def send_telegram_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

@app.on_event("startup")
async def startup_event():
    if BOT_TOKEN and WEBHOOK_URL:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
        async with httpx.AsyncClient() as client:
            await client.post(url, params={"url": WEBHOOK_URL})