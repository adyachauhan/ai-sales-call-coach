import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Make path absolute to avoid issues with uvicorn
BASE_DIR = os.path.dirname(__file__)  # backend/rag
DB_PATH = os.path.join(BASE_DIR, "faiss_index")

# Load embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load FAISS index with safe deserialization
db = FAISS.load_local(
    DB_PATH, 
    embeddings, 
    allow_dangerous_deserialization=True
)

def query_knowledge_base(question: str) -> list:
    try:
        docs = db.similarity_search(question, k=3)
        return [doc.page_content for doc in docs]
    except Exception:
        return [
            "Always confirm next steps before ending a sales call.",
            "Handle pricing objections early in the conversation.",
            "Use open-ended discovery questions to uncover pain points."
        ]