"""Offline audit of cached Gemini predictions against human-adjudicated references.

This deliberately reports a point-comparable slice separately from taxonomy and
boundary coverage gaps. It never rewrites historical reports or reads holdout data.
"""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVISION = ROOT / "evals/golden/revisions/development-human-review-v1.json"
CACHED = ROOT / "evals/iterations/gemini-development-summary/full-control.json"

# Only facts with a retained point anchor, a human-supported label, and unchanged
# model input/scored core belong in the strict comparable slice.
COMPARABLE = {
    1: {"free_throw_made": [225.0]},
    2: {"steal": [758.0]},
    3: {},
    4: {"free_throw_miss": [96.0]},
    5: {"block": [978.0]},
    6: {"two_point_miss": [1320.0]},
}

# Predictions with these labels are adjudicated contradictions and count as FP.
# Other predictions are ignored because the human review did not resolve them or
# because their corresponding corrected reference lacks comparable time/input.
ADJUDICATED_PREDICTION_LABELS = {
    1: {"free_throw_made", "free_throw_miss"},
    2: {"steal"},
    3: set(),
    4: {"free_throw_made", "free_throw_miss"},
    5: {"block"},
    6: {"two_point_miss", "steal", "turnover"},
}


def score_slice(calls: list[dict], tolerance: float = 5.0) -> dict:
    tp = fp = fn = 0
    rows = []
    for call in calls:
        index = call["index"]
        if index not in COMPARABLE:
            continue
        references = COMPARABLE[index]
        predictions = [event for event in call["events"]
                       if event["label"] in ADJUDICATED_PREDICTION_LABELS[index]]
        matched_predictions: set[int] = set()
        matched_refs: set[tuple[str, int]] = set()
        for label, times in references.items():
            for ref_i, time_seconds in enumerate(times):
                choices = [(abs(event["time_seconds"] - time_seconds), pred_i)
                           for pred_i, event in enumerate(predictions)
                           if pred_i not in matched_predictions
                           and event["label"] == label
                           and abs(event["time_seconds"] - time_seconds) <= tolerance]
                if choices:
                    _, pred_i = min(choices)
                    matched_predictions.add(pred_i)
                    matched_refs.add((label, ref_i))
        case_tp = len(matched_refs)
        case_fp = len(predictions) - len(matched_predictions)
        case_fn = sum(len(times) for times in references.values()) - case_tp
        tp += case_tp; fp += case_fp; fn += case_fn
        rows.append({"window_id": f"W{index}", "tp": case_tp, "fp": case_fp,
                     "fn": case_fn, "scored_prediction_labels":
                     [event["label"] for event in predictions]})
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1 = 2 * tp / (2 * tp + fp + fn) if tp + fp + fn else None
    return {"tp": tp, "fp": fp, "fn": fn, "precision": precision,
            "recall": recall, "micro_f1": f1, "windows": rows}


def main() -> None:
    revision = json.loads(REVISION.read_text())
    cached = json.loads(CACHED.read_text())
    result = {
        "revision": revision["version"],
        "cached_model": cached["calls"][0]["raw_response"]["modelVersion"],
        "historical_full_original": {
            key: cached["metrics"]["gemini_video"][key]
            for key in ("tp", "fp", "fn", "micro_precision", "micro_recall", "micro_f1")
        },
        "adjudicated_point_comparable_slice": score_slice(cached["calls"]),
        "coverage_gaps": {
            "input_changed_or_incomplete": ["W2 made basket", "W6 defensive rebound"],
            "generic_unknown_point_value": ["W5 missed_field_goal", "W7 made_field_goal"],
            "unresolved_exact_timing": ["W6 second two_point_miss", "W6 offensive_rebound"],
            "unresolved_original_labels": ["W2 assist", "W2 turnover"],
            "excluded_unreviewed": ["W0"],
        },
        "interpretation": (
            "The comparable-slice score is an annotation/evaluator audit, not a model gain. "
            "It is not directly comparable with the full 8-window/14-reference headline."
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
