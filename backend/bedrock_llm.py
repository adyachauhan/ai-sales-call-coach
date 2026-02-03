import json
import boto3
import os

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID")

bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)

def bedrock_json(prompt: str, max_tokens: int = 800) -> dict:
    """
    Callsison / Claude style payload (works for many Bedrock chat models).
    If your model is different, tell me the model_id and I’ll adjust payload.
    """
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": 0.2,
        "messages": [{"role": "user", "content": prompt}],
    }

    resp = bedrock.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json",
    )

    raw = json.loads(resp["body"].read())

    # Claude returns content list with text
    text = ""
    if "content" in raw and isinstance(raw["content"], list):
        text = raw["content"][0].get("text", "")
    else:
        # fallback: some models return 'outputText' etc.
        text = raw.get("outputText") or raw.get("generation") or ""

    # Extract JSON strictly
    text = text.strip()
    # If model wraps in ```json ...```
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        text = text.replace("json", "", 1).strip()

    return json.loads(text)