# bot.py
import os
import logging
import tempfile
import aiohttp
import openai
from pydub import AudioSegment
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# 🔐 Переменные окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("BACKEND_URL", "http://localhost:8000/ask")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 🧠 Подключаем ключ OpenAI
openai.api_key = OPENAI_API_KEY

# 🔧 Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 🎙 Функция для распознавания речи через Whisper
async def transcribe_voice(file_path: str) -> str:
    with open(file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript["text"]

# 📥 Обработка голосовых сообщений
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Скачиваем голосовое сообщение
        voice_file = await context.bot.get_file(update.message.voice.file_id)
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp_ogg:
            await voice_file.download_to_drive(tmp_ogg.name)
            # Конвертируем в WAV
            sound = AudioSegment.from_ogg(tmp_ogg.name)
            tmp_wav = tmp_ogg.name.replace(".ogg", ".wav")
            sound.export(tmp_wav, format="wav")

        # Распознаём речь
        text = await transcribe_voice(tmp_wav)
        await process_text(update, context, text)

    except Exception as e:
        logging.exception("Ошибка при обработке голосового сообщения")
        await update.message.reply_text("Произошла ошибка при распознавании голоса.")

# 💬 Обработка текстовых сообщений и текста из голоса
async def process_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str = None):
    if text is None:
        text = update.message.text

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json={"message": text}) as resp:
                data = await resp.json()
                reply = data.get("response") or data.get("error", "Ошибка ответа от сервера")
                await update.message.reply_text(reply)
    except Exception as e:
        logging.exception("Ошибка при обращении к main.py")
        await update.message.reply_text("Ошибка при обращении к нейросотруднику.")

# 🚀 Запуск бота
if _name_ == "_main_":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_text))
    app.run_polling()
