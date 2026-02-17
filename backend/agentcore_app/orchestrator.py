# backend/agentcore_app/orchestrator.py
from backend.agents.transcript_analyzer import transcript_analyzer_agent
from backend.agents.sales_coach import sales_coach_agent
from backend.agents.objection_expert import objection_expert_agent
from backend.agents.final_report import generate_final_report

from typing import Any, Dict
import concurrent.futures as cf

# ✅ Use relative imports inside the package
from .agents.transcript_analyzer import transcript_analyzer_agent
from .agents.sales_coach import sales_coach_agent
from .agents.objection_expert import objection_expert_agent
from .agents.final_report import generate_final_report


def run_pipeline(payload: Dict[str, Any]) -> Dict[str, Any]:
    transcript: str = payload["transcript"]["text"]

    # Optional inputs from FastAPI (fine if absent)
    sentiment = payload.get("sentiment")          # can be None
    # You are currently NOT passing rag_context into sales_coach_agent (it doesn't accept it)

    # Run in parallel (like your old RunnableParallel)
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        # ✅ transcript_analyzer_agent(transcript: str)
        f1 = ex.submit(transcript_analyzer_agent, transcript)

        # ✅ sales_coach_agent(transcript: str, sentiment: Optional[str] = None)
        f2 = ex.submit(sales_coach_agent, transcript, sentiment)

        # ✅ objection_expert_agent(transcript: str, sentiment: str)
        # If sentiment is None, pass a safe default so it doesn’t crash.
        f3 = ex.submit(objection_expert_agent, transcript, sentiment or "Neutral")

        transcript_analysis = f1.result()
        sales_feedback = f2.result()
        objection_feedback = f3.result()

    # Aggregate into final report
    return generate_final_report(
        transcript_analysis,
        sales_feedback,
        objection_feedback,
    )