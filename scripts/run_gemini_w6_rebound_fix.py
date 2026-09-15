"""Targeted paid development evaluation of the possession-sequence prompt fix."""
from __future__ import annotations

import base64
import json
import os
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from hypereel.config import get_settings
from hypereel.evaluation.possession_sequence import rebound_sequence_guidance, validate_rebound_fields
from hypereel.providers.gemini_video import BudgetClient


ROOT = Path(__file__).resolve().parents[1]
CLIP = ROOT / "evals/iterations/gemini-human-review-034/media/w6-action-complete.mp4"
ITERATION = os.environ.get("HYPEREEL_EVAL_ITERATION", "035")
OUT = ROOT / f"evals/iterations/gemini-w6-rebound-fix-{ITERATION}"
ALLOWED = {"two_point_miss", "missed_field_goal", "offensive_rebound", "defensive_rebound", "turnover", "steal"}


def now() -> str:
    return datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()


def prompt() -> str:
    return (
        "Analyze the continuous basketball play in source interval [1316,1325]. Clip 00:00 is source "
        "1314 seconds. Team identity supplied by the reviewed game setup: Campus wears yellow and "
        "Unlimited wears white. This identity mapping is context, not an event label.\n"
        + rebound_sequence_guidance()
        + "Return every supported event in chronological order. Allowed labels: "
        + ", ".join(sorted(ALLOWED))
        + ". For shots, team is the shooting team and shooting_team is the same value. For rebounds, "
        "team is the team obtaining clear control and shooting_team is the team that took the immediately "
        "preceding missed shot. Use unknown for an unsupported identity. Return strict JSON only: "
        '{"events":[{"sequence_index":1,"label":"label","time_seconds":0.0,"team":"Campus|Unlimited|unknown",'
        '"shooting_team":"Campus|Unlimited|unknown","confidence":0.8,"evidence":"visible ordered evidence"}]}. '
        "Do not use the scoreboard and do not invent events hidden between frames."
    )


def parse(raw: str) -> list[dict]:
    obj = json.loads(raw)
    if set(obj) != {"events"} or not isinstance(obj["events"], list):
        raise ValueError("invalid payload")
    events = obj["events"]
    last_index = 0
    for event in events:
        required = {"sequence_index", "label", "time_seconds", "team", "shooting_team", "confidence", "evidence"}
        if set(event) != required or event["label"] not in ALLOWED:
            raise ValueError("invalid event fields")
        if event["sequence_index"] <= last_index:
            raise ValueError("invalid event order")
        reported_time = event["time_seconds"]
        if 0 <= reported_time <= 13:
            event["reported_time_seconds"] = reported_time
            event["time_seconds"] = 1314 + reported_time
            event["time_basis"] = "clip_relative_normalized_to_source"
        elif 1314 <= reported_time <= 1327:
            event["time_basis"] = "source"
        else:
            raise ValueError("invalid event time")
        if event["team"] not in {"Campus", "Unlimited", "unknown"} or event["shooting_team"] not in {"Campus", "Unlimited", "unknown"}:
            raise ValueError("invalid team")
        valid, reason = validate_rebound_fields(event)
        event["internal_consistency"] = {"valid": valid, "reason": reason}
        last_index = event["sequence_index"]
    # A generic missed_field_goal and an exact miss at the same instant are one
    # shot, not two events. Prefer the supported exact subtype.
    exact_misses = [event for event in events if event["label"] == "two_point_miss"]
    events = [event for event in events if not (
        event["label"] == "missed_field_goal"
        and any(exact["team"] == event["team"]
                and abs(exact["time_seconds"] - event["time_seconds"]) <= 1.0
                for exact in exact_misses)
    )]
    return events


def evaluate(events: list[dict]) -> dict:
    defensive = [event for event in events if event["label"] == "defensive_rebound"]
    matches = [event for event in defensive
               if event["team"] == "Unlimited"
               and event["shooting_team"] == "Campus"
               and 1323 <= event["time_seconds"] <= 1325
               and event["internal_consistency"]["valid"]]
    recovered_labels = {event["label"] for event in events}
    return {
        "defensive_rebound": {
            "tp": 1 if matches else 0,
            "fp": len(defensive) - (1 if matches else 0),
            "fn": 0 if matches else 1,
            "supported": bool(matches),
        },
        "sequence_coverage": {
            "campus_offensive_rebound_recovered": "offensive_rebound" in recovered_labels,
            "second_campus_miss_recovered": any(
                event["label"] in {"two_point_miss", "missed_field_goal"}
                and event["team"] == "Campus" and event["time_seconds"] >= 1322
                for event in events
            ),
            "unsupported_turnover_emitted": "turnover" in recovered_labels,
        },
    }


def main() -> None:
    report_path = OUT / "report.json"
    if report_path.exists():
        raise FileExistsError("refusing to overwrite run")
    if not CLIP.is_file():
        raise FileNotFoundError(CLIP)
    OUT.mkdir(parents=True)
    settings = get_settings()
    settings.gemini_model = "gemini-3.8-flash"
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY unavailable")
    client = BudgetClient(settings)
    before = client.read_spend()
    request_prompt = prompt()
    started = time.monotonic()
    report = {"name": OUT.name, "status": "running", "started_at": now(), "model": settings.gemini_model,
              "scope": "reviewed development W6 only", "holdout_used": False, "spend_before_usd": before,
              "prompt": request_prompt}
    report_path.write_text(json.dumps(report, indent=2))
    try:
        raw = client.generate([
            {"inlineData": {"mimeType": "video/mp4", "data": base64.b64encode(CLIP.read_bytes()).decode()},
             "videoMetadata": {"fps": 6}},
            {"text": request_prompt},
        ], json_output=True, max_tokens=2048,
           metadata={"iteration": ITERATION, "window_id": "W6", "kind": "possession_sequence_fix", "fps": 6})
        events = parse(raw)
        report.update(status="completed", raw_text=raw, events=events, evaluation=evaluate(events))
    except Exception as error:
        report.update(status="stopped", error_type=type(error).__name__, error=str(error))
        raise
    finally:
        report.update(ended_at=now(), elapsed_seconds=time.monotonic() - started,
                      spend_after_usd=client.read_spend())
        report["incremental_estimated_spend_usd"] = report["spend_after_usd"] - before
        report_path.write_text(json.dumps(report, indent=2))
    print(json.dumps(report["events"], indent=2))


if __name__ == "__main__":
    main()
