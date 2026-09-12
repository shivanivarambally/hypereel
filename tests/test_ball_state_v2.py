import pytest,json
from hypereel.evaluation.ball_state_v2 import derive,parse

def r(t,s,team='red',zone='unknown',player='unknown'):return dict(time_seconds=t,ball_state=s,team=team,release_zone=zone,player=player)
def labels(rows):return [e['label'] for e in derive(rows,0,20)[0]]
def test_unseen_or_unexplained_change_is_not_steal():
 assert labels([r(0,'held'),r(1,'not_visible'),r(2,'held','blue')])==[]
 assert labels([r(0,'held'),r(2,'held','blue')])==[]
def test_intercepted_pass_is_not_shot():
 assert labels([r(0,'held'),r(1,'pass_release'),r(2,'in_flight'),r(3,'interception','blue')])==['steal','turnover']
def test_airball_and_rebound_require_explicit_miss_not_rim():
 prefix=[r(0,'shot_release',zone='inside_arc'),r(1,'in_flight')]
 assert labels(prefix+[r(2,'missed'),r(3,'held','blue')])==['two_point_miss','defensive_rebound']
 assert labels(prefix+[r(2,'loose'),r(3,'held','blue')])==[]
def test_rim_contact_does_not_prove_miss():
 assert labels([r(0,'shot_release',zone='inside_arc'),r(1,'rim_contact'),r(2,'through_net')])==['two_point_made']
def test_release_zone_is_not_overwritten_by_ball_location():
 assert labels([r(0,'shot_release',zone='inside_arc'),r(1,'in_flight',zone='beyond_arc'),r(2,'through_net')])==['two_point_made']
 with pytest.raises(ValueError):parse(json.dumps({'frames':[r(1,'in_flight',zone='beyond_arc')]}),[1])
def test_pass_needs_different_known_player_for_assist():
 rows=[r(0,'pass_release',player='1'),r(1,'shot_release',zone='inside_arc',player='2'),r(2,'through_net')]
 assert labels(rows)==['two_point_made','assist']
 rows[0]['player']='unknown';assert labels(rows)==['two_point_made']
def test_free_throw_release_and_core_boundary():
 rows=[r(0,'shot_release',zone='free_throw_line'),r(2,'through_net')]
 assert labels(rows)==['free_throw_made']
 assert derive(rows,3,5)[0]==[]
def test_parser_requires_real_timestamps_and_all_rows():
 with pytest.raises(ValueError):parse(json.dumps({'frames':[r(0,'held')]}),[0,1])
 with pytest.raises(ValueError):parse(json.dumps({'frames':[r(True,'held')]}),[1])
def test_predeclared_timestamp_keyed_shape_keeps_semantics():
 row=r(1,'held')
 assert parse(json.dumps({'1':row}),[1])==[row]
 with pytest.raises(ValueError):parse(json.dumps({'2':row}),[1])
def test_concatenated_batches_preserve_release_to_outcome():
 batches=[[r(0,'shot_release',zone='inside_arc')],[r(1,'in_flight'),r(2,'through_net')]]
 assert labels([row for batch in batches for row in batch])==['two_point_made']
