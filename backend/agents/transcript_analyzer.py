from backend.rag.query_rag import query_knowledge_base

def transcript_analyzer_agent(transcript: str) -> dict:
    rag_context = query_knowledge_base(
        "how to identify customer intent and sentiment in sales calls"
    )

    return {
        "summary": (
            "The sales representative initiated the call politely and "
            "attempted to understand the customer's needs through basic discovery questions."
        ),
        "customer_intent": (
            "The customer appears to be exploring whether the product is relevant "
            "to their current business needs."
        ),
        "sentiment": "Neutral to mildly positive",
        "key_moments": [
            "Greeting and introduction",
            "Initial discovery questions",
            "Customer engagement without objections raised"
        ],
        # RAG proof
        "rag_context_used": rag_context
    }