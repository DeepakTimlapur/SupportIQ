from pathlib import Path
from typing import Dict

from app.ingestion.document_loader import load_documents
from app.ingestion.chunking import chunk_documents
from app.retrieval.search import index_chunks


def index_directory(directory: str) -> Dict:
    """
    Load supported documents, chunk their text, and index them in ChromaDB.
    """
    root = Path(directory)

    if not root.exists():
        raise FileNotFoundError(f"Document directory not found: {root}")

    documents = load_documents(str(root))

    if not documents:
        return {
            "documents_loaded": 0,
            "chunks_created": 0,
            "chunks_indexed": 0,
            "message": "No supported documents found."
        }

    chunks = chunk_documents(
        documents,
        chunk_size=800,
        overlap=150
    )

    indexed_count = index_chunks(chunks)

    return {
        "documents_loaded": len(documents),
        "chunks_created": len(chunks),
        "chunks_indexed": indexed_count,
        "message": "Document indexing completed."
    }


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    document_directory = project_root / "documents"

    result = index_directory(str(document_directory))

    print("\nSupportIQ Document Indexing Report")
    print("----------------------------------")
    for key, value in result.items():
        print(f"{key}: {value}")
