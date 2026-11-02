# SupportIQ – AI-Powered Customer Support Intelligence

SupportIQ is an AI-powered customer support knowledge assistant. It uses Retrieval-Augmented Generation (RAG) to retrieve relevant information from an indexed knowledge base and provide source-grounded answers through a web application.

## Features
- Natural-language customer support chat
- Semantic search using Sentence Transformers
- Extractive RAG answer generation
- Source attribution and retrieval similarity
- Knowledge-base dashboard and document explorer
- Persistent ChromaDB vector storage
- Document indexing and re-indexing
- Safe fallback for unsupported questions

## Technology Stack
| Layer | Technologies |
|---|---|
| Frontend | React, TypeScript, Vite, CSS |
| Backend | Python, FastAPI, Uvicorn |
| Embeddings | Sentence Transformers, all-MiniLM-L6-v2 |
| Vector Database | ChromaDB |
| Document Processing | PyMuPDF, python-docx |
| Testing | Pytest |

## Architecture
1. User submits a question through the React interface.
2. FastAPI validates the question.
3. Sentence Transformers creates the query embedding.
4. ChromaDB retrieves relevant knowledge-base chunks.
5. The RAG pipeline extracts relevant answer passages.
6. The API returns the answer, source information, and retrieval similarity.

## Project Structure
```text
SupportIQ/
├── app/
│   ├── assistant/
│   ├── evaluation/
│   ├── ingestion/
│   ├── retrieval/
│   ├── services/
│   └── main.py
├── documents/
│   ├── policies/
│   ├── faqs/
│   ├── product_guides/
│   └── conversations/
├── frontend/
├── tests/
├── data/
├── reports/
├── requirements.txt
└── generate_conversations.py
```

## Setup

### 1. Backend
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at `http://127.0.0.1:8000`.

### 2. Frontend
Open another terminal:
```powershell
Set-Location frontend
npm install
npm run dev
```

Frontend runs at `http://127.0.0.1:5173`.

## API Endpoints
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Backend health check |
| POST | `/api/ask` | Ask a knowledge-base question |
| POST | `/api/index` | Index knowledge-base documents |
| GET | `/api/knowledge/stats` | Knowledge-base statistics |
| GET | `/api/knowledge/documents` | List indexed documents |

## Testing
```powershell
python -m pytest -q
python -m compileall -q app tests
```

The current validated test suite contains 31 passing tests. The React production build also passes.

## Demo Data and Limitations
- The included ShopEase knowledge base is demonstration content.
- Generated support conversations are synthetic examples, not real customer interactions.
- Answer generation is extractive RAG; this implementation does not use an external LLM to generate answers.
- Retrieval similarity is a ranking score, not a calibrated probability.
- ChromaDB data is locally persisted and can be rebuilt by indexing the documents.

## License
Add a license before distributing this project if you intend to make it open source.
