import os

USE_FAKE_RAG = os.getenv("USE_FAKE_RAG", "false").lower() == "true"

FAISS_PATH = "backend/rag/faiss_index"


def query_knowledge_base(query: str, company: str = None):
    """
    Returns relevant sales coaching context.

    Args:
        query (str): user query
        company (str | None): optional company filter (e.g. "signiance")

    Behavior:
    - fake lightweight RAG in deployment environments
    - real FAISS retrieval locally
    - prioritizes company-specific KB if company is provided
    """

    # SAFE MODE (Render / low-memory)
    if USE_FAKE_RAG:
        return [
            "Always confirm next steps before ending a sales call.",
            "Address pricing objections proactively.",
            "Use discovery questions to uncover customer pain points.",
            "Clarify decision timelines and buying authority."
        ]

    # FULL RAG (LOCAL)
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = FAISS.load_local(
        FAISS_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    results = []

    # 1Try company-specific retrieval first
    if company:
        company_docs = db.similarity_search(
            query,
            k=5,
            filter={"company": company}
        )
        results.extend(company_docs)

    # 2Fallback / supplement with generic knowledge
    generic_docs = db.similarity_search(
        query,
        k=5,
        filter={"kb_type": "generic"}
    )

    results.extend(generic_docs)

    # 3Deduplicate + keep top context
    seen = set()
    final_docs = []

    for doc in results:
        if doc.page_content not in seen:
            seen.add(doc.page_content)
            final_docs.append(doc)

        if len(final_docs) >= 5:
            break

    return [doc.page_content for doc in final_docs]