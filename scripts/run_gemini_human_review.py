"""Fresh Gemini evaluation on human-reviewed development inputs only."""
from __future__ import annotations

import base64, json, subprocess, time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from hypereel.config import get_settings
from hypereel.providers.gemini_video import BudgetClient

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evals/iterations/gemini-human-review-034"
MEDIA = ROOT / "evals/iterations/gemini-development-media"
REVISED = OUT / "media"
ALLOWED = {"two_point_made", "two_point_miss", "three_point_made", "three_point_miss",
           "made_field_goal", "missed_field_goal", "free_throw_made", "free_throw_miss",
           "offensive_rebound", "defensive_rebound", "steal", "turnover", "block", "assist"}
CASES = [
    dict(index=1, game="east-bay-elite-vs-spartans", clip=MEDIA/"w1-continuous.mp4", source_start=221, core=(221,231), input="unchanged"),
    dict(index=2, game="east-bay-elite-vs-spartans", source=ROOT/"downloads/KBETdDRM70Q.studio-720p.mp4", clip=REVISED/"w2-action-complete.mp4", source_start=754, source_end=769, core=(756,767), input="revised_action_complete"),
    dict(index=3, game="unlimited-vs-campus", clip=MEDIA/"w3-continuous.mp4", source_start=18, core=(20,28), input="unchanged"),
    dict(index=4, game="unlimited-vs-campus", clip=MEDIA/"w4-continuous.mp4", source_start=92, core=(94,102), input="unchanged"),
    dict(index=5, game="unlimited-vs-campus", clip=MEDIA/"w5-continuous.mp4", source_start=974, core=(976,984), input="unchanged"),
    dict(index=6, game="unlimited-vs-campus", source=ROOT/"downloads/rHSdABRoBeE.studio-720p.mp4", clip=REVISED/"w6-action-complete.mp4", source_start=1314, source_end=1327, core=(1316,1325), input="revised_action_complete"),
    dict(index=7, game="unlimited-vs-campus", clip=MEDIA/"w7-continuous.mp4", source_start=2376, core=(2378,2386), input="unchanged"),
]

def now(): return datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()
def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp=path.with_suffix(path.suffix+".tmp"); tmp.write_text(json.dumps(data,indent=2)); tmp.replace(path)

def prepare(case):
    if case["input"] == "revised_action_complete":
        case["clip"].parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg","-v","error","-nostdin","-y","-ss",str(case["source_start"]),
                        "-i",str(case["source"]),"-t",str(case["source_end"]-case["source_start"]),
                        "-an","-c:v","libx264","-preset","fast","-crf","20",str(case["clip"])],
                       check=True,timeout=120)
    if not case["clip"].is_file() or case["clip"].stat().st_size >= 19_000_000:
        raise ValueError(f"Invalid inline clip W{case['index']}")

def prompt(case):
    a,b=case["core"]
    return f"""Analyze every supported basketball event in this continuous video. Clip 00:00 is source time {case['source_start']} seconds; return SOURCE time_seconds. Score only events whose decisive action occurs in [{a},{b}], using surrounding footage as context.
Allowed labels: {', '.join(sorted(ALLOWED))}.
made_field_goal and missed_field_goal mean the outcome is visible but two-versus-three point value is not visually established. Prefer those generic labels rather than guessing shot value. A block also implies a missed field-goal attempt. A defensive rebound after an opponent miss is not a turnover. Preserve multiple compatible events. Do not infer shot value from trajectory or a scoreboard. Do not invent hidden events. Return only JSON {{"events":[{{"label":"label","time_seconds":0.0,"confidence":0.8,"evidence":"visible evidence"}}]}}; empty events is allowed."""

def parse(text, case):
    obj=json.loads(text); events=obj.get("events")
    if set(obj)!={"events"} or not isinstance(events,list) or len(events)>16: raise ValueError("invalid events payload")
    result=[]
    for event in events:
        if event.get("label") not in ALLOWED or not isinstance(event.get("time_seconds"),(int,float)): raise ValueError("invalid event")
        if not case["source_start"] <= event["time_seconds"] <= case.get("source_end",case["source_start"]+12): raise ValueError("event outside clip")
        result.append(dict(event,game_id=case["game"]))
    return result

def main():
    if (OUT/"report.json").exists(): raise FileExistsError("refusing to overwrite run")
    settings=get_settings(); settings.gemini_model="gemini-3.8-flash"; assert settings.gemini_api_key
    for case in CASES: prepare(case)
    client=BudgetClient(settings); before=client.read_spend(); started=time.monotonic()
    report={"name":"gemini-human-review-034","status":"running","started_at":now(),"model":"gemini-3.8-flash",
            "config":{"temperature":0,"maxOutputTokens":2048,"thinkingLevel":"LOW","mediaResolution":"HIGH","fps":4},
            "annotation_revision":"evals/golden/revisions/development-human-review-v1.json",
            "spend_before_usd":before,"holdout_used":False,"calls":[]}
    save(OUT/"report.json",report)
    try:
        for case in CASES:
            data=case["clip"].read_bytes(); p=prompt(case)
            row={k:(str(v.relative_to(ROOT)) if k=="clip" else v) for k,v in case.items() if k!="source"}
            row.update(status="started",started_at=now(),prompt=p); report["calls"].append(row); save(OUT/"report.json",report)
            raw=client.generate([{"inlineData":{"mimeType":"video/mp4","data":base64.b64encode(data).decode()},"videoMetadata":{"fps":4}},{"text":p}],json_output=True,max_tokens=2048,metadata={"iteration":"034","window_id":f"W{case['index']}","input":case["input"]})
            row.update(status="completed",ended_at=now(),raw_text=raw,events=parse(raw,case)); save(OUT/"report.json",report)
            print(f"W{case['index']} {row['events']}",flush=True)
        report["status"]="completed"
    except Exception as error:
        report.update(status="stopped",error_type=type(error).__name__,error=str(error)); raise
    finally:
        report.update(ended_at=now(),elapsed_seconds=time.monotonic()-started,spend_after_usd=client.read_spend())
        report["incremental_estimated_spend_usd"]=report["spend_after_usd"]-before
        save(OUT/"report.json",report)

if __name__ == "__main__": main()
