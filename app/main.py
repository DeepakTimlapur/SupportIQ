from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.assistant.generator import generate_answer
from app.ingestion.indexer import index_directory
from app.retrieval.search import get_collection


app = FastAPI(
    title="SupportIQ API",
    description="AI-powered customer support intelligence using RAG",
    version="1.0.0"
)


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=3, ge=1, le=10)


class SourceResponse(BaseModel):
    document: str
    similarity: float


class AskResponse(BaseModel):
    answer: str
    sources: List[SourceResponse]
    confidence: float
    grounded: bool


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "SupportIQ API",
        "version": "1.0.0"
    }


@app.post("/api/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    try:
        return generate_answer(
            request.question,
            top_k=request.top_k
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing the question."
        )


@app.post("/api/index")
def index_knowledge_base():
    project_root = Path(__file__).resolve().parents[1]
    documents_path = project_root / "documents"

    try:
        result = index_directory(str(documents_path))
        return result
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Knowledge-base indexing failed."
        )


@app.get("/api/knowledge/stats")
def knowledge_stats():
    collection = get_collection()

    return {
        "collection": collection.name,
        "total_chunks": collection.count(),
        "storage": "Persistent ChromaDB"
    }


@app.get("/api/knowledge/documents")
def knowledge_documents():
    project_root = Path(__file__).resolve().parents[1]
    documents_path = project_root / "documents"
    supported = {".pdf", ".docx", ".txt", ".md"}

    collection = get_collection()
    records = collection.get(include=["metadatas"])
    indexed_counts = {}

    for metadata in (records.get("metadatas") or []):
        if metadata:
            source = metadata.get("source")
            if source:
                indexed_counts[source] = indexed_counts.get(source, 0) + 1

    documents = []
    if documents_path.exists():
        for path in sorted(documents_path.rglob("*")):
            if path.is_file() and path.suffix.lower() in supported:
                documents.append({
                    "name": path.name,
                    "path": str(path.relative_to(documents_path)).replace("\\", "/"),
                    "category": path.parent.name.replace("_", " ").title(),
                    "file_type": path.suffix.lower().replace(".", "").upper(),
                    "size_bytes": path.stat().st_size,
                    "modified": path.stat().st_mtime,
                    "indexed_chunks": indexed_counts.get(path.name, 0)
                })

    return {
        "total_documents": len(documents),
        "total_chunks": collection.count(),
        "documents": documents
    }
