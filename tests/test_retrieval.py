import pytest
from unittest.mock import MagicMock

from app.retrieval import search


def test_empty_chunks_return_zero():
    assert search.index_chunks([]) == 0


def test_stable_id_is_deterministic():
    chunk = {
        "source": "test.md",
        "file_type": "md",
        "chunk_index": 0,
        "text": "Test support document"
    }
    assert search._stable_id(chunk) == search._stable_id(chunk)


def test_stable_id_changes_when_text_changes():
    first = {
        "source": "test.md",
        "file_type": "md",
        "chunk_index": 0,
        "text": "First document"
    }
    second = {
        "source": "test.md",
        "file_type": "md",
        "chunk_index": 0,
        "text": "Second document"
    }
    assert search._stable_id(first) != search._stable_id(second)


def test_index_chunks_uses_embeddings(monkeypatch):
    collection = MagicMock()
    monkeypatch.setattr(search, "get_collection", lambda: collection)

    class FakeEmbeddings:
        def tolist(self):
            return [[0.1, 0.2, 0.3]]

    monkeypatch.setattr(
        search, "encode_texts", lambda texts: FakeEmbeddings()
    )

    chunks = [{
        "source": "test.md",
        "file_type": "md",
        "chunk_index": 0,
        "text": "Return policy information"
    }]

    assert search.index_chunks(chunks) == 1
    collection.upsert.assert_called_once()


def test_search_rejects_empty_query():
    with pytest.raises(ValueError):
        search.search_knowledge("")


def test_search_rejects_whitespace_query():
    with pytest.raises(ValueError):
        search.search_knowledge("   ")


def test_search_rejects_non_string_query():
    with pytest.raises(ValueError):
        search.search_knowledge(123)


def test_search_rejects_zero_top_k():
    with pytest.raises(ValueError):
        search.search_knowledge("return policy", top_k=0)


def test_search_rejects_negative_top_k():
    with pytest.raises(ValueError):
        search.search_knowledge("return policy", top_k=-1)


def test_search_empty_collection_returns_empty(monkeypatch):
    collection = MagicMock()
    collection.count.return_value = 0

    monkeypatch.setattr(search, "get_collection", lambda: collection)

    assert search.search_knowledge("return policy") == []
