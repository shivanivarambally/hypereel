"""Offline checks for controlled pilot image selection and context instructions."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run_evidence_pilot import make_manifest,pilot_prompt


def fixture():
 a={'time':10,'wide':{'path':'wide.jpg','sha256':'a'},'crop':{'path':'crop.jpg','sha256':'b'}}
 b={'time':12,'wide':{'path':'wide2.jpg','sha256':'c'}}
 return {'window':{'start':10,'end':12},'frames':[a,b],'sparse_frames':[b]}


def test_crops_supplement_every_wide_view_and_absence_never_drops_frame():
 w=fixture();items=make_manifest(w,'wide12_ball_crops')
 assert [i['path'] for i in items]==['wide.jpg','crop.jpg','wide2.jpg']
 assert [i['time'] for i in items]==[10,10,12]
 assert [i['path'] for i in make_manifest(w,'wide12_context')]==['wide.jpg','wide2.jpg']
 assert [i['path'] for i in make_manifest(w,'wide6_context')]==['wide2.jpg']


def test_common_prompt_preserves_core_scope_and_treats_crop_as_uncertain():
 w=fixture();text=pilot_prompt(w,make_manifest(w,'wide12_ball_crops'))
 assert 'Evaluation interval: [10, 12]' in text
 assert 'unverified detector suggestion' in text
 assert 'SAME instant,not separate events' in text
 assert 'steal' in text and 'offensive_rebound' in text


def test_sheet_time_mapping_and_identical_no_crop_evidence():
 from run_evidence_pilot_sheets import pilot_prompt as sheet_prompt
 a={'time':1,'row_times':[1,2],'sha256':'same','path':'wide'}
 b={**a,'path':'crop'}
 w={'window':{'start':1,'end':2}}
 assert sheet_prompt(w,[a])==sheet_prompt(w,[b])
 assert '"top_time": 1, "bottom_time": 2' in sheet_prompt(w,[a])
 assert 'LEFT panel is a wide view' in sheet_prompt(w,[a])
