import re
from typing import Dict, List

from app.retrieval.search import search_knowledge
from app.retrieval.embeddings import encode_texts, encode_query
from app.assistant.safety import (
    FALLBACK_MESSAGE,
    is_relevant,
    validate_question
)


def extract_relevant_sentences(
    question: str,
    document_text: str,
    max_sentences: int = 3
) -> List[str]:
    # Split on sentence boundaries and common product-field boundaries.
    parts = re.split(
        r'(?<=[!?])\s+|(?<=\.)\s+(?=[A-Z#])|'
        r'\s+(?=(?:Category|Display|Battery life|Water resistance|'
        r'Warranty|Driver size|Connectivity|Capacity|Output|Ports|'
        r'Playback time|Charging case):)',
        document_text
    )

    sentences = [
        re.sub(r'\s+', ' ', part).strip()
        for part in parts
        if len(part.strip()) > 15
        and not part.strip().startswith("#")
        and not part.strip().startswith("DOCUMENT TYPE:")
    ]

    if not sentences:
        return []

    vectors = encode_texts(sentences)
    query_vector = encode_query(question)

    scores = vectors @ query_vector
    ranked = sorted(
        zip(sentences, scores.tolist()),
        key=lambda item: item[1],
        reverse=True
    )

    selected = [
        sentence for sentence, score in ranked[:max_sentences]
        if score >= 0.20
    ]

    return selected


def generate_answer(question: str, top_k: int = 3) -> Dict:
    validate_question(question)

    if top_k <= 0:
        raise ValueError("top_k must be positive")

    results = search_knowledge(question, top_k=top_k)

    if not is_relevant(results):
        return {
            "answer": FALLBACK_MESSAGE,
            "sources": [],
            "confidence": 0.0,
            "grounded": False
        }

    best_result = results[0]

    relevant_sentences = extract_relevant_sentences(
        question,
        best_result["text"]
    )

    if not relevant_sentences:
        return {
            "answer": FALLBACK_MESSAGE,
            "sources": [],
            "confidence": 0.0,
            "grounded": False
        }

    return {
        "answer": " ".join(relevant_sentences),
        "sources": [
            {
                "document": best_result["source"],
                "similarity": round(best_result["similarity"], 4)
            }
        ],
        "confidence": round(best_result["similarity"], 4),
        "grounded": True
    }
