# AI-Powered Sales Call Improvement Platform (AWS-Native, Local MVP)

A web-based system that accepts a sales call audio recording, generates a transcript (mocked locally for now), and produces actionable sales improvement feedback using a **multi-agent** architecture and **RAG** (FAISS + embeddings).  
AWS components (S3, Transcribe, Bedrock) are planned as drop-in replacements in the next phase.

---

## ✅ Features (Current Local MVP)

- **Upload audio** via web UI (HTML) or FastAPI Swagger UI
- **Transcript display** (currently mocked; AWS Transcribe will replace)
- **AI analysis dashboard JSON** suitable for a sales manager:
  - Call summary
  - Customer intent
  - Sentiment
  - Rep performance (what went well / what to improve / score)
  - Objection analysis (missed objections, buying signals, missed opportunities)
  - Recommended next actions
- **Multi-agent system (3 agents)**:
  - Transcript Analyzer
  - Sales Coach (RAG-augmented)
  - Objection Expert
- **RAG knowledge base** using FAISS + HuggingFace embeddings, queried during analysis
- **LangChain orchestration** (agents executed via a LangChain runnable graph)

---

## 🧱 Tech Stack

**Backend**
- Python + FastAPI
- LangChain (`langchain-core`, `langchain-community`, `RunnableParallel`)
- FAISS vector store
- HuggingFace / Sentence-Transformers embeddings

**Frontend**
- Minimal HTML/JS (`frontend/index.html`)

**AWS (Next Phase)**
- S3 for storage
- AWS Transcribe for speech-to-text
- AWS Bedrock for LLM inference

---

## 📁 Project Structure
ai-sales-call-coach/
├─ backend/
│ ├─ agents/
│ │ ├─ transcript_analyzer.py
│ │ ├─ sales_coach.py
│ │ ├─ objection_expert.py
│ │ └─ final_report.py
│ ├─ rag/
│ │ ├─ build_index.py
│ │ ├─ query_rag.py
│ │ └─ faiss_index/ # index.faiss + index.pkl
│ ├─ orchestrator.py # LangChain multi-agent orchestration
│ └─ main.py # FastAPI app
├─ frontend/
│ └─ index.html
├─ sample_data/ # (add) sample audio file
├─ sample_output/ # (add) example output JSON
├─ requirements.txt
└─ README.md

---

## 🧠 Architecture Diagram

```mermaid
flowchart TD
  U[User] --> UI[Frontend: HTML Upload Page]
  UI -->|POST /upload-audio/| API[FastAPI Backend]

  API -->|Save file| LOCAL[(Local Storage: uploads/)]
  API -->|Mock transcript (AWS Transcribe later)| T[Transcript Text]

  API --> ORCH[LangChain Orchestrator<br/>RunnableParallel]

  ORCH --> A1[Agent 1: Transcript Analyzer]
  ORCH --> A2[Agent 2: Sales Coach]
  ORCH --> A3[Agent 3: Objection Expert]

  A2 --> RAG[RAG Retrieval]
  RAG --> VS[(FAISS Vector Store)]
  VS --> KB[Sales Coaching Knowledge Base<br/>(rag_data text chunks)]

  ORCH --> AGG[Final Report Aggregator<br/>(final_report.py)]
  AGG --> OUT[Dashboard JSON Response]

  OUT --> UI

## ⚙️ Setup Instructions

1. Clone the repository
```bash
git clone https://github.com/<your-username>/ai-sales-call-coach.git
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


### 🎧 Sample Audio
```md
## 🎧 Sample Audio

A sample sales call audio file is included under:
