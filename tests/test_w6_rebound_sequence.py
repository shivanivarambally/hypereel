import importlib.util
import json
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/audit_w6_rebound_sequence.py"
SPEC = importlib.util.spec_from_file_location("audit_w6_rebound_sequence", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_wrong_team_does_not_receive_defensive_rebound_credit():
    events = [{
        "label": "defensive_rebound",
        "time_seconds": 1321.5,
        "evidence": "Yellow player rebounds the missed layup.",
    }]
    result = MODULE.audit(events)
    assert result["defensive_rebound"]["naive_label_time_match"] is True
    assert result["defensive_rebound"]["evidence_aware_match"] is False
    assert result["scoring_effect"]["evidence_aware"] == {"tp": 0, "fp": 1, "fn": 1}


def test_actual_run_remains_frozen_as_unsupported():
    report = json.loads(MODULE.RUN.read_text())
    events = next(call["events"] for call in report["calls"] if call["index"] == 6)
    result = MODULE.audit(events)
    assert result["defensive_rebound"]["predicted_team_from_evidence"] == "Campus"
    assert result["defensive_rebound"]["verdict"] == "unsupported"
    assert result["sequence_consistency"]["supported"] is False
