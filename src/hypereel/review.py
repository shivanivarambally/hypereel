"""Simple, deterministic human-review actions for potential events."""
from __future__ import annotations

from .models import PotentialEvent


def apply_review_action(
    item: PotentialEvent,
    action: str,
    *,
    corrected_label: str | None = None,
) -> PotentialEvent:
    """Return an updated queue item; callers persist state through the graph/UI."""
    if action not in {"confirm", "correct", "reject"}:
        raise ValueError("action must be confirm, correct, or reject")
    if action == "correct" and not corrected_label:
        raise ValueError("corrected_label is required for correct")
    update = {"review_status": {"confirm": "confirmed", "correct": "corrected", "reject": "rejected"}[action]}
    if corrected_label:
        update["proposed_label"] = corrected_label
    return item.model_copy(update=update)
