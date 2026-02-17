from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Your existing paths
RAG_DATA_PATH = os.path.normpath(os.path.join(BASE_DIR, "../../rag_data"))
COMPANY_KB_ROOT = os.path.normpath(os.path.join(BASE_DIR, "../../company_kb"))

DB_PATH = os.path.join(BASE_DIR, "faiss_index")

# Set to a company folder name (e.g., "signiance") to only index that company.
# Set to None to index ALL companies inside company_kb/
COMPANY_FILTER = "signiance"  # or None


def iter_text_files(root_dir: str, extensions=(".txt", ".md")):
    """Yield absolute file paths for matching extensions under root_dir (recursive)."""
    if not os.path.isdir(root_dir):
        return
    for dirpath, _, filenames in os.walk(root_dir):
        for fn in filenames:
            if fn.lower().endswith(extensions):
                yield os.path.join(dirpath, fn)


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def relpath(path: str, start: str) -> str:
    try:
        return os.path.relpath(path, start)
    except Exception:
        return path


documents = []

# 1) Load generic rag_data/
rag_files = list(iter_text_files(RAG_DATA_PATH, extensions=(".txt",)))
for fp in rag_files:
    text = read_file(fp).strip()
    if not text:
        continue
    documents.append(
        Document(
            page_content=text,
            metadata={
                "source": f"rag_data/{relpath(fp, RAG_DATA_PATH)}",
                "kb_type": "generic",
            },
        )
    )

# 2) Load company_kb/<company>/
company_files = []
if os.path.isdir(COMPANY_KB_ROOT):
    if COMPANY_FILTER:
        company_dirs = [os.path.join(COMPANY_KB_ROOT, COMPANY_FILTER)]
    else:
        company_dirs = [
            os.path.join(COMPANY_KB_ROOT, d)
            for d in os.listdir(COMPANY_KB_ROOT)
            if os.path.isdir(os.path.join(COMPANY_KB_ROOT, d))
        ]

    for company_dir in company_dirs:
        company_name = os.path.basename(company_dir)
        for fp in iter_text_files(company_dir, extensions=(".txt", ".md")):
            company_files.append(fp)
            text = read_file(fp).strip()
            if not text:
                continue
            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": f"company_kb/{company_name}/{relpath(fp, company_dir)}",
                        "kb_type": "company",
                        "company": company_name,
                    },
                )
            )

print("==== Ingestion Summary ====")
print("RAG_DATA_PATH:", RAG_DATA_PATH)
print("company_kb root:", COMPANY_KB_ROOT)
print("COMPANY_FILTER:", COMPANY_FILTER)
print("Generic files found:", len(rag_files))
print("Company files found:", len(company_files))
print("Raw documents loaded:", len(documents))

# Chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
texts = text_splitter.split_documents(documents)
print("Number of text chunks:", len(texts))

# Embeddings + FAISS
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = FAISS.from_documents(texts, embeddings)
db.save_local(DB_PATH)

print("RAG index created successfully")
print("DB_PATH:", DB_PATH)