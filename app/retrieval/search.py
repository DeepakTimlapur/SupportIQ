from pathlib import Path
from typing import Dict, List
import hashlib

import chromadb

from app.retrieval.embeddings import encode_query, encode_texts


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHROMA_PATH = PROJECT_ROOT / "data" / "chroma_db"
COLLECTION_NAME = "supportiq_knowledge"


def get_collection():
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(CHROMA_PATH))

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )


def _stable_id(chunk: Dict) -> str:
    identity = (
        f'{chunk["source"]}|'
        f'{chunk.get("file_type", "")}|'
        f'{chunk.get("chunk_index", 0)}|'
        f'{chunk["text"]}'
    )
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def index_chunks(chunks: List[Dict]) -> int:
    if not chunks:
        return 0

    collection = get_collection()

    ids = [_stable_id(chunk) for chunk in chunks]
    texts = [chunk["text"] for chunk in chunks]

    embeddings = encode_texts(texts)

    metadatas = [
        {
            "source": chunk["source"],
            "file_type": chunk.get("file_type", ""),
            "chunk_index": int(chunk.get("chunk_index", 0))
        }
        for chunk in chunks
    ]

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    return len(ids)


def search_knowledge(query: str, top_k: int = 5) -> List[Dict]:
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Search query must be a non-empty string")

    if top_k <= 0:
        raise ValueError("top_k must be positive")

    collection = get_collection()

    if collection.count() == 0:
        return []

    query_embedding = encode_query(query)

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"]
    )

    matches = []

    for index, document in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][index]
        distance = results["distances"][0][index]

        matches.append({
            "text": document,
            "source": metadata["source"],
            "file_type": metadata.get("file_type", ""),
            "chunk_index": metadata.get("chunk_index", 0),
            "distance": float(distance),
            "similarity": float(1.0 - distance)
        })

    return matches
