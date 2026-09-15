import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/rescore_human_review.py"
SPEC = importlib.util.spec_from_file_location("rescore_human_review", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
score_slice = MODULE.score_slice


def test_human_review_point_comparable_slice_is_frozen():
    import json
    calls = json.loads(MODULE.CACHED.read_text())["calls"]
    result = score_slice(calls)
    assert (result["tp"], result["fp"], result["fn"]) == (2, 5, 3)
    assert result["precision"] == 2 / 7
    assert result["recall"] == 0.4
    assert result["micro_f1"] == 1 / 3


def test_unadjudicated_predictions_do_not_become_false_positives():
    calls = [{"index": 2, "events": [
        {"label": "steal", "time_seconds": 760.75},
        {"label": "turnover", "time_seconds": 760.75},
    ]}]
    result = score_slice(calls)
    assert (result["tp"], result["fp"], result["fn"]) == (1, 0, 0)
