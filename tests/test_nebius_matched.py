"""Offline parity checks: never call a provider or load the final holdout."""
import importlib.util
import json
from pathlib import Path
import pytest
from hypereel.evaluation.basketball_events import build_prompt, build_observation_prompt, score_events

ROOT = Path(__file__).resolve().parents[1]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_nebius_transport_keeps_prompt_and_image_bytes():
    runner = load(ROOT/'scripts/eval_nebius_matched.py', 'matched_runner')
    args = runner.request_arguments(['YWJj', 'ZGVm'], 'exact prompt')
    assert args['model'] == 'openbmb/MiniCPM-V-4_5'
    assert args['max_tokens'] == 768 and args['temperature'] == args['seed'] == 0
    assert args['messages'] == [{'role':'user','content':[
        {'type':'text','text':'exact prompt'},
        {'type':'image_url','image_url':{'url':'data:image/jpeg;base64,YWJj'}},
        {'type':'image_url','image_url':{'url':'data:image/jpeg;base64,ZGVm'}}]}]


@pytest.mark.parametrize('n', ['009','010','011'])
def test_saved_local_prompt_and_scoring_are_unchanged(n):
    folder = ROOT/f'evals/iterations/ollama-all-events-{n}'
    old = load(folder/'detector-snapshot.py', 'hypereel.evaluation.frozen_test_'+n)
    baseline = json.loads((folder/'report.json').read_text())
    for window in baseline['windows']:
        times = window['frame_times']
        if baseline['settings']['prompt_variant'] == 'observations':
            assert build_observation_prompt(times) == old.build_observation_prompt(times)
        else:
            assert build_prompt(times) == old.build_prompt(times)
    assert score_events(baseline['scored_references'],[e for w in baseline['windows'] for e in w['events']]) == baseline['metrics']
