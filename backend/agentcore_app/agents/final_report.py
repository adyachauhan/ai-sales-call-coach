def build_agent_consensus(
    transcript_analysis: dict,
    sales_feedback: dict,
    objection_feedback: dict,
) -> dict:
    transcript_analysis = transcript_analysis or {}
    sales_feedback = sales_feedback or {}
    objection_feedback = objection_feedback or {}

    strengths = []
    gaps = []

    signals = sales_feedback.get("signals_detected") or {}

    # --- Strengths ---
    if (sales_feedback.get("rep_performance_score") or 0) >= 7:
        strengths.append("overall selling effectiveness")

    if signals.get("mentioned_value_prop"):
        strengths.append("clear value articulation")

    if signals.get("mentioned_next_steps"):
        strengths.append("clear next-step confirmation")

    if objection_feedback.get("buying_signals"):
        neutral = any(
            "neutral" in s.lower()
            for s in objection_feedback.get("buying_signals", [])
        )
        if not neutral:
            strengths.append("positive customer engagement")

    # --- Gaps ---
    if (sales_feedback.get("rep_performance_score") or 10) < 6:
        gaps.append("selling technique consistency")

    if not signals.get("mentioned_value_prop"):
        gaps.append("value proposition clarity")

    if not signals.get("mentioned_next_steps"):
        gaps.append("closing and next-step confirmation")

    if objection_feedback.get("missed_objections"):
        gaps.append("proactive objection handling")

    if objection_feedback.get("missed_opportunities"):
        gaps.append("deeper discovery and qualification")

    # --- Compose message ---
    if strengths and gaps:
        assessment = (
            "Agents agree the call showed strengths in "
            + ", ".join(strengths)
            + ", but improvements are needed in "
            + ", ".join(gaps)
            + "."
        )
    elif strengths:
        assessment = (
            "Agents agree the call was strong, particularly in "
            + ", ".join(strengths)
            + "."
        )
    elif gaps:
        assessment = (
            "Agents agree improvement is needed, mainly in "
            + ", ".join(gaps)
            + "."
        )
    else:
        assessment = (
            "Agents could not extract enough signal from the call "
            "to form a confident assessment."
        )

    return {"overall_assessment": assessment}

def generate_final_report(transcript_analysis: dict, sales_feedback: dict, objection_feedback: dict) -> dict:
    transcript_analysis = transcript_analysis or {}
    sales_feedback = sales_feedback or {}
    objection_feedback = objection_feedback or {}

    return {
        "report_version": "v1",

        "call_summary": (
            transcript_analysis.get("call_summary")
            or transcript_analysis.get("summary")
        ),
        "customer_intent": transcript_analysis.get("customer_intent"),
        "sentiment": transcript_analysis.get("sentiment"),

        "rep_performance": {
            "score": sales_feedback.get("rep_performance_score"),
            "what_went_well": sales_feedback.get("what_went_well") or [],
            "what_to_improve": sales_feedback.get("what_to_improve") or [],
            "signals_detected": sales_feedback.get("signals_detected"),
        },

        "objection_analysis": {
            "missed_objections": objection_feedback.get("missed_objections") or [],
            "buying_signals": objection_feedback.get("buying_signals") or [],
            "missed_opportunities": objection_feedback.get("missed_opportunities") or [],
            "rag_context_used": objection_feedback.get("rag_context_used"),
        },

        "recommended_next_actions": sales_feedback.get("recommended_next_actions") or [],

        # Explicit RAG proof (single place)
        "rag": {
            "query": sales_feedback.get("rag_query"),
            "top_snippets": sales_feedback.get("coaching_references") or [],
        },

        "agent_consensus": build_agent_consensus(
            transcript_analysis, sales_feedback, objection_feedback
        ),

    }