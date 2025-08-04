import os
import requests
import subprocess
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from gpt import ask_gpt
from whisper_api import transcribe_audio

TOKEN = os.getenv("TELEGRAM_TOKEN")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Здравствуйте! Я Центральный Нейросотрудник. Жду ваш запрос.")

def handle_text(update: Update, context: CallbackContext):
    user_message = update.message.text
    gpt_reply = ask_gpt(user_message)
    update.message.reply_text(gpt_reply)

def handle_voice(update: Update, context: CallbackContext):
    file = update.message.voice.get_file()
    ogg_path = "voice.ogg"
    wav_path = "voice.wav"
    file.download(ogg_path)

    try:
        subprocess.run(["ffmpeg", "-y", "-i", ogg_path, wav_path], check=True)
        text = transcribe_audio(wav_path)
        gpt_reply = ask_gpt(text)
        update.message.reply_text(gpt_reply)
    except Exception as e:
        update.message.reply_text("Ошибка при распознавании голоса.")
    finally:
        if os.path.exists(ogg_path):
            os.remove(ogg_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)

def run_bot():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    dp.add_handler(MessageHandler(Filters.voice, handle_voice))

    updater.start_polling()
    updater.idle()
