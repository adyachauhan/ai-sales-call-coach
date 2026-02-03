# backend/aws/transcribe_utils.py
import os
import time
import json
import urllib.request
import boto3

AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")

transcribe = boto3.client("transcribe", region_name=AWS_REGION)

def start_transcription_job(job_name: str, media_s3_uri: str, media_format: str = "mp3", language_code: str = "en-US"):
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={"MediaFileUri": media_s3_uri},
        MediaFormat=media_format,
        LanguageCode=language_code,
    )

def wait_for_job(job_name: str, timeout_seconds: int = 300) -> dict:
    """
    Polls Transcribe until completed/failed.
    """
    start = time.time()
    while True:
        resp = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        status = resp["TranscriptionJob"]["TranscriptionJobStatus"]

        if status in ("COMPLETED", "FAILED"):
            return resp

        if time.time() - start > timeout_seconds:
            raise TimeoutError("Transcribe job timed out")

        time.sleep(3)

def fetch_transcript_text(transcript_file_uri: str) -> str:
    """
    Downloads the transcript JSON from the TranscriptFileUri and extracts the text.
    """
    with urllib.request.urlopen(transcript_file_uri) as f:
        data = json.loads(f.read().decode("utf-8"))

    # Standard Transcribe JSON structure
    return data["results"]["transcripts"][0]["transcript"]