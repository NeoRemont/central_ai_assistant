import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-1")

def transcribe_voice(audio_bytes: bytes, filename: str = "voice.wav") -> str:
    try:
        result = client.audio.transcriptions.create(
            model=WHISPER_MODEL,
            file=(filename, audio_bytes, "audio/wav"),
        )
        return result.text
    except Exception as e:
        print("[ERROR][WHISPER]", e)
        return ""