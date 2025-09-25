"""Utility helpers for test suites."""

import json
from typing import Any

from llm import complete_text


def _serialize_for_prompt(value: Any) -> str:
    """Convert arbitrary input into a stable text snippet for prompting."""
    if isinstance(value, str):
        return value.strip()

    try:
        return json.dumps(value, ensure_ascii=True, sort_keys=True)
    except (TypeError, ValueError):
        return str(value)


async def verify_textual_match(reference: Any, candidate: Any) -> bool:
    """Return True when reference and candidate share the same meaning."""
    reference_text = _serialize_for_prompt(reference)
    candidate_text = _serialize_for_prompt(candidate)

    prompt = (
        "You are a precise semantic comparison assistant.\n"
        "Determine if the reference text and the candidate text express the same "
        "UI regression outcome.\n"
        "Respond with exactly 'true' if they match semantically, otherwise respond "
        "with exactly 'false'.\n"
        f"Reference: {reference_text}\n"
        f"Candidate: {candidate_text}\n"
        "Answer:"
    )

    response = await complete_text(prompt)
    normalized = str(response).strip().lower()

    if normalized.startswith("true"):
        return True
    if normalized.startswith("false"):
        return False
    return False
