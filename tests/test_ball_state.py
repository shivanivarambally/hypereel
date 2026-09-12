import json
import pytest
from hypereel.evaluation.ball_state import (BALL_STATES, contradictory_pairs, derive_events,
                                            parse_states, state_prompt)

CORE = (0., 20.)


def frame(t, state, team='black', zone='unknown'):
    return dict(time_seconds=t, ball_state=state, team=team, court_zone=zone)


def labels(states, core=CORE):
    events, _ = derive_events(states, *core)
    return [(e['label'], e['time_seconds']) for e in events]


def test_made_shot_requires_the_ball_through_the_net():
    seen = [frame(0, 'held', zone='beyond_arc'), frame(2, 'in_flight'), frame(4, 'through_net')]
    assert labels(seen) == [('three_point_made', 4)]


def test_flight_that_leaves_view_yields_no_shot_event_and_says_why():
    seen = [frame(0, 'held', zone='inside_arc'), frame(2, 'in_flight'), frame(4, 'not_visible')]
    events, notes = derive_events(seen, *CORE)
    assert events == []
    assert any('outcome unobserved' in n for n in notes)


def test_rim_contact_then_possession_is_a_miss_and_names_the_rebound_by_team():
    shot = [frame(0, 'held', 'black', 'inside_arc'), frame(2, 'in_flight'), frame(4, 'rim_contact')]
    assert labels(shot + [frame(6, 'held', 'blue')]) == [('two_point_miss', 4), ('defensive_rebound', 6)]
    assert labels(shot + [frame(6, 'held', 'black')]) == [('two_point_miss', 4), ('offensive_rebound', 6)]


def test_unknown_court_zone_emits_no_typed_shot_rather_than_guessing():
    seen = [frame(0, 'held'), frame(2, 'in_flight'), frame(4, 'through_net')]
    events, notes = derive_events(seen, *CORE)
    assert events == []
    assert any('court zone unknown' in n for n in notes)


def test_possession_change_without_a_shot_is_a_paired_turnover_and_steal():
    assert labels([frame(0, 'held', 'black'), frame(2, 'held', 'blue')]) == [('turnover', 2), ('steal', 2)]


def test_block_requires_a_defender_deflecting_a_live_flight():
    seen = [frame(0, 'held', 'black', 'inside_arc'), frame(2, 'in_flight'), frame(4, 'deflected', 'blue')]
    assert labels(seen) == [('block', 4)]
    stray, notes = derive_events([frame(0, 'deflected', 'blue')], *CORE)
    assert stray == [] and any('without a live flight' in n for n in notes)


def test_assist_is_not_derived_because_a_pass_is_not_observable_from_team_colour():
    """Consecutive held frames by one team are continued possession, not an observed pass."""
    made = [frame(0, 'held', 'black'), frame(2, 'held', 'black', 'beyond_arc'),
            frame(4, 'in_flight'), frame(6, 'through_net')]
    assert labels(made) == [('three_point_made', 6)]
    missed = made[:3] + [frame(6, 'rim_contact'), frame(8, 'held', 'blue')]
    assert [l for l, _ in labels(missed)] == ['three_point_miss', 'defensive_rebound']


def test_parser_accepts_the_timestamp_keyed_serialisation_with_identical_semantics():
    listed = json.dumps({'frames': [frame(0, 'held'), frame(2, 'in_flight')]})
    keyed = json.dumps({'0': frame(0, 'held'), '2': frame(2, 'in_flight')})
    assert parse_states(keyed, [0, 2]) == parse_states(listed, [0, 2])
    with pytest.raises(ValueError):
        parse_states(json.dumps({'0': dict(frame(0, 'held'), ball_state='dunked')}), [0])


def test_derived_events_outside_the_core_window_are_reported_not_emitted():
    seen = [frame(0, 'held', zone='inside_arc'), frame(2, 'in_flight'), frame(4, 'through_net')]
    events, notes = derive_events(seen, 10., 20.)
    assert events == [] and any('outside the core window' in n for n in notes)


@pytest.mark.parametrize('sequence', [
    [frame(0, 'held', 'black', 'inside_arc'), frame(2, 'in_flight'), frame(4, 'rim_contact'), frame(6, 'held', 'black')],
    [frame(0, 'held', 'black', 'beyond_arc'), frame(2, 'in_flight'), frame(4, 'through_net'),
     frame(6, 'held', 'blue'), frame(8, 'in_flight'), frame(10, 'rim_contact'), frame(12, 'held', 'black')],
    [frame(t, state) for t, state in enumerate(BALL_STATES)],
])
def test_derivation_can_never_emit_mutually_exclusive_labels(sequence):
    events, _ = derive_events(sequence, 0., 60.)
    assert contradictory_pairs(events) == []


def test_state_parser_rejects_wrong_length_unknown_states_and_drifting_timestamps():
    ok = json.dumps({'frames': [frame(0, 'held'), frame(2, 'in_flight')]})
    assert [r['ball_state'] for r in parse_states(ok, [0, 2])] == ['held', 'in_flight']
    for raw, times in [(ok, [0, 2, 4]),
                       (json.dumps({'frames': [frame(0, 'dunked'), frame(2, 'held')]}), [0, 2]),
                       (json.dumps({'frames': [frame(0, 'held'), frame(9, 'held')]}), [0, 2]),
                       (json.dumps({'frames': [dict(frame(0, 'held'), court_zone='midcourt'), frame(2, 'held')]}), [0, 2])]:
        with pytest.raises(ValueError):
            parse_states(raw, times)


def test_prompt_offers_the_closed_vocabulary_and_forbids_the_scoreboard():
    prompt = state_prompt([1., 2.])
    assert all(state in prompt for state in BALL_STATES)
    assert 'scoreboard' in prompt.lower()
