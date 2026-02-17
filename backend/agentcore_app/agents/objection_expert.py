# backend/agents/objection_expert.py

from backend.rag.query_rag import query_knowledge_base


def objection_expert_agent(transcript: str, sentiment: str) -> dict:
    """
    Objection & Opportunity Expert.

    Goal:
    - Detect objections / buying signals / missed opportunities *from the transcript*.
    - Use RAG as best-practice grounding (shown in output as proof).
    - Keep outputs dynamic and appropriate for negative calls vs normal calls.
    """

    transcript = transcript or ""
    t = transcript.lower()

    # -------------------------
    # 1) Negative-call pathway
    # -------------------------
    # If the call is negative, coach for recovery (de-escalate + preserve relationship),
    # NOT for closing and pushing next steps.
    if (sentiment or "").strip().lower() == "negative":
        rag_context = query_knowledge_base(
            "handling negative or resistant sales conversations: de-escalation, empathy, and graceful exit"
        )

        # Try to ground in transcript with a couple of lightweight cues
        hard_rejection = any(
            p in t for p in ["not interested", "stop calling", "don't call", "do not call", "leave me alone"]
        )
        anger = any(
            p in t for p in ["annoyed", "angry", "frustrated", "upset", "rude", "waste of time"]
        )

        missed_objections = []
        buying_signals = []
        missed_opportunities = []

        # Objections (for negative calls, these are typically resistance reasons)
        if hard_rejection:
            missed_objections.append("Customer expressed a clear rejection; the underlying reason was not explored.")
        if anger:
            missed_objections.append("Customer frustration was present; emotional concern was not acknowledged explicitly.")

        if not missed_objections:
            missed_objections.append("Customer sentiment was negative; the specific cause of resistance was not clearly uncovered.")

        # Buying signals (usually none on negative calls; keep it explicit)
        buying_signals.append("No buying signals detected due to customer resistance / disengagement.")

        # Opportunities (recovery-oriented)
        missed_opportunities.append("Acknowledge the customer's frustration to de-escalate the conversation.")
        missed_opportunities.append("Ask one short, low-effort clarifying question to uncover the root issue (if the customer is willing).")
        missed_opportunities.append("Gracefully end the call if resistance continues, to protect trust and brand perception.")

        return {
            "missed_objections": missed_objections,
            "buying_signals": buying_signals,
            "missed_opportunities": missed_opportunities,
            "rag_context_used": rag_context,
        }

    # ---------------------------------
    # 2) Normal-call pathway (heuristic)
    # ---------------------------------

    # Expanded phrase sets for better recall (still simple & explainable)
    budget_phrases = [
        "budget", "price", "pricing", "cost", "afford", "expensive",
        "reasonable", "within range", "approved", "discount"
    ]
    timeline_phrases = [
        "timeline", "deadline", "by when", "this month", "next month", "this quarter",
        "asap", "soon", "right away", "later this year"
    ]
    current_solution_phrases = [
        "currently using", "current solution", "existing system", "today we use", "right now we use"
    ]
    competitor_phrases = [
        "competitor", "alternative", "other vendor", "other option"
    ]
    positive_phrases = [
        "sounds good", "interested", "makes sense", "that helps",
        "that works", "okay", "great", "perfect", "go ahead", "let's do it"
    ]

    mentioned_budget = any(p in t for p in budget_phrases)
    mentioned_timeline = any(p in t for p in timeline_phrases)
    mentioned_current_solution = any(p in t for p in current_solution_phrases)
    mentioned_competitor = any(p in t for p in competitor_phrases)
    positive_language = any(p in t for p in positive_phrases)

    missed_objections = []
    buying_signals = []
    missed_opportunities = []

    # Objection risks / missed objections
    if not mentioned_budget:
        missed_objections.append("Budget/pricing topic was not discussed (risk of late-stage price objection).")
        missed_opportunities.append("Ask about budget range early and position value/ROI accordingly.")
    if not mentioned_timeline:
        missed_objections.append("Decision timeline was not clarified (urgency and priority unknown).")
        missed_opportunities.append("Ask what timing the customer is targeting and what drives that deadline.")

    # Opportunities for stronger discovery / qualification
    if not mentioned_current_solution:
        missed_opportunities.append("Explore the customer's current solution/process to surface pain points and impact.")
    if mentioned_competitor:
        buying_signals.append("Customer mentioned alternatives/competitors, indicating active evaluation.")
        missed_opportunities.append("Ask what they like/dislike about alternatives and differentiate clearly.")

    # Buying signals
    if positive_language:
        buying_signals.append("Customer used positive language indicating openness or interest.")
    if not buying_signals:
        buying_signals.append("Customer engagement appeared neutral with no explicit buying signals detected.")

    # Fallback: keep UI sections non-empty
    if not missed_objections:
        missed_objections.append("No explicit objections were raised or missed in this call.")

    # RAG grounding
    rag_context = query_knowledge_base(
        "common sales objections and effective objection handling techniques"
    )

    return {
        "missed_objections": missed_objections,
        "buying_signals": buying_signals,
        "missed_opportunities": missed_opportunities,
        "rag_context_used": rag_context,
    }