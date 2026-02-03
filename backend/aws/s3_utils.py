# backend/aws/s3_utils.py
import os
import boto3

AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
S3_BUCKET = os.getenv("S3_BUCKET")

s3 = boto3.client("s3", region_name=AWS_REGION)

def upload_file_to_s3(local_path: str, key: str) -> str:
    """
    Uploads a local file to S3 and returns the S3 URI.
    """
    if not S3_BUCKET:
        raise RuntimeError("S3_BUCKET env var not set")

    s3.upload_file(local_path, S3_BUCKET, key)
    return f"s3://{S3_BUCKET}/{key}"