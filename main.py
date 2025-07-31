from fastapi import FastAPI, Request
from bot import telegram_webhook
import os

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    from webhook_setup import set_webhook
    await set_webhook()

@app.post("/webhook")
async def telegram_webhook_entry(request: Request):
    return await telegram_webhook(await request.json())