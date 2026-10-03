from fastapi import FastAPI
from app.api import upload

app = FastAPI()
app.include_router(upload.router)

@app.get("/")
def root():
    return {"message": "RAG Chatbot API is running"}