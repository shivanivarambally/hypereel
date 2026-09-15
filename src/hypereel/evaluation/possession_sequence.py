"""Shared temporal guidance and validation for basketball possession sequences."""
from __future__ import annotations


def rebound_sequence_guidance() -> str:
    return (
        "\nBasketball possession-sequence procedure:\n"
        "1. Follow the same live ball chronologically; do not classify isolated frames.\n"
        "2. For every shot, record the shooting team, visible outcome, and next team with clear control.\n"
        "3. After a confirmed miss, compare the next controlling team with the shooting team: "
        "same team means offensive_rebound; opponent means defensive_rebound.\n"
        "4. If the shooting team gets an offensive rebound, keep the possession open and separately "
        "analyze any putback shot and its later rebound. Do not attach the later rebound to the first shot.\n"
        "5. A possession change following a missed shot and rebound is not, by itself, a turnover or steal.\n"
        "6. Never decide rebound type from jersey color alone. First identify which team took the relevant shot.\n"
        "In the reason/evidence, explicitly name the shooting team and rebound-controlling team. "
        "Use unknown rather than guessing when either team or the event order is unclear.\n"
    )


def validate_rebound_fields(event: dict) -> tuple[bool, str]:
    """Validate a structured rebound against its own shooter/controller claims."""
    if event.get("label") not in {"offensive_rebound", "defensive_rebound"}:
        return True, "not a rebound"
    rebound_team = event.get("team")
    shooting_team = event.get("shooting_team")
    if not rebound_team or rebound_team == "unknown" or not shooting_team or shooting_team == "unknown":
        return False, "rebound requires known shooting_team and controlling team"
    same = rebound_team == shooting_team
    if event["label"] == "offensive_rebound" and not same:
        return False, "offensive rebound controller must equal shooting team"
    if event["label"] == "defensive_rebound" and same:
        return False, "defensive rebound controller must differ from shooting team"
    return True, "internally consistent"
