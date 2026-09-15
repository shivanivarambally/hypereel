"""Rules validation for detected basketball event sequences.

The W1 case is the reason this module exists: a made free throw followed by a
player collecting the ball was reported as a defensive rebound in all eight runs.
See docs/BASKETBALL_RULES.md.
"""
from hypereel.evaluation.basketball_rules import rules_prompt_text, validate_sequence


def event(label, time, team=None):
    return {'moment_type': label, 'event_time': time, 'team': team}


def rules(violations):
    return {v.rule for v in violations}


def test_w1_made_free_throw_then_rebound_is_illegal():
    """The actual W1 failure: the catch after a made free throw is an inbound."""
    found = validate_sequence([
        event('free_throw_made', 7.5, 'Spartans'),
        event('defensive_rebound', 8.25, 'Spartans'),
    ])
    assert 'R1' in rules(found)
    illegal = [v for v in found if v.rule == 'R1' and v.severity == 'illegal']
    assert illegal, 'made free throw followed by a rebound must be illegal'
    assert 'inbound' in illegal[0].detail


def test_made_field_goal_then_rebound_is_illegal():
    found = validate_sequence([
        event('two_point_made', 5.0, 'Blue'),
        event('defensive_rebound', 6.0, 'Black'),
    ])
    assert any(v.rule == 'R1' and v.severity == 'illegal' for v in found)


def test_missed_field_goal_then_rebound_is_legal():
    found = validate_sequence([
        event('two_point_miss', 5.0, 'Blue'),
        event('defensive_rebound', 6.0, 'Black'),
    ])
    assert found == []


def test_rebound_without_any_shot_is_illegal():
    found = validate_sequence([event('offensive_rebound', 4.0, 'Blue')])
    assert any(v.rule == 'R1' and v.severity == 'illegal' for v in found)


def test_same_team_rebound_must_be_offensive():
    found = validate_sequence([
        event('two_point_miss', 5.0, 'Blue'),
        event('defensive_rebound', 6.0, 'Blue'),
    ])
    assert any(v.rule == 'R2' and v.severity == 'illegal' for v in found)


def test_opposing_team_rebound_must_be_defensive():
    found = validate_sequence([
        event('three_point_miss', 5.0, 'Blue'),
        event('offensive_rebound', 6.0, 'Black'),
    ])
    assert any(v.rule == 'R2' and v.severity == 'illegal' for v in found)


def test_missed_free_throw_rebound_is_flagged_for_review_not_rejected():
    """Legal only on the final attempt, which the taxonomy does not record."""
    found = validate_sequence([
        event('free_throw_miss', 5.0, 'Blue'),
        event('defensive_rebound', 6.0, 'Black'),
    ])
    assert [v.severity for v in found if v.rule == 'R1'] == ['review']


def test_assist_without_made_field_goal_is_illegal():
    found = validate_sequence([
        event('free_throw_made', 5.0, 'Blue'),
        event('assist', 4.8, 'Blue'),
    ])
    assert any(v.rule == 'R4' and v.severity == 'illegal' for v in found)


def test_assist_with_made_field_goal_is_legal():
    found = validate_sequence([
        event('assist', 4.8, 'Blue'),
        event('two_point_made', 5.0, 'Blue'),
    ])
    assert found == []


def test_block_without_shot_is_flagged():
    found = validate_sequence([event('block', 4.0, 'Black')])
    assert any(v.rule == 'R5' for v in found)


def test_steal_and_turnover_together_are_flagged():
    found = validate_sequence([
        event('steal', 4.0, 'Blue'),
        event('turnover', 4.0, 'Black'),
    ])
    assert any(v.rule == 'R6' for v in found)


def test_ordering_is_by_event_time_not_list_order():
    """The rebound is listed first but occurs after the shot."""
    found = validate_sequence([
        event('defensive_rebound', 8.25, 'Spartans'),
        event('free_throw_made', 7.5, 'Spartans'),
    ])
    assert any(v.rule == 'R1' and v.severity == 'illegal' for v in found)


def test_clean_multi_event_sequence_passes():
    found = validate_sequence([
        event('turnover', 3.8, 'Campus'),
        event('two_point_miss', 6.2, 'Unlimited'),
        event('offensive_rebound', 7.5, 'Unlimited'),
    ])
    assert found == []


def test_rules_prompt_text_states_the_w1_rule():
    text = rules_prompt_text()
    assert 'Never report a rebound after a made shot' in text
    assert 'inbounding' in text


def test_legacy_taxonomy_labels_are_recognised_as_shots():
    """Older recipes emit made_basket / three_pointer; rules must cover both sets."""
    assert validate_sequence([
        event('made_basket', 3.0, 'red'),
        event('block', 1.0, 'blue'),
    ]) == []
    found = validate_sequence([
        event('three_pointer', 5.0, 'red'),
        event('defensive_rebound', 6.0, 'blue'),
    ])
    assert any(v.rule == 'R1' and v.severity == 'illegal' for v in found)
