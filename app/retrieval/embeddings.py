from functools import lru_cache
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    """Load the embedding model once and reuse it."""
    return SentenceTransformer(MODEL_NAME)


def get_embedding_dimension() -> int:
    """Return the model's output embedding dimension."""
    dimension = get_model().get_embedding_dimension()

    if dimension is None:
        raise RuntimeError("Could not determine embedding dimension")

    return int(dimension)


def encode_texts(
    texts: List[str],
    batch_size: int = 32
) -> np.ndarray:
    """Convert multiple text passages into normalized embeddings."""
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")

    if not texts:
        return np.empty((0, get_embedding_dimension()), dtype=np.float32)

    if any(not isinstance(text, str) or not text.strip() for text in texts):
        raise ValueError("Every input must be a non-empty string")

    embeddings = get_model().encode(
        texts,
        batch_size=batch_size,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    return np.asarray(embeddings, dtype=np.float32)


def encode_query(query: str) -> np.ndarray:
    """Convert one search query into a normalized embedding."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query must be a non-empty string")

    return encode_texts([query])[0]

