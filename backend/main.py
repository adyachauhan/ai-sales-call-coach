# backend/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
import shutil, os, uuid, traceback

from dotenv import load_dotenv
load_dotenv()

from botocore.exceptions import ClientError

from backend.agents.transcript_analyzer import transcript_analyzer_agent
from backend.agents.sales_coach import sales_coach_agent
from backend.agents.objection_expert import objection_expert_agent
from backend.agents.final_report import generate_final_report

from backend.aws.s3_utils import upload_file_to_s3
from backend.aws.transcribe_utils import start_transcription_job, wait_for_job, fetch_transcript_text

USE_MOCK_TRANSCRIPT = os.getenv("USE_MOCK_TRANSCRIPT", "false").lower() == "true"
MOCK_TRANSCRIPT_PATH = os.path.join("backend", "sample_transcripts", "sample_call.txt")


app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def serve_ui():
    return FileResponse("frontend/index.html")

@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    try:
        # 1) Save locally
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2) Upload to S3
        ext = (file.filename.split(".")[-1] or "").lower()
        if ext not in ("mp3", "wav", "m4a", "mp4"):
            ext = "mp3"

        s3_key = f"uploads/{uuid.uuid4()}-{file.filename}"
        media_s3_uri = upload_file_to_s3(file_path, s3_key)
        print("✅ Uploaded to S3:", media_s3_uri)

        # 3) Transcribe (or fallback)
        transcript = None

        if USE_MOCK_TRANSCRIPT:
            with open(MOCK_TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
                transcript = f.read()
            print("Using MOCK transcript (USE_MOCK_TRANSCRIPT=true)")

        else:
            job_name = f"sales-call-{uuid.uuid4().hex}"
            print("Starting Transcribe job:", job_name)

            try:
                start_transcription_job(
                    job_name=job_name,
                    media_s3_uri=media_s3_uri,
                    media_format=ext,
                    language_code="en-US",
                )

                job_resp = wait_for_job(job_name, timeout_seconds=300)
                status = job_resp["TranscriptionJob"]["TranscriptionJobStatus"]
                print("Transcribe status:", status)

                if status == "FAILED":
                    reason = job_resp["TranscriptionJob"].get("FailureReason", "Unknown")
                    return JSONResponse(
                        status_code=500,
                        content={"error": "Transcription failed", "reason": reason},
                    )

                transcript_uri = job_resp["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
                print("Transcript URI:", transcript_uri)

                transcript = fetch_transcript_text(transcript_uri)
                print("Transcript length:", len(transcript))

            except ClientError as ce:
                # If Transcribe isn't activated yet, fallback automatically
                code = ce.response.get("Error", {}).get("Code", "")
                msg = ce.response.get("Error", {}).get("Message", str(ce))
                print("Transcribe ClientError:", code, msg)

                if code in ("SubscriptionRequiredException", "OptInRequiredException"):
                    with open(MOCK_TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
                        transcript = f.read()
                    print("Transcribe not enabled yet — using MOCK transcript fallback")
                else:
                    raise

        # transcript must exist now
        if not transcript or not transcript.strip():
            return JSONResponse(
                status_code=500,
                content={"error": "Transcript is empty", "where": "transcription"},
            )

        # 4) Agents
        transcript_analysis = transcript_analyzer_agent(transcript)
        sentiment = transcript_analysis.get("sentiment")
        sales_feedback = sales_coach_agent(transcript, sentiment)
        objection_feedback = objection_expert_agent(transcript, sentiment)


        dashboard = generate_final_report(transcript_analysis, sales_feedback, objection_feedback)

        return {
            "filename": file.filename,
            "transcript": transcript,
            "dashboard": dashboard,
        }

    except Exception as e:
        # Always return JSON so frontend doesn't crash on .json()
        tb = traceback.format_exc()
        print("❌ ERROR in /upload-audio/:", tb)

        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": str(e),
                "where": "upload_audio",
            },
        )