from typing import Dict, List


def chunk_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 150
) -> List[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between 0 and chunk_size")

    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))

        if end == len(words):
            break

        start = end - overlap

    return chunks


def chunk_documents(
    documents: List[Dict],
    chunk_size: int = 800,
    overlap: int = 150
) -> List[Dict]:
    results = []

    for document in documents:
        chunks = chunk_text(
            document["content"],
            chunk_size=chunk_size,
            overlap=overlap
        )

        for index, chunk in enumerate(chunks):
            results.append({
                "id": f'{document["source"]}__chunk_{index}',
                "text": chunk,
                "source": document["source"],
                "file_type": document["file_type"],
                "chunk_index": index
            })

    return results
