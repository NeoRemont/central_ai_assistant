import os
import tempfile
from io import BytesIO

import httpx
from pydub import AudioSegment
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from whisper_api import transcribe_voice

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
SERVICE_PORT = int(os.environ.get("PORT", "10000"))
LOCAL_ASK_URL = f"http://127.0.0.1:{SERVICE_PORT}/ask"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Пришлите текст или голосовое.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправьте текст — отвечу. Голос — распознаю и отвечу.")

async def process_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(LOCAL_ASK_URL, json={"message": text})
            data = r.json()
        reply = data.get("response", "Нет ответа.")
    except Exception as e:
        print("[ERROR][TEXT]", e)
        reply = "Ошибка при обращении к нейропомощнику."
    await update.message.reply_text(reply)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        voice = update.message.voice
        if not voice:
            await update.message.reply_text("Не удалось прочитать голосовое.")
            return

        tg_file = await context.bot.get_file(voice.file_id)

        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as ogg_f:
            await tg_file.download_to_drive(ogg_f.name)
            ogg_path = ogg_f.name

        audio = AudioSegment.from_file(ogg_path)
        wav_io = BytesIO()
        audio.export(wav_io, format="wav")
        wav_bytes = wav_io.getvalue()

        text = transcribe_voice(wav_bytes, filename="voice.wav") or ""
        if not text:
            await update.message.reply_text("Не удалось распознать аудио.")
            return

        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(LOCAL_ASK_URL, json={"message": text})
            data = r.json()
        reply = data.get("response", "Нет ответа.")
        await update.message.reply_text(reply)

    except Exception as e:
        print("[ERROR][VOICE]", e)
        await update.message.reply_text("Ошибка при обработке голосового.")

async def run_bot():
    if not TELEGRAM_TOKEN:
        print("[WARN] TELEGRAM_TOKEN не задан — бот не запустится.")
        return

    app = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_text))

    await app.initialize()
    await app.start()
    print("[BOT] Polling started")
    await app.updater.start_polling()