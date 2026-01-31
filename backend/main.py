# backend/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import shutil
import os

app = FastAPI()

# Paths (absolute-safe)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))          # .../backend
PROJECT_ROOT = os.path.dirname(BASE_DIR)                       # .../ai-sales-call-coach
FRONTEND_INDEX = os.path.join(PROJECT_ROOT, "frontend", "index.html")

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def serve_ui():
    return FileResponse(FRONTEND_INDEX)


@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    # 1) Save uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2) Mock transcript (AWS Transcribe later)
    transcript = (
        "Hello, thank you for taking my call. "
        "I wanted to understand your current challenges "
        "and see if our solution could help."
    )

    # 3) Run LangChain multi-agent orchestration (agents + final report)
    dashboard = orchestrator.invoke({"transcript": transcript})

    return {
        "filename": file.filename,
        "transcript": transcript,
        "dashboard": dashboard
    }