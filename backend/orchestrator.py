# backend/orchestrator.py

from __future__ import annotations
from typing import Dict, Any

from langchain_core.runnables import RunnableLambda, RunnableParallel

from backend.agents.transcript_analyzer import transcript_analyzer_agent
from backend.agents.sales_coach import sales_coach_agent
from backend.agents.objection_expert import objection_expert_agent
from backend.agents.final_report import generate_final_report


def build_orchestrator():
    """
    Minimal LangChain orchestration (no LLM yet).
    - Runs agents in parallel
    - Aggregates into final dashboard report
    """

    analyze_transcript = RunnableLambda(lambda x: transcript_analyzer_agent(x["transcript"]))
    coach_sales = RunnableLambda(lambda x: sales_coach_agent(x["transcript"]))
    objection_expert = RunnableLambda(lambda x: objection_expert_agent(x["transcript"]))

    # Run 3 agents "collaboratively" (parallel execution graph)
    agents_parallel = RunnableParallel(
        transcript_analysis=analyze_transcript,
        sales_feedback=coach_sales,
        objection_feedback=objection_expert,
    )

    # Aggregate into final report
    aggregate = RunnableLambda(
        lambda outputs: generate_final_report(
            outputs["transcript_analysis"],
            outputs["sales_feedback"],
            outputs["objection_feedback"],
        )
    )

    # Compose chain: input -> run agents -> aggregate
    chain = agents_parallel | aggregate
    return chain