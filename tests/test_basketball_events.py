import json
import pytest
from hypereel.evaluation.basketball_events import parse_events,score_events,build_prompt,LABELS

def row(label,t=10,game='a'):
 return {'label':label,'time_seconds':t,'game_id':game}

def test_common_baskets_cannot_hide_three_failed_types():
 refs=[row('two_point_made',i*20) for i in range(100)]+[row(x) for x in ['steal','offensive_rebound','defensive_rebound']]
 preds=refs[:100];m=score_events(refs,preds)
 assert m['micro_recall']>.97
 assert m['macro_f1']==.25
 assert m['worst_type_recall']==0
 assert not m['release_gate_pass']

def test_same_label_one_to_one_and_cross_game_isolation():
 m=score_events([row('steal'),row('turnover')],[row('steal'),row('steal'),row('turnover',game='b')])
 assert (m['tp'],m['fp'],m['fn'])==(1,2,1)

def test_augmenting_match_avoids_greedy_false_negative():
 m=score_events([row('steal',0),row('steal',4)],[row('steal',2),row('steal',0)],2)
 assert m['tp']==2

def test_multiple_events_retained():
 text=json.dumps({'events':[dict(label=l,time_seconds=2,confidence=.7,evidence='visible possession change') for l in ['steal','turnover']]})
 assert len(parse_events(text,0,5))==2

@pytest.mark.parametrize('label,time,confidence',[('bad',2,.8),('steal',9,.8),('steal',2,float('nan'))])
def test_invalid_predictions_fail(label,time,confidence):
 with pytest.raises(ValueError):parse_events(json.dumps({'events':[dict(label=label,time_seconds=time,confidence=confidence,evidence='x')]}),0,5)

def test_prompt_covers_all_types_without_reference_hints():
 prompt=build_prompt([0,2,4,6]);assert all(label in prompt for label in LABELS)
 assert 'rebound' in prompt and 'turnover may coexist' in prompt
 assert 'reference' not in prompt.lower()


def test_observations_required_even_for_empty_predictions():
 from hypereel.evaluation.basketball_events import parse_observed_events
 with pytest.raises(ValueError):
  parse_observed_events(json.dumps({'observations':[], 'events':[]}),[0,2])
 valid={'observations':[{'time_seconds':t,'observation':'ball obscured'} for t in [0,2]],'events':[]}
 assert parse_observed_events(json.dumps(valid),[0,2])==[]
 valid['observations'].reverse()
 with pytest.raises(ValueError):parse_observed_events(json.dumps(valid),[0,2])
