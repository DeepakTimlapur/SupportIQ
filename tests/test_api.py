from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.main import app
from app import main


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "SupportIQ API"


def test_knowledge_stats_endpoint(monkeypatch):
    collection = MagicMock()
    collection.name = "supportiq_knowledge"
    collection.count.return_value = 6

    monkeypatch.setattr(main, "get_collection", lambda: collection)

    response = client.get("/api/knowledge/stats")

    assert response.status_code == 200
    assert response.json()["total_chunks"] == 6
    assert response.json()["collection"] == "supportiq_knowledge"


def test_ask_endpoint_returns_grounded_answer(monkeypatch):
    expected = {
        "answer": "Returns are accepted within 7 calendar days.",
        "sources": [
            {"document": "return_refund_policy.md", "similarity": 0.85}
        ],
        "confidence": 0.85,
        "grounded": True
    }

    monkeypatch.setattr(
        main, "generate_answer", lambda question, top_k=3: expected
    )

    response = client.post(
        "/api/ask",
        json={"question": "What is the return policy?"}
    )

    assert response.status_code == 200
    assert response.json()["grounded"] is True
    assert response.json()["answer"] == expected["answer"]


def test_ask_endpoint_returns_unknown_question_fallback(monkeypatch):
    expected = {
        "answer": "I could not find sufficiently relevant information.",
        "sources": [],
        "confidence": 0.0,
        "grounded": False
    }

    monkeypatch.setattr(
        main, "generate_answer", lambda question, top_k=3: expected
    )

    response = client.post(
        "/api/ask",
        json={"question": "Tell me about space travel to Mars"}
    )

    assert response.status_code == 200
    assert response.json()["grounded"] is False
    assert response.json()["sources"] == []


def test_ask_endpoint_rejects_empty_question():
    response = client.post(
        "/api/ask",
        json={"question": ""}
    )

    assert response.status_code == 422


def test_ask_endpoint_rejects_question_over_limit():
    response = client.post(
        "/api/ask",
        json={"question": "a" * 2001}
    )

    assert response.status_code == 422


def test_ask_endpoint_rejects_invalid_top_k():
    response = client.post(
        "/api/ask",
        json={"question": "Return policy?", "top_k": 0}
    )

    assert response.status_code == 422


def test_ask_endpoint_rejects_top_k_above_limit():
    response = client.post(
        "/api/ask",
        json={"question": "Return policy?", "top_k": 11}
    )

    assert response.status_code == 422


def test_ask_endpoint_handles_generator_value_error(monkeypatch):
    def raise_value_error(question, top_k=3):
        raise ValueError("Invalid question")

    monkeypatch.setattr(main, "generate_answer", raise_value_error)

    response = client.post(
        "/api/ask",
        json={"question": "A valid question"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid question"


def test_ask_endpoint_hides_unexpected_internal_errors(monkeypatch):
    def raise_runtime_error(question, top_k=3):
        raise RuntimeError("Internal test error")

    monkeypatch.setattr(main, "generate_answer", raise_runtime_error)

    response = client.post(
        "/api/ask",
        json={"question": "A valid question"}
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "An internal error occurred while processing the question."
    )
