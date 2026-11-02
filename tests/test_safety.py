import pytest

from app.assistant.safety import (
    MINIMUM_SIMILARITY,
    FALLBACK_MESSAGE,
    is_relevant,
    validate_question,
)


def test_minimum_similarity_threshold():
    assert MINIMUM_SIMILARITY == 0.40


def test_relevant_result_is_accepted():
    results = [{"similarity": 0.85}]
    assert is_relevant(results) is True


def test_irrelevant_result_is_rejected():
    results = [{"similarity": 0.20}]
    assert is_relevant(results) is False


def test_empty_results_are_rejected():
    assert is_relevant([]) is False


def test_custom_similarity_threshold():
    results = [{"similarity": 0.65}]
    assert is_relevant(results, threshold=0.60) is True


def test_valid_question_is_accepted():
    validate_question("What is the return policy?")


def test_empty_question_is_rejected():
    with pytest.raises(ValueError):
        validate_question("")


def test_whitespace_question_is_rejected():
    with pytest.raises(ValueError):
        validate_question("   ")


def test_non_string_question_is_rejected():
    with pytest.raises(ValueError):
        validate_question(123)


def test_question_over_2000_characters_is_rejected():
    with pytest.raises(ValueError):
        validate_question("a" * 2001)


def test_fallback_message_exists():
    assert "contact customer support" in FALLBACK_MESSAGE.lower()
