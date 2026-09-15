"""Fresh current-prompt evaluation on reviewed development windows other than W6."""
from __future__ import annotations

import base64
import json
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from hypereel.config import get_settings
from hypereel.evaluation.possession_sequence import rebound_sequence_guidance, validate_rebound_fields
from hypereel.providers.gemini_video import BudgetClient


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evals/iterations/gemini-broader-fix-eval-037"
MEDIA = ROOT / "evals/iterations/gemini-development-media"
REVISED = ROOT / "evals/iterations/gemini-human-review-034/media"
ALLOWED = {"two_point_made", "two_point_miss", "three_point_made", "three_point_miss",
           "made_field_goal", "missed_field_goal", "free_throw_made", "free_throw_miss",
           "offensive_rebound", "defensive_rebound", "steal", "turnover", "block", "assist"}
CASES = [
    dict(index=1, game="east-bay-elite-vs-spartans", clip=MEDIA/"w1-continuous.mp4", start=221, end=233, core=(223,231), teams="East Bay Elite wears blue; Spartans wears black"),
    dict(index=2, game="east-bay-elite-vs-spartans", clip=REVISED/"w2-action-complete.mp4", start=754, end=769, core=(756,767), teams="East Bay Elite wears blue; Spartans wears black", input="revised_action_complete"),
    dict(index=3, game="unlimited-vs-campus", clip=MEDIA/"w3-continuous.mp4", start=18, end=30, core=(20,28), teams="Campus wears yellow; Unlimited wears white"),
    dict(index=4, game="unlimited-vs-campus", clip=MEDIA/"w4-continuous.mp4", start=92, end=104, core=(94,102), teams="Campus wears yellow; Unlimited wears white"),
    dict(index=5, game="unlimited-vs-campus", clip=MEDIA/"w5-continuous.mp4", start=974, end=986, core=(976,984), teams="Campus wears yellow; Unlimited wears white"),
    dict(index=7, game="unlimited-vs-campus", clip=MEDIA/"w7-continuous.mp4", start=2376, end=2388, core=(2378,2386), teams="Campus wears yellow; Unlimited wears white"),
]


def now():
    return datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(data, indent=2))
    temp.replace(path)


def build_prompt(case):
    a, b = case["core"]
    return (
        f"Analyze all supported basketball events in source interval [{a},{b}]. Clip 00:00 is source "
        f"{case['start']} seconds. Reviewed game setup supplies team identity only: {case['teams']}. "
        "Do not treat that mapping as evidence that an event occurred.\n"
        + rebound_sequence_guidance()
        + "Return supported events chronologically. Allowed labels: " + ", ".join(sorted(ALLOWED)) + ". "
        "Use made_field_goal or missed_field_goal when the outcome is visible but two-versus-three point value is not. "
        "A block also implies a missed field-goal attempt. For shots, team and shooting_team are the shooting team. "
        "For rebounds, team is the controller and shooting_team is the immediately preceding missed-shot team. "
        "Use unknown rather than guess. Return strict JSON only: "
        '{"events":[{"sequence_index":1,"label":"label","time_seconds":0.0,"team":"team name|unknown",'
        '"shooting_team":"team name|unknown","confidence":0.8,"evidence":"visible ordered evidence"}]}. '
        "Return an empty list for no event. Do not infer from scoreboard, trajectory, or hidden action."
    )


def parse(raw, case):
    obj = json.loads(raw)
    if set(obj) != {"events"} or not isinstance(obj["events"], list):
        raise ValueError("invalid payload")
    result = []
    last = 0
    duration = case["end"] - case["start"]
    for event in obj["events"]:
        required = {"sequence_index", "label", "time_seconds", "team", "shooting_team", "confidence", "evidence"}
        if set(event) != required or event["label"] not in ALLOWED or event["sequence_index"] <= last:
            raise ValueError("invalid event")
        reported = event["time_seconds"]
        if 0 <= reported <= duration:
            event["reported_time_seconds"] = reported
            event["time_seconds"] = case["start"] + reported
            event["time_basis"] = "clip_relative_normalized_to_source"
        elif case["start"] <= reported <= case["end"]:
            event["time_basis"] = "source"
        else:
            raise ValueError("time outside clip")
        valid, reason = validate_rebound_fields(event)
        event["internal_consistency"] = {"valid": valid, "reason": reason}
        result.append(event)
        last = event["sequence_index"]
    exact = {"two_point_made": "made_field_goal", "three_point_made": "made_field_goal",
             "two_point_miss": "missed_field_goal", "three_point_miss": "missed_field_goal"}
    return [event for event in result if not any(
        exact.get(other["label"]) == event["label"] and other["team"] == event["team"]
        and abs(other["time_seconds"] - event["time_seconds"]) <= 1
        for other in result
    )]


def main():
    report_path = OUT / "report.json"
    if report_path.exists():
        raise FileExistsError("refusing to overwrite run")
    settings = get_settings(); settings.gemini_model = "gemini-3.8-flash"
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY unavailable")
    client = BudgetClient(settings); before = client.read_spend(); started = time.monotonic()
    report = {"name": OUT.name, "status": "running", "started_at": now(), "model": settings.gemini_model,
              "holdout_used": False, "spend_before_usd": before, "calls": []}
    save(report_path, report)
    try:
        for case in CASES:
            if not case["clip"].is_file(): raise FileNotFoundError(case["clip"])
            p = build_prompt(case)
            row = {"index": case["index"], "game": case["game"], "clip": str(case["clip"].relative_to(ROOT)),
                   "source_start": case["start"], "source_end": case["end"], "core": case["core"],
                   "input": case.get("input", "unchanged"), "status": "started", "prompt": p}
            report["calls"].append(row); save(report_path, report)
            raw = client.generate([
                {"inlineData": {"mimeType": "video/mp4", "data": base64.b64encode(case["clip"].read_bytes()).decode()}, "videoMetadata": {"fps": 4}},
                {"text": p},
            ], json_output=True, max_tokens=2048,
               metadata={"iteration": "037", "window_id": f"W{case['index']}", "kind": "broader_possession_fix", "fps": 4})
            row.update(status="completed", raw_text=raw, events=parse(raw, case), ended_at=now())
            save(report_path, report); print(f"W{case['index']} {row['events']}", flush=True)
        report["status"] = "completed"
    except Exception as error:
        report.update(status="stopped", error_type=type(error).__name__, error=str(error)); raise
    finally:
        report.update(ended_at=now(), elapsed_seconds=time.monotonic()-started, spend_after_usd=client.read_spend())
        report["incremental_estimated_spend_usd"] = report["spend_after_usd"] - before
        save(report_path, report)


if __name__ == "__main__": main()
