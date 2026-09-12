"""Protect the all-event scope from silently reverting to highlight-only labels."""
import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('all_events_builder', Path(__file__).resolve().parents[1] / 'scripts/build_all_events_development.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def test_every_development_annotation_survives_with_unique_identity():
    rows, manifest = builder.build()
    assert len(rows) == 462
    assert len({row['reference_id'] for row in rows}) == 462
    assert sum(manifest['counts_by_type'].values()) == 462
    assert set(row['game_id'] for row in rows) == set(builder.GAMES)
    assert manifest['counts_by_type']['turnover'] == 95
    assert manifest['counts_by_type']['offensive_rebound'] == 43
    assert manifest['counts_by_type']['defensive_rebound'] == 47
    assert all(row['action_start_seconds'] is None for row in rows)
    assert all(row['action_end_seconds'] is None for row in rows)


@pytest.mark.parametrize('event', [{'event_type': 'NEW_TYPE'}, {'event_type': '2PT', 'outcome': 'unknown'}])
def test_unknown_labels_fail_instead_of_becoming_negatives(event):
    with pytest.raises(ValueError, match='Unmapped'):
        builder.event_label(event)


def test_paired_steal_and_turnover_are_preserved_separately():
    rows, _ = builder.build()
    paired = [row for row in rows if row['game_id'] == 'unlimited-vs-campus' and row['source_timestamp_seconds'] == 212]
    assert {row['label'] for row in paired} == {'steal', 'turnover'}
    assert len({row['reference_id'] for row in paired}) == 2
