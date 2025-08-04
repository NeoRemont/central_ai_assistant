import os
import asyncio
from fastapi import FastAPI, Body
from gpt import ask_gpt
from bot import run_bot  # async

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Central AI Assistant is running."}

@app.post("/ask")
async def ask_endpoint(payload: dict = Body(...)):
    message = (payload or {}).get("message", "")
    reply = ask_gpt(message)
    return {"response": reply}

@app.on_event("startup")
async def startup():
    asyncio.create_task(run_bot())

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "10000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)