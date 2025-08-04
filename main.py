import asyncio
import uvicorn
from fastapi import FastAPI
from bot import run_bot  # Импортируем функцию запуска бота

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Central AI Assistant is running."}

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_bot())  # Запускаем Telegram-бота параллельно с FastAPI

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
