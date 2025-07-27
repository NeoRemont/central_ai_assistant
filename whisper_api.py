import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def transcribe_voice(audio_data):
    response = openai.Audio.transcribe(
        model="whisper-1",
        file=("voice.ogg", audio_data, "audio/ogg"),
        language=os.getenv("WHISPER_LANGUAGE", "ru")
    )
    return response["text"]
