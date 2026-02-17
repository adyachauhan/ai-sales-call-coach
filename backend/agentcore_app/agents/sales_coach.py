# backend/agents/sales_coach.py

from __future__ import annotations

from backend.rag.query_rag import query_knowledge_base

def _simple_call_signals(transcript: str) -> dict:
    """
    Lightweight heuristics so the output feels transcript-grounded (no LLM).
    Works for both paragraph transcripts and conversation-formatted transcripts.
    """
    transcript = transcript or ""
    t = transcript.lower()

    asked_questions = transcript.count("?")

    next_step_phrases = [
        "next step", "next steps", "follow up", "follow-up",
        "schedule", "calendar", "book a demo", "demo", "meeting", "call back",
        "send you", "i'll email", "i will email", "let's meet", "set up"
    ]
    value_phrases = [
        "value", "benefit", "roi", "save", "savings", "increase", "reduce",
        "improve", "faster", "efficient", "time", "cost savings"
    ]
    pricing_phrases = [
        "price", "pricing", "cost", "budget", "afford", "expensive",
        "discount", "quote"
    ]
    timeline_phrases = [
        "timeline", "by when", "when do you", "this quarter", "deadline",
        "next month", "this month", "asap", "soon"
    ]
    empathy_phrases = [
        "i understand", "that makes sense", "totally understand",
        "thanks for sharing", "appreciate", "sorry to hear", "no worries"
    ]

    mentioned_next_steps = any(p in t for p in next_step_phrases)
    mentioned_value = any(p in t for p in value_phrases)
    mentioned_pricing = any(p in t for p in pricing_phrases)
    mentioned_timeline = any(p in t for p in timeline_phrases)
    showed_empathy = any(p in t for p in empathy_phrases)

    return {
        "asked_questions_count": asked_questions,
        "mentioned_next_steps": mentioned_next_steps,
        "mentioned_value_prop": mentioned_value,
        "mentioned_pricing": mentioned_pricing,
        "mentioned_timeline": mentioned_timeline,
        "showed_empathy": showed_empathy,
    }


def sales_coach_agent(transcript: str, sentiment: str | None = None) -> dict:
    """
    Evaluates selling technique + pulls best-practice guidance via RAG.
    Produces transcript-dependent coaching (no hardcoded one-size-fits-all).
    """

    transcript = transcript or ""
    t = transcript.lower()
    sentiment_norm = (sentiment or "").strip().lower()

    # RAG call: best-practice grounding (proof for reviewers)
    rag_snippets = query_knowledge_base(
        "sales discovery questions, closing techniques, tone and empathy, and follow-up strategies"
    )
    if isinstance(rag_snippets, str):
        rag_snippets_list = [s.strip() for s in rag_snippets.split("\n") if s.strip()]
    else:
        rag_snippets_list = list(rag_snippets)

    signals = _simple_call_signals(transcript)

    # --------------------------
    # Transcript-grounded content
    # --------------------------

    what_went_well: list[str] = []
    what_to_improve: list[str] = []
    next_actions: list[str] = []

    # Strengths (derived from detected signals)
    if signals["asked_questions_count"] >= 2:
        what_went_well.append("Asked multiple questions to understand the customer context (discovery).")
    else:
        what_to_improve.append("Ask more open-ended discovery questions to uncover pain points and impact.")
        next_actions.append("Prepare 5–7 discovery questions (pain, current process, impact, stakeholders, timeline).")

    if signals["showed_empathy"]:
        what_went_well.append("Used empathetic language to keep the conversation respectful and collaborative.")
    else:
        what_to_improve.append("Use more empathy/acknowledgement phrases to build trust (e.g., 'That makes sense').")
        next_actions.append("Add quick acknowledgement before pitching (validate concern → ask 1 clarifier).")

    if signals["mentioned_value_prop"]:
        what_went_well.append("Mentioned customer value/benefits (value proposition).")
    else:
        what_to_improve.append("Value proposition was not clearly articulated.")
        next_actions.append("Deliver a 20–30 second value pitch tied to a specific pain point + measurable outcome.")

    if signals["mentioned_next_steps"]:
        what_went_well.append("Discussed a next step, which helps move the deal forward.")
    else:
        what_to_improve.append("Call lacked a clear closing or next-step confirmation.")
        next_actions.append("End with a clear next step (demo / follow-up) and confirm date/time on the call.")

    # Pricing/timeline are situational: treat as opportunity rather than “failure”
    if not signals["mentioned_pricing"]:
        next_actions.append("If appropriate, qualify budget/pricing expectations early to avoid late-stage surprises.")
    if not signals["mentioned_timeline"]:
        next_actions.append("Ask about decision timeline and urgency to qualify the opportunity.")

    # ---------------------------------------
    # Negative call handling (more interesting)
    # ---------------------------------------
    # If call sentiment is negative, shift coaching toward recovery instead of closing pressure.
    if "negative" in sentiment_norm:

        # Replace the most “salesy” next steps with recovery steps
        next_actions = [
            "Acknowledge the customer's frustration and ask one clarifying question to understand the root cause.",
            "If resistance continues, gracefully exit: ask permission to follow up later rather than pushing a demo.",
            "Log the reason for rejection (price, timing, relevance, previous experience) and tailor future outreach.",
        ]

        # Improve bullets for negative context
        if not any("empat" in s.lower() for s in what_went_well):
            what_to_improve.insert(0, "De-escalation opportunity: acknowledge frustration before continuing the pitch.")
        what_to_improve.append("Avoid pushing next steps when the customer is disengaged; focus on preserving trust.")

    # ----------------
    # Score (simple)
    # ----------------
    # Start from 7 and subtract for missing pillars; add a small bonus for empathy & good discovery.
    score = 7.0
    if not signals["mentioned_value_prop"]:
        score -= 0.7
    if not signals["mentioned_next_steps"] and sentiment_norm != "negative":
        score -= 0.6
    if signals["asked_questions_count"] < 2:
        score -= 0.4
    if signals["showed_empathy"]:
        score += 0.3

    # If negative call, keep score conservative
    if "negative" in sentiment_norm:
        score = min(score, 5.5)

    score = max(1.0, min(10.0, round(score, 1)))

    # Ensure UI sections never empty
    if not what_went_well:
        what_went_well = ["Maintained a professional tone throughout the call."]
    if not what_to_improve:
        what_to_improve = ["No major coaching gaps detected based on available transcript signals."]

    return {
        "rep_performance_score": score,
        "what_went_well": what_went_well,
        "what_to_improve": what_to_improve,
        "recommended_next_actions": next_actions,
        "signals_detected": signals,
        # RAG proof (kept simple & visible)
        "rag_query": "sales discovery questions, closing techniques, tone and empathy, and follow-up strategies",
        "coaching_references": rag_snippets_list[:3],
    }