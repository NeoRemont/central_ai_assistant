import os
import telebot
import requests
from gpt import ask_gpt
from whisper_api import transcribe_voice

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    reply = ask_gpt(message.text)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    file_info = bot.get_file(message.voice.file_id)
    file = requests.get(f'https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}')
    transcript = transcribe_voice(file.content)
    reply = ask_gpt(transcript)
    bot.send_message(message.chat.id, reply)

async def start_bot():
    bot.polling(none_stop=True)
