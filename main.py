from fastapi import FastAPI
from bot import start_bot

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await start_bot()
