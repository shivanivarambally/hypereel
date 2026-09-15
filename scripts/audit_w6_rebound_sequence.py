"""Evidence-aware audit for the reviewed W6 rebound sequence.

This intentionally handles one bounded, manually reviewed development case. It
does not guess team identity from uniform color: the aliases below come directly
from the versioned human-review record (Campus/yellow, Unlimited/white).
"""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "evals/iterations/gemini-human-review-034/report.json"

TEAM_ALIASES = {"yellow": "Campus", "white": "Unlimited"}


def evidence_team(evidence: str) -> str | None:
    text = evidence.lower()
    found = {team for alias, team in TEAM_ALIASES.items() if alias in text}
    return next(iter(found)) if len(found) == 1 else None


def audit(events: list[dict]) -> dict:
    rebound_predictions = [event for event in events
                           if event["label"] in {"offensive_rebound", "defensive_rebound"}]
    defensive = next((event for event in rebound_predictions
                      if event["label"] == "defensive_rebound"), None)
    naive_time_match = bool(defensive and 1323 - 5 <= defensive["time_seconds"] <= 1325 + 5)
    predicted_team = evidence_team(defensive["evidence"]) if defensive else None
    evidence_aware_match = bool(naive_time_match and predicted_team == "Unlimited")

    labeled_sequence = [
        {"label": "two_point_miss", "team": "Campus", "time": "about 1320"},
        {"label": "offensive_rebound", "team": "Campus", "time": "about 1322"},
        {"label": "two_point_miss", "team": "Campus", "time": "unresolved"},
        {"label": "defensive_rebound", "team": "Unlimited", "time": "1323-1325"},
    ]
    predicted_sequence = [{
        "label": event["label"],
        "team_from_evidence": evidence_team(event["evidence"]),
        "time_seconds": event["time_seconds"],
        "evidence": event["evidence"],
    } for event in events]

    return {
        "scope": "W6 reviewed development sequence only",
        "team_alias_provenance": "development-human-review-v1.json",
        "labeled_sequence": labeled_sequence,
        "predicted_sequence": predicted_sequence,
        "defensive_rebound": {
            "naive_label_time_match": naive_time_match,
            "evidence_aware_match": evidence_aware_match,
            "expected_team": "Unlimited",
            "predicted_team_from_evidence": predicted_team,
            "expected_time": [1323, 1325],
            "predicted_time": defensive["time_seconds"] if defensive else None,
            "verdict": "unsupported" if not evidence_aware_match else "supported",
            "reason": (
                "Gemini assigns the defensive rebound to yellow/Campus, but the reviewed "
                "sequence assigns the final defensive rebound to Unlimited after Campus's "
                "offensive rebound and second miss."
            ),
        },
        "sequence_consistency": {
            "supported": False,
            "reason": (
                "The predicted narrative reverses the first shooter/team, treats Campus's "
                "possession-retaining rebound as defensive, and places a Campus offensive "
                "rebound after its next miss rather than before that miss."
            ),
        },
        "scoring_effect": {
            "naive": {"tp": 1, "fp": 0, "fn": 0},
            "evidence_aware": {"tp": 0, "fp": 1, "fn": 1},
            "note": "Counts shown are for the defensive-rebound fact only."
        },
        "unresolved": [
            "Exact point time for Campus's second missed two-pointer",
            "Exact point time for Campus's offensive rebound",
        ],
    }


def main() -> None:
    report = json.loads(RUN.read_text())
    call = next(call for call in report["calls"] if call["index"] == 6)
    print(json.dumps(audit(call["events"]), indent=2))


if __name__ == "__main__":
    main()
