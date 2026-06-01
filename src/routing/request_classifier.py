"""Request classification."""


def classify_request(payload: dict) -> dict:
    """Classify a request using provided metadata."""
    return {
        "task_type": payload.get("task_type", "summarization"),
        "domain": payload.get("domain", "general_business"),
        "risk_level": payload.get("risk_level", "low"),
    }
