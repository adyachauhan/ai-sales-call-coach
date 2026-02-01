# AI-Powered Sales Call Improvement Platform  
*(AWS-Native Design, Local MVP)*

A web-based system that accepts a sales call audio recording, generates a transcript (mocked locally for now), and produces actionable sales improvement feedback using a **multi-agent architecture** and **RAG (FAISS + embeddings)**.

AWS components (S3, Transcribe, Bedrock) are designed as **drop-in replacements** for the local MVP.

---
## 🌐 Live Demo

Public URL (Render):  
https://ai-sales-call-coach.onrender.com

You can upload a sample sales call audio file and view the AI-generated sales analysis dashboard directly in the browser.

## ✅ Features (Current Local MVP)

- Upload audio via **Web UI (HTML)** or **FastAPI Swagger UI**
- Transcript display *(currently mocked; AWS Transcribe will replace)*
- AI-generated **Sales Manager Dashboard JSON**, including:
  - Call summary
  - Customer intent
  - Sentiment
  - Rep performance (score, strengths, improvements)
  - Objection analysis (missed objections, buying signals)
  - Recommended next actions
- **Multi-agent system**:
  - Transcript Analyzer
  - Sales Coach *(RAG-augmented)*
  - Objection Expert
- **RAG knowledge base** using FAISS + HuggingFace embeddings
- **LangChain orchestration** using a runnable graph

---

## 🧱 Tech Stack

### Backend
- Python + FastAPI
- LangChain (`langchain-core`, `langchain-community`)
- FAISS vector store
- HuggingFace / Sentence-Transformers embeddings

### Frontend
- Minimal HTML + JavaScript (`frontend/index.html`)

### AWS (Next Phase)
- Amazon S3 (audio storage)
- AWS Transcribe (speech-to-text)
- AWS Bedrock (LLM inference)

---

## 📁 Project Structure

```text
ai-sales-call-coach/
├─ backend/
│  ├─ agents/
│  │  ├─ transcript_analyzer.py
│  │  ├─ sales_coach.py
│  │  ├─ objection_expert.py
│  │  └─ final_report.py
│  ├─ rag/
│  │  ├─ build_index.py
│  │  ├─ query_rag.py
│  │  └─ faiss_index/
│  │     ├─ index.faiss
│  │     └─ index.pkl
│  ├─ orchestrator.py
│  └─ main.py
├─ frontend/
│  └─ index.html
├─ sample_data/
│  └─ sample_sales_call.mp3
├─ sample_output/
│  └─ output.json
├─ requirements.txt
└─ README.md
```

---

### 🧠 Architecture Diagram

![Architecture Diagram](architecture.png)

**Flow:**  
Audio Upload → Transcript → RAG Retrieval → Multi-Agent Analysis → Aggregated Sales Dashboard → UI


## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/adyachauhan/ai-sales-call-coach.git
cd ai-sales-call-coach

2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Run the backend
python -m uvicorn backend.main:app --reload

5. Open the app
UI: http://127.0.0.1:8000
API docs: http://127.0.0.1:8000/docs


---

## 🎧 Sample Audio

A sample sales call audio file is included at:

sample_data/sample_sales_call.mp3

This file can be uploaded directly through the web UI or Swagger UI to test the system.

---

## 📊 Sample Output

An example AI-generated sales coaching report is available at:

sample_output/output.json

This demonstrates the full dashboard-style response returned by the API.
