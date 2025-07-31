from fastapi import FastAPI, Request
from bot import process_telegram_update

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    await process_telegram_update(data)
    return {"ok": True}