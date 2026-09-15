"""Deterministic accounting for the reviewed broader 034-vs-current comparison.

The decisions below are evidence adjudications, not nearest-timestamp guesses.
They prevent the known later W6 miss from being credited as the earlier miss and
prevent a wrong-team rebound from receiving label/time credit.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evals/iterations/gemini-broader-fix-eval-037/evaluation.json"

# Eight scorable reviewed facts. W3 is a confirmed negative; W7 has no audited
# point time and remains qualitative. W2 unresolved turnover/assist are excluded.
REFERENCES = {
    "W1-make": "free_throw_made",
    "W2-steal": "steal",
    "W2-make": "two_point_made",
    "W4-miss": "free_throw_miss",
    "W5-miss-parent": "missed_field_goal",
    "W5-block": "block",
    "W6-first-miss": "two_point_miss",
    "W6-def-rebound": "defensive_rebound",
}

RUNS = {
    "baseline_034": {
        "matched": ["W2-steal", "W2-make", "W4-miss", "W5-miss-parent", "W6-first-miss"],
        "false_positive_labels": ["free_throw_miss", "turnover", "defensive_rebound"],
        "notes": "W6 wrong-team defensive rebound is FP; its reviewed rebound is also FN.",
    },
    "current_037_plus_036": {
        "matched": ["W2-steal", "W2-make", "W5-miss-parent", "W6-def-rebound"],
        "false_positive_labels": ["free_throw_miss", "free_throw_made"],
        "notes": "W6 later miss is supported but not point-scored as the earlier miss; exact second-miss time is unknown.",
    },
}


def metrics(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else None
    r = tp / (tp + fn) if tp + fn else None
    f1 = 2 * tp / (2 * tp + fp + fn) if tp + fp + fn else None
    return {"tp": tp, "fp": fp, "fn": fn, "precision": p, "recall": r, "f1": f1}


def score(run):
    matched = set(run["matched"])
    overall = metrics(len(matched), len(run["false_positive_labels"]), len(REFERENCES) - len(matched))
    labels = sorted(set(REFERENCES.values()) | set(run["false_positive_labels"]))
    per_class = {}
    for label in labels:
        refs = [ref for ref, ref_label in REFERENCES.items() if ref_label == label]
        tp = sum(ref in matched for ref in refs)
        fp = run["false_positive_labels"].count(label)
        per_class[label] = {"references": len(refs), **metrics(tp, fp, len(refs)-tp)}
    return {"overall": overall, "per_class": per_class, "adjudication_note": run["notes"]}


def main():
    baseline = score(RUNS["baseline_034"])
    current = score(RUNS["current_037_plus_036"])
    report = {
        "scope": "reviewed development W1-W6; W3 confirmed negative; W7 qualitative only; W0 excluded",
        "holdout_used": False,
        "positive_references": len(REFERENCES),
        "baseline_034": baseline,
        "current_037_plus_036": current,
        "delta": {
            key: current["overall"][key] - baseline["overall"][key]
            for key in ("precision", "recall", "f1")
        },
        "confirmed_negative": {"window": "W3", "baseline_events": 0, "current_events": 0},
        "excluded": {
            "W0": "not adjudicated in-window",
            "W2": ["turnover and assist unresolved"],
            "W6": ["offensive rebound and second miss lack audited point times"],
            "W7": ["made_field_goal label supported; exact point time unverified"],
        },
        "lighting_context": {
            "metric": "mean decoded luma (YAVG), one sample per second; descriptive only",
            "W1": 122.57, "W2": 114.46, "W3": 123.58, "W4": 124.45,
            "W5": 129.43, "W6": 128.90, "W7": 127.90,
            "interpretation": "No causal lighting conclusion: darkest W2 was correct, while normally lit W4 regressed."
        },
    }
    OUT.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__": main()
