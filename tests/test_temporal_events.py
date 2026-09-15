import json
from types import SimpleNamespace

import pytest

from hypereel.analyze.classifier import classify_moments
from hypereel.analyze.temporal_events import (discovery_prompt, parse_discovery,
                                              parse_verification, verification_prompt)
from hypereel.config import Settings
from hypereel.models import CandidateWindow
from hypereel.models import Clip, Classification
from hypereel.select.selector import select_clips


def payload(label='made_basket', time=3, **kwargs):
    return dict(moment_type=label, time_seconds=time, confidence=.8,
                subject_present=True, team='red', reason='ball passes through net', **kwargs)


def discover(recipe):
    return parse_discovery(json.dumps({'events': [payload(), payload('block', 1)]}),
                           recipe, CandidateWindow(start=10, end=15), 10, 4)


def test_multiple_events_keep_anchors_and_provenance(basketball_recipe):
    events = discover(basketball_recipe)
    assert [e.event_time for e in events] == [13, 11]
    assert [e.event_id for e in events] == ['w4e0', 'w4e1']
    assert events[1].phase1_moment_type == 'block'


@pytest.mark.parametrize('time', [-1, 8, float('nan')])
def test_out_of_window_or_invalid_time_is_not_silently_clamped(basketball_recipe, time):
    with pytest.raises(ValueError):
        parse_discovery(json.dumps({'events':[payload(time=time)]}), basketball_recipe,
                        CandidateWindow(start=10, end=15), 10, 0)


def test_verifier_can_correct_same_event_and_missing_id_goes_to_review(basketball_recipe):
    proposals = discover(basketball_recipe)
    raw = json.dumps({'events':[payload('block', 3, event_id='w4e0', status='corrected')]})
    results = parse_verification(raw, proposals, basketball_recipe, CandidateWindow(start=10,end=15), 10)
    assert results[0].moment_type == 'block' and results[0].decision == 'confirmed'
    assert results[0].phase1_moment_type == 'made_basket'
    assert results[1].decision == 'potential_event'
    assert results[1].expert_review_required


def test_rejected_hidden_outcome_is_retained_and_duplicate_ids_fail(basketball_recipe):
    proposals = discover(basketball_recipe)
    row = payload(event_id='w4e0', status='rejected')
    row['reason'] = 'outcome is off-camera'
    results = parse_verification(json.dumps({'events':[row]}), proposals, basketball_recipe,
                                 CandidateWindow(start=10,end=15), 10)
    assert results[0].decision == 'potential_event'
    with pytest.raises(ValueError):
        parse_verification(json.dumps({'events':[row,row]}), proposals, basketball_recipe,
                           CandidateWindow(start=10,end=15), 10)


def test_expansion_preserves_all_events_and_original_context(basketball_recipe):
    events = discover(basketball_recipe)
    provider = SimpleNamespace(classify_video_events=lambda *a, **kw: events)
    window = CandidateWindow(start=10,end=15)
    windows, results = classify_moments([window], basketball_recipe, provider,
                                       Settings(two_phase_verification=True), '/video.mp4')
    assert windows == [window, window] and results == events


def test_verified_correction_cannot_substitute_far_away_event(basketball_recipe):
    proposals = discover(basketball_recipe)
    row = payload(time=0, event_id='w4e0', status='corrected')
    results = parse_verification(json.dumps({'events':[row]}), proposals, basketball_recipe,
                                 CandidateWindow(start=10,end=15), 10)
    assert results[0].decision == 'potential_event'


def test_footage_dedup_keeps_multiple_events_but_not_outside_anchors(basketball_recipe):
    events = [Classification(moment_type=label,event_time=t,event_id=str(i),decision='confirmed')
              for i,(label,t) in enumerate([('steal_break',11),('made_basket',14),('block',99)])]
    clips = [Clip(start=10,end=16,moment_type=e.moment_type,score=.9,events=[e]) for e in events]
    picked = select_clips(clips,basketball_recipe)
    assert len(picked) == 1
    assert [e.moment_type for e in picked[0].events] == ['steal_break','made_basket']


def test_review_queue_keeps_proposed_timestamp_and_team(basketball_recipe):
    from hypereel.analyze.two_phase import build_review_queue
    from hypereel.analyze.temporal_events import potential
    event = potential(discover(basketball_recipe)[0], 'UNCERTAIN: outcome obscured')
    item = build_review_queue([CandidateWindow(start=10,end=15)], [event])[0]
    assert item.event_time == 13 and item.team == 'red' and item.event_id == 'w4e0'


def test_verification_failure_retains_all_discovery_events(basketball_recipe):
    from unittest.mock import Mock
    from hypereel.providers.gemini_video import GeminiVideoVisionProvider
    provider = GeminiVideoVisionProvider(Settings())
    provider._video_payload = Mock(return_value=(b'test',10,5))
    provider.client.generate = Mock(side_effect=[json.dumps({'events':[payload(),payload('block',1)]}),
                                                ValueError('malformed')])
    results = provider.classify_video_events('test',CandidateWindow(start=10,end=15),basketball_recipe)
    assert len(results) == 2 and all(e.decision == 'potential_event' for e in results)
    assert provider.client.generate.call_count == 2


def test_assist_anchoring_is_specified_identically_in_both_prompts(basketball_recipe):
    """W2/050: phase 1 anchored an assist at the basket (12.1s), phase 2 at the pass
    (8.7s). The 3.4s gap exceeded the 2s guard, so parse_verification discarded an
    assist both phases agreed on. Neither prompt named an anchor for assists."""
    window = CandidateWindow(start=10, end=15)
    for text in (discovery_prompt(basketball_recipe, window, 10),
                 verification_prompt(basketball_recipe, window, 10, [])):
        assert 'ASSIST' in text and 'PASS' in text, 'assist anchor must be specified'
