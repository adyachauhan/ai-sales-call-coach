# backend/agentcore_app/agent.py
from __future__ import annotations

from typing import Any, Dict, Optional

from backend.agentcore_app.orchestrator import run_pipeline


def handler(event: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    AgentCore runtime entrypoint.
    event: JSON payload from FastAPI.
    Returns: JSON-serializable dict (your dashboard response).
    """
    try:
        # minimal sanity check (optional but helpful)
        if "transcript" not in event:
            raise ValueError("Missing 'transcript' in payload")
        if isinstance(event["transcript"], dict) and "text" not in event["transcript"]:
            raise ValueError("Missing 'transcript.text' in payload")

        return run_pipeline(event)

    except Exception as e:
        # Keep failures JSON so FastAPI/UI can handle them
        return {
            "call_id": event.get("call_id", "unknown"),
            "error": {
                "type": e.__class__.__name__,
                "message": str(e),
            },
        }