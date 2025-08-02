import math


def estimate_tokens(text: str) -> int:
    """Estimate token count using a simple 4-characters-per-token heuristic."""
    if not text:
        return 0
    return math.ceil(len(text) / 4)
