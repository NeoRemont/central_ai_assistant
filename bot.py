
import logging
import os
import tempfile
import subprocess
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai
from whisper_api import transcribe_audio
from gpt import ask_gpt
from imageio_ffmpeg import get_ffmpeg_exe

# Настройка логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
FFMPEG_PATH = get_ffmpeg_exe()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я нейросотрудник. Жду твою команду.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    reply = await ask_gpt(user_text)
    await update.message.reply_text(reply)


from whisper_api import transcribe_audio
import tempfile
import subprocess
import os

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)

    with tempfile.TemporaryDirectory() as tmpdir:
        ogg_path = os.path.join(tmpdir, "voice.ogg")
        wav_path = os.path.join(tmpdir, "voice.wav")

        await file.download_to_drive(ogg_path)
        subprocess.run(["ffmpeg", "-i", ogg_path, wav_path], check=True)

        transcript = transcribe_audio(wav_path)
        await update.message.reply_text(transcript)

app.add_handler(MessageHandler(filters.VOICE, handle_voice))


    app.run_polling()

if __name__ == "__main__":
    main()
