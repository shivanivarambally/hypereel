import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/score_gemini_broader_fix_eval.py"
SPEC = importlib.util.spec_from_file_location("score_gemini_broader_fix_eval", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_broader_before_after_accounting_is_frozen():
    baseline = MODULE.score(MODULE.RUNS["baseline_034"])["overall"]
    current = MODULE.score(MODULE.RUNS["current_037_plus_036"])["overall"]
    assert (baseline["tp"], baseline["fp"], baseline["fn"], baseline["f1"]) == (5, 3, 3, 0.625)
    assert (current["tp"], current["fp"], current["fn"], current["f1"]) == (4, 2, 4, 4/7)


def test_wrong_team_rebound_and_later_unresolved_miss_are_not_overcredited():
    assert "W6-def-rebound" not in MODULE.RUNS["baseline_034"]["matched"]
    assert "W6-def-rebound" in MODULE.RUNS["current_037_plus_036"]["matched"]
    assert "W6-first-miss" not in MODULE.RUNS["current_037_plus_036"]["matched"]
