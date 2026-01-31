from backend.rag.query_rag import query_knowledge_base

def objection_expert_agent(transcript: str) -> dict:
    rag_context = query_knowledge_base(
        "common sales objections and effective objection handling techniques"
    )

    return {
        "missed_objections": [
            "Potential budget concerns were not proactively addressed",
            "Implementation effort and timeline were not discussed"
        ],
        "buying_signals": [
            "Customer willingly answered discovery questions",
            "Customer did not express negative sentiment"
        ],
        "missed_opportunities": [
            "Could have explored urgency or decision timeline",
            "Could have asked about current solution pain points"
        ],
        # RAG proof
        "rag_context_used": rag_context
    }