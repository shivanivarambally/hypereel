"""Reparse one preserved W6 run with the current normalization/evaluator."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from run_gemini_w6_rebound_fix import ROOT, evaluate, parse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("iteration")
    args = parser.parse_args()
    source = ROOT / f"evals/iterations/gemini-w6-rebound-fix-{args.iteration}/report.json"
    report = json.loads(source.read_text())
    if not report.get("raw_text"):
        raise ValueError("run has no preserved raw_text")
    events = parse(report["raw_text"])
    normalized = dict(report, events=events, evaluation=evaluate(events),
                      normalization_note="Reparsed preserved raw output; no provider call.")
    target = source.with_name("normalized-report.json")
    if target.exists():
        raise FileExistsError("refusing to overwrite normalized report")
    target.write_text(json.dumps(normalized, indent=2))
    print(json.dumps({"events": events, "evaluation": normalized["evaluation"]}, indent=2))


if __name__ == "__main__":
    main()
