from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/ask")
def ask_endpoint():
    return {"response": "Assistant is active."}
