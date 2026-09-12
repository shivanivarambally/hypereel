import json
import pytest
from hypereel.evaluation.basketball_events import LABELS, parse_window_events, partition_by_core
from hypereel.evaluation.transcript import (ENTAILMENT_CUES, ENTAILMENT_REQUIREMENTS, entailment_elements,
                                             hedging_tokens, parse_transcript, parse_extracted_events,
                                             parse_window_extracted_events, reject_unentailed,
                                             screen_extracted_events)


def test_transcript_rejects_unseen_timestamp_and_reversed_order():
    row=lambda t:dict(time_seconds=t,observation='Blue controls the ball.',visibility='clear')
    for rows in [[row(3)], [row(2),row(1)]]:
        with pytest.raises(ValueError):parse_transcript(json.dumps({'observations':rows}),[1,2])


def test_extraction_preserves_paired_events_but_rejects_invented_citation():
    rows=parse_transcript(json.dumps({'observations':[dict(time_seconds=2,observation='Blue takes control after disrupting red.',visibility='clear')]}),[1,2])
    event=dict(label='steal',time_seconds=2,confidence=.5,evidence='Blue gains control.',observation_ids=['o1'])
    pair=[event,dict(event,label='turnover')]
    assert len(parse_extracted_events(json.dumps({'events':pair}),rows,1,2))==2
    with pytest.raises(ValueError):parse_extracted_events(json.dumps({'events':[dict(event,observation_ids=['o99'])]}),rows,1,2)


def test_empty_transcript_cannot_support_an_event():
    assert parse_transcript('{"observations":[]}',[1,2])==[]
    event=dict(label='steal',time_seconds=2,confidence=.5,evidence='Claim',observation_ids=['o1'])
    with pytest.raises(ValueError):parse_extracted_events(json.dumps({'events':[event]}),[],1,2)


CONTEXT=(221.,233.)
CORE=(223.,231.)


def _rows():
    return parse_transcript(json.dumps({'observations':[
        dict(time_seconds=221.,observation='Blue controls the ball at the top of the key.',visibility='clear'),
        dict(time_seconds=233.,observation='Yellow brings the ball up the floor.',visibility='uncertain')]}),[221.,233.])


def _payload(times,cited=False):
    event=lambda t:dict(label='steal',time_seconds=t,confidence=.5,evidence='Blue gains control.')
    return json.dumps({'events':[dict(event(t),observation_ids=['o1']) if cited else event(t) for t in times]})


def test_both_arms_place_an_out_of_core_context_event_in_context_not_window_failure():
    """Pilot015 regression: direct filtered an out-of-core event, extraction discarded the window."""
    direct=parse_window_events(_payload([225.,233.]),*CONTEXT,*CORE)
    transcript=parse_window_extracted_events(_payload([225.,233.],cited=True),_rows(),*CONTEXT,*CORE)
    for core,context in (direct,transcript):
        assert [e['time_seconds'] for e in core]==[225.]
        assert [e['time_seconds'] for e in context]==[233.]


def test_both_arms_still_reject_an_event_outside_the_observed_context_span():
    for call in [lambda:parse_window_events(_payload([240.]),*CONTEXT,*CORE),
                 lambda:parse_window_extracted_events(_payload([240.],cited=True),_rows(),*CONTEXT,*CORE)]:
        with pytest.raises(ValueError):call()


def test_partition_is_lossless_and_core_must_lie_inside_context():
    events=[dict(label='steal',time_seconds=t,confidence=.5,evidence='x') for t in [221.,225.,233.]]
    core,context=partition_by_core(events,*CORE)
    assert len(core)+len(context)==len(events)
    assert [e['time_seconds'] for e in core]==[225.]
    assert [e['time_seconds'] for e in context]==[221.,233.]
    with pytest.raises(ValueError):parse_window_events(_payload([225.]),223.,231.,221.,233.)


def test_strict_core_parsing_still_rejects_an_out_of_core_event():
    """The original all-or-nothing mode stays available and documented."""
    with pytest.raises(ValueError):parse_extracted_events(_payload([233.],cited=True),_rows(),*CORE)


def test_entailment_rubric_covers_every_label_and_element():
    assert set(ENTAILMENT_REQUIREMENTS)==set(LABELS)
    assert {e for v in ENTAILMENT_REQUIREMENTS.values() for e in v} <= set(ENTAILMENT_CUES)


def test_ball_in_the_air_is_not_a_shot_outcome():
    """The exact substitution pilot015 made: an attempt in flight scored as a miss."""
    flight=['The ball is in the air, moving towards the basket. Players are ready to rebound.']
    required,found,missing=entailment_elements('two_point_miss',flight,flight)
    assert 'shot_outcome' in missing and 'shot_outcome' not in found
    landed=['The ball makes contact with the rim, bouncing off after the shot.']
    assert entailment_elements('two_point_miss',landed,landed)[2]==[]


def test_prior_elements_are_screened_against_earlier_observations_not_only_the_citation():
    cited=['A player in blue is seen with the ball.']
    prior=['A player in black releases the ball.','The ball bounces off the rim.']+cited
    assert entailment_elements('defensive_rebound',cited,cited)[2]==['prior_miss']
    assert entailment_elements('defensive_rebound',cited,prior)[2]==[]


def test_hedged_text_is_detected_regardless_of_the_visibility_flag():
    assert hedging_tokens('A player in blue is seen with the ball, possibly after a rebound.')==['possibly']
    assert hedging_tokens('Blue controls the ball.')==[]


def test_screening_records_without_rejecting_and_strict_mode_rejects():
    rows=parse_transcript(json.dumps({'observations':[
        dict(time_seconds=1,observation='Black releases the ball; it bounces off the rim.',visibility='clear'),
        dict(time_seconds=2,observation='The ball is in the air, moving towards the basket.',visibility='clear')]}),[1,2])
    events=[dict(label='two_point_miss',time_seconds=2,confidence=1.,evidence='e',observation_ids=['o2']),
            dict(label='two_point_miss',time_seconds=2,confidence=1.,evidence='e',observation_ids=['o1'])]
    screened=screen_extracted_events(events,rows)
    assert len(screened)==2, 'recording mode must never drop an event'
    assert [e['entailment']['screen'] for e in screened]==['unsupported','supported']
    assert [e['label'] for e in reject_unentailed(events,rows)]==['two_point_miss']
    assert len(reject_unentailed(events,rows))==1
