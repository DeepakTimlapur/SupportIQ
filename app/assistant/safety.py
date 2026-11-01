MINIMUM_SIMILARITY = 0.40

FALLBACK_MESSAGE = (
    "I could not find sufficiently relevant information in the "
    "available knowledge base. Please contact customer support "
    "for further assistance."
)


def is_relevant(results, threshold=MINIMUM_SIMILARITY):
    if not results:
        return False

    return results[0].get("similarity", 0.0) >= threshold


def validate_question(question: str):
    if not isinstance(question, str):
        raise ValueError("Question must be a string")

    if not question.strip():
        raise ValueError("Question cannot be empty")

    if len(question) > 2000:
        raise ValueError("Question exceeds the 2000-character limit")
