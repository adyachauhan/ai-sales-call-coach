import os

USE_FAKE_RAG = os.getenv("USE_FAKE_RAG", "false").lower() == "true"

def query_knowledge_base(query: str):
    """
    Returns relevant sales coaching context.
    Uses fake lightweight RAG in deployment environments.
    """

    # SAFE MODE (Render / low-memory)
    if USE_FAKE_RAG:
        return [
            "Always confirm next steps before ending a sales call.",
            "Address pricing objections proactively.",
            "Use discovery questions to uncover customer pain points.",
            "Clarify decision timelines and buying authority."
        ]

    # FULL RAG (LOCAL ONLY)
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = FAISS.load_local(
        "backend/rag/faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )

    docs = db.similarity_search(query, k=3)
    return [doc.page_content for doc in docs]