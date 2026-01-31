from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "../../rag_data")
DB_PATH = os.path.join(BASE_DIR, "faiss_index")

documents = []

for file in os.listdir(DATA_PATH):
    if file.endswith(".txt"):
        with open(os.path.join(DATA_PATH, file), "r", encoding="utf-8") as f:
            documents.append(f.read())

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

texts = text_splitter.create_documents(documents)
print("Number of text chunks:", len(texts))

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = FAISS.from_documents(texts, embeddings)
db.save_local(DB_PATH)

print("RAG index created successfully")

print("DATA_PATH:", DATA_PATH)
print("Files found:", os.listdir(DATA_PATH))
