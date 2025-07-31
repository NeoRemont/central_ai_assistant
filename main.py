import os
import openai
from fastapi import FastAPI, Request
import uvicorn
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio

TOKEN = os.getenv("TELEGRAM_TOKEN")
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4-turbo")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()
bot_app = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Нейроассистент готов!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    if not user_message:
        return
    try:
        completion = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=[{"role": "user", "content": user_message}]
        )
        reply = completion.choices[0].message.content
    except Exception as e:
        reply = "Произошла ошибка при обращении к GPT."
    await update.message.reply_text(reply)

@app.on_event("startup")
async def startup_event():
    global bot_app
    bot_app = Application.builder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await bot_app.initialize()
    await bot_app.bot.set_webhook(WEBHOOK_URL)
    asyncio.create_task(bot_app.start())

@app.post("/")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = telegram.Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)