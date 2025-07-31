from fastapi import FastAPI, Request
import telebot
import os
import openai

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = telebot.TeleBot(BOT_TOKEN)
openai.api_key = OPENAI_API_KEY

app = FastAPI()

@app.on_event("startup")
async def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)

@app.post("/webhook")
async def process_webhook(request: Request):
    json_str = await request.body()
    update = telebot.types.Update.de_json(json_str.decode("utf-8"))
    bot.process_new_updates([update])
    return {"ok": True}

@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.send_message(message.chat.id, "Нейросотрудник запущен и готов к работе.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "Ты помощник по управлению проектами и ИИ-сотрудниками."},
            {"role": "user", "content": message.text}
        ]
    )
    bot.send_message(message.chat.id, response["choices"][0]["message"]["content"])