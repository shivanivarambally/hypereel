"""Offline detection-scoring checks; no model calls or sealed references."""
import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location('golden_score', Path(__file__).resolve().parents[1]/'scripts/score_against_golden.py')
scorer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scorer)


def row(t=610):
    return dict(game_id='east-bay-elite-vs-spartans',event_time=t,
                source_event_type='2PT',source_outcome='miss',expected_moment_type=None)


def test_detection_uses_source_label_not_selection_eligibility():
    assert scorer.golden_label(row()) == 'two_point_miss'


def test_half_open_tiles_count_boundary_once():
    refs = [row()]
    assert scorer.references_for([600,610],refs[0]['game_id'],refs,'half-open') == []
    assert scorer.references_for([610,620],refs[0]['game_id'],refs,'half-open') == ['two_point_miss']


def test_sweep_uses_explicit_game_not_window_number():
    report = dict(game_id=row()['game_id'],cases=[dict(index=610,core=[610,620],
        arms={'two_phase':{'classifications':[dict(moment_type='two_point_miss',decision='confirmed')]}})])
    assert scorer.score(report,[row()],'confirmed',boundary='half-open')['overall']['tp'] == 1
    del report['game_id']
    with pytest.raises(ValueError,match='explicit game_id'):
        scorer.score(report,[row()],'confirmed')
