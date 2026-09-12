import json
from pathlib import Path
from unittest.mock import Mock
import pytest
from hypereel.config import Settings
from hypereel.models import CandidateWindow, Classification
from hypereel.recipe import load_recipe
from hypereel.analyze.classifier import classify_candidates
from hypereel.providers import gemini_video
from hypereel.providers._util import build_classification_prompt

@pytest.fixture
def recipe():
    return load_recipe(Path(__file__).resolve().parents[1]/'recipes/basketball_demo_video.yaml')

def test_classifier_dispatches_real_video_without_extracting_sparse_frames(recipe,monkeypatch):
    provider=Mock();expected=Classification(moment_type='steal',subject_present=True,confidence=.9)
    provider.classify_video_window.return_value=expected
    monkeypatch.setattr('hypereel.analyze.classifier.extract_frames',Mock(side_effect=AssertionError('No sparse fallback')))
    window=CandidateWindow(start=8,end=14)
    assert classify_candidates([window],recipe,provider,Settings(),'/real.mp4')==[expected]
    provider.classify_video_window.assert_called_once_with('/real.mp4',window,recipe,window_index=0)
    provider.classify_window.assert_not_called()

def test_rebound_recipe_is_not_negated_by_shared_prompt(recipe):
    prompt=build_classification_prompt(recipe)
    assert '- rebound:' in prompt
    assert 'Rebounds are allowed' in prompt
    assert 'defensive rebound, missed shot' not in prompt

@pytest.mark.parametrize("minimum,start,duration", [(0,6,10),(12,5,12),(50,1,20)])
def test_video_payload_contains_temporal_media(recipe,monkeypatch,minimum,start,duration):
    recipe.scorer_signals()[0].params["min_video_seconds"] = minimum
    provider=gemini_video.GeminiVideoVisionProvider(Settings())
    def ffmpeg(args,**kwargs):Path(args[-1]).write_bytes(b'fake-video')
    monkeypatch.setattr(gemini_video.subprocess,'run',ffmpeg)
    provider.client.generate=Mock(return_value=json.dumps({'moment_type':'steal','subject_present':True,'confidence':.9,'reason':'visible possession change'}))
    result=provider.classify_video_window('/source.mp4',CandidateWindow(start=8,end=14),recipe)
    assert result.moment_type=='steal'
    args=provider.client.generate.call_args
    assert args.args[0][0]['videoMetadata']=={'fps':4}
    assert args.kwargs['metadata']['source_start']==start
    assert args.kwargs['metadata']['duration']==duration

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(gemini_video,'ROOT',tmp_path)
    folder=tmp_path/'evals/iterations';folder.mkdir(parents=True)
    (folder/'spend-ledger.json').write_text('{"estimated_spend_usd":0}')
    (folder/'gemini-funded-budget.json').write_text('{"baseline_cumulative_ledger_usd":0,"new_evaluation_cap_usd":2}')
    return gemini_video.BudgetClient(Settings(gemini_model='gemini-3.8-flash'))

def test_unknown_provider_usage_retains_reservation(client):
    client.post=Mock(side_effect=[{'totalTokens':100},RuntimeError('temporary outage')])
    with pytest.raises(RuntimeError):client.generate([{'text':'test'}])
    assert client.read_spend()>0
    record=json.loads(next(client.logs.glob('*.json')).read_text())
    assert record['status']=='error' and 'raw_response' not in record

def test_success_reconciles_actual_usage(client):
    client.post=Mock(side_effect=[{'totalTokens':100},{'usageMetadata':{'promptTokenCount':100,'totalTokenCount':110,'candidatesTokenCount':10},'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':'ok'}]}}]}])
    assert client.generate([{'text':'test'}])=='ok'
    assert client.read_spend()==pytest.approx((100*.75+10*3.75)/1e6)
