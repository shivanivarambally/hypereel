"""Durable evidence survives process interruption without inventing usage."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from hypereel.checkpoints import CheckpointWriteError
from hypereel.config import Settings, get_settings
from hypereel.observability import (
    authorize_provider_call, provider_budget_scope, record_local_provider_usage,
    record_local_provider_failure,
)


def start():
    authorize_provider_call(provider="ollama", model="local-model", operation="vision", local=True)


def rows(directory):
    return [json.loads(line) for line in next(directory.glob('calls-*.jsonl')).read_text().splitlines()]


def test_journal_survives_hard_process_exit(tmp_path):
    code = '''
import os, sys
from hypereel.config import Settings
from hypereel.observability import provider_budget_scope, authorize_provider_call, record_local_provider_usage
with provider_budget_scope(Settings(provider_checkpoint_dir=sys.argv[1])):
    authorize_provider_call(provider="ollama", model="local", operation="vision", local=True)
    record_local_provider_usage({"prompt_eval_count":123,"eval_count":7},elapsed_seconds=1)
    authorize_provider_call(provider="ollama", model="local", operation="vision", local=True)
    os._exit(9)
'''
    result = subprocess.run([sys.executable, '-c', code, str(tmp_path)])
    assert result.returncode == 9
    evidence = rows(tmp_path)
    assert [r['event'] for r in evidence] == ['scope_started', 'call_started', 'call_finished', 'call_started']
    assert evidence[2]['call']['total_tokens'] == 130
    assert evidence[3]['call']['status'] == 'started'
    assert 'total_tokens' not in evidence[3]['call']


def test_completed_classification_survives_next_window_interrupt(tmp_path, basketball_recipe):
    from hypereel.analyze.classifier import classify_candidates
    from hypereel.models import CandidateWindow, Classification
    class Provider:
        def classify_window(self, frames, recipe, window_index):
            start()
            if window_index == 1:
                raise KeyboardInterrupt()
            record_local_provider_usage({'prompt_eval_count': 12, 'eval_count': 3}, elapsed_seconds=1)
            return Classification(moment_type='steal', confidence=.9, reason='test evidence')
    settings = Settings(provider_checkpoint_dir=str(tmp_path))
    with pytest.raises(KeyboardInterrupt):
        with provider_budget_scope(settings):
            classify_candidates([CandidateWindow(start=1,end=3),CandidateWindow(start=4,end=6)],
                                basketball_recipe, Provider(), settings)
    evidence=rows(tmp_path)
    classified=[r for r in evidence if r['event']=='classification']
    assert classified[0]['classification']['moment_type']=='steal'
    assert classified[0]['window']=={'start':1,'end':3}
    assert evidence[-1]['event']=='scope_interrupted'
    assert evidence[-1]['calls'][0]['total_tokens']==15
    assert evidence[-1]['calls'][1]['status']=='started'


def test_error_safe_fields_and_unique_files(tmp_path):
    settings=Settings(provider_checkpoint_dir=str(tmp_path))
    with provider_budget_scope(settings):
        start()
        record_local_provider_failure(TimeoutError('secret-url'),elapsed_seconds=1)
    original=next(tmp_path.glob('*.jsonl')).read_bytes()
    with provider_budget_scope(settings):
        pass
    assert len(list(tmp_path.glob('*.jsonl')))==2
    assert any(p.read_bytes()==original for p in tmp_path.glob('*.jsonl'))
    assert b'secret-url' not in original
    assert b'TimeoutError' in original


def test_failed_checkpoint_blocks_following_authorization(tmp_path, monkeypatch):
    with pytest.raises(CheckpointWriteError):
        with provider_budget_scope(Settings(provider_checkpoint_dir=str(tmp_path))) as state:
            def fail(_):raise OSError('disk unavailable')
            monkeypatch.setattr(os,'fsync',fail)
            with pytest.raises(CheckpointWriteError):start()
            assert state['journal'].failed
            with pytest.raises(CheckpointWriteError):start()


def test_checkpoint_environment_opt_in(monkeypatch,tmp_path):
    monkeypatch.setenv('HYPEREEL_PROVIDER_CHECKPOINT_DIR',str(tmp_path))
    assert get_settings().provider_checkpoint_dir==str(tmp_path)


def test_error_classification_omits_raw_exception_text(tmp_path):
    from hypereel.observability import checkpoint_classification
    from hypereel.models import Classification, CandidateWindow
    with provider_budget_scope(Settings(provider_checkpoint_dir=str(tmp_path))):
        checkpoint_classification(0, CandidateWindow(start=1,end=2),
                                  Classification(reason="ollama error: secret-url"))
    evidence = rows(tmp_path)
    assert evidence[1]['classification']['reason'] == 'ollama error: details omitted'
    assert 'secret-url' not in str(evidence)
