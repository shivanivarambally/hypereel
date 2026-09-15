from hypereel.evaluation.possession_sequence import rebound_sequence_guidance, validate_rebound_fields
import importlib.util
from pathlib import Path


RUNNER_PATH = Path(__file__).resolve().parents[1] / "scripts/run_gemini_w6_rebound_fix.py"
SPEC = importlib.util.spec_from_file_location("run_gemini_w6_rebound_fix", RUNNER_PATH)
assert SPEC and SPEC.loader
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


def test_rebound_class_requires_shooter_controller_relationship():
    good = {"label": "defensive_rebound", "team": "Unlimited", "shooting_team": "Campus"}
    bad = {"label": "defensive_rebound", "team": "Campus", "shooting_team": "Campus"}
    assert validate_rebound_fields(good)[0] is True
    assert validate_rebound_fields(bad)[0] is False


def test_shared_prompt_preserves_putback_sequence():
    text = rebound_sequence_guidance()
    assert "offensive rebound" in text
    assert "putback shot" in text
    assert "not, by itself, a turnover" in text


def test_clip_relative_time_is_normalized_and_rebound_scored_with_team():
    raw = '{"events":[{"sequence_index":1,"label":"defensive_rebound","time_seconds":10.167,"team":"Unlimited","shooting_team":"Campus","confidence":0.8,"evidence":"Unlimited controls after Campus miss"}]}'
    events = RUNNER.parse(raw)
    assert events[0]["time_seconds"] == 1324.167
    assert events[0]["time_basis"] == "clip_relative_normalized_to_source"
    assert RUNNER.evaluate(events)["defensive_rebound"] == {"tp": 1, "fp": 0, "fn": 0, "supported": True}


def test_generic_and_exact_miss_for_same_action_are_deduplicated():
    raw = '{"events":[' \
          '{"sequence_index":1,"label":"two_point_miss","time_seconds":8.5,"team":"Campus","shooting_team":"Campus","confidence":0.8,"evidence":"miss"},' \
          '{"sequence_index":2,"label":"missed_field_goal","time_seconds":8.67,"team":"Campus","shooting_team":"Campus","confidence":0.8,"evidence":"same miss"}' \
          ']}'
    assert [event["label"] for event in RUNNER.parse(raw)] == ["two_point_miss"]
