
import os
import telebot
import openai
import requests
import tempfile
from pydub import AudioSegment
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

# Webhook установка при старте
if WEBHOOK_URL:
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)

def transcribe_voice(file_path):
    audio = open(file_path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio)
    return transcript["text"]

def ask_gpt(message_text):
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": message_text}]
    )
    return response["choices"][0]["message"]["content"]

@bot.message_handler(content_types=['text'])
def handle_text(message):
    reply = ask_gpt(message.text)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        file_info = bot.get_file(message.voice.file_id)
        file_data = bot.download_file(file_info.file_path)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as f:
            f.write(file_data)
            ogg_path = f.name

        wav_path = ogg_path.replace(".ogg", ".wav")
        AudioSegment.from_ogg(ogg_path).export(wav_path, format="wav")

        prompt = transcribe_voice(wav_path)
        reply = ask_gpt(prompt)
        bot.send_message(message.chat.id, reply)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка обработки голосового: {e}")

bot.infinity_polling()
