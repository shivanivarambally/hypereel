"""Opt-in native-video Gemini adapter with shared funded-evaluation budget.

Used for the bounded demo; it never substitutes mock classifications on failure.
"""
from __future__ import annotations
import base64
from contextlib import contextmanager
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time
import urllib.request
import uuid
from datetime import datetime, timezone
from ..evaluation.gemini_budget import check_reservation
from ..models import Classification
from .base import VisionProvider, LLMProvider
from ._util import build_classification_prompt, parse_classification_json

ROOT = Path(__file__).resolve().parents[3]

class BudgetClient:
    def __init__(self, settings):
        self.settings = settings
        self.ledger = ROOT / settings.provider_spend_ledger_path
        self.logs = ROOT / 'evals/iterations/demo-integration-029'

    @contextmanager
    def locked(self):
        self.ledger.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger.with_suffix('.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def read_spend(self):
        return json.loads(self.ledger.read_text())['estimated_spend_usd']

    def write_spend(self, value):
        temp = self.ledger.with_suffix('.tmp')
        temp.write_text(json.dumps({'estimated_spend_usd': value}, indent=2))
        temp.replace(self.ledger)

    def post(self, method, payload):
        model = self.settings.gemini_model
        if model != 'gemini-3.8-flash':
            raise ValueError('Native-video demo pricing is pinned to gemini-3.8-flash')
        request = urllib.request.Request(
            f'https://generativelanguage.googleapis.com/v1beta/models/{model}:{method}',
            data=json.dumps(payload).encode(),
            headers={'x-goog-api-key': self.settings.gemini_api_key, 'Content-Type': 'application/json'})
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.load(response)

    def generate(self, parts, *, json_output=False, max_tokens=2048, metadata=None):
        config = {'temperature': 0, 'maxOutputTokens': min(max_tokens, 2048),
                  'thinkingConfig': {'thinkingLevel': 'LOW'}, 'mediaResolution': 'MEDIA_RESOLUTION_HIGH'}
        if json_output:
            config['responseMimeType'] = 'application/json'
        body = {'contents': [{'role': 'user', 'parts': parts}], 'generationConfig': config}
        count = self.post('countTokens', {'generateContentRequest': dict(body, model='models/'+self.settings.gemini_model)})
        reserve = (count['totalTokens'] * 1.25 * .75 + config['maxOutputTokens'] * 3.75) / 1e6 + .01
        with self.locked():
            spent = self.read_spend()
            check_reservation(ROOT, spent, reserve)
            self.write_spend(spent + reserve)
        self.logs.mkdir(parents=True, exist_ok=True)
        path = self.logs / (uuid.uuid4().hex + '.json')
        record = {'started_at': datetime.now(timezone.utc).isoformat(), 'status': 'reserved',
                  'reserved_usd': reserve, 'model': self.settings.gemini_model, 'config': config,
                  'metadata': metadata, 'prompt': [p['text'] for p in parts if 'text' in p],
                  'token_preflight': count}
        path.write_text(json.dumps(record, indent=2))
        started = time.monotonic()
        try:
            raw = self.post('generateContent', body)
            record['raw_response'] = raw
            usage = raw.get('usageMetadata', {})
            if 'promptTokenCount' not in usage or 'totalTokenCount' not in usage:
                raise ValueError('Missing usage; reservation retained')
            output = max(usage.get('candidatesTokenCount', 0)+usage.get('thoughtsTokenCount', 0),
                         usage['totalTokenCount']-usage['promptTokenCount'])
            cost = (usage['promptTokenCount']*.75 + output*3.75)/1e6
            with self.locked():
                self.write_spend(self.read_spend()-reserve+cost)
            record['estimated_cost_usd'] = cost
            choices = raw.get('candidates', [])
            if not choices or choices[0].get('finishReason') != 'STOP':
                raise ValueError('Incomplete model output')
            result = ''.join(p.get('text', '') for p in choices[0].get('content', {}).get('parts', []) if not p.get('thought'))
            record['status'] = 'completed'
            return result
        except Exception as error:
            record.update(status='error', error_type=type(error).__name__)
            raise
        finally:
            record['elapsed_seconds'] = time.monotonic()-started
            path.write_text(json.dumps(record, indent=2))

class GeminiVideoVisionProvider(VisionProvider):
    name = 'gemini'
    def __init__(self, settings):
        self.client = BudgetClient(settings)

    def classify_window(self, frame_paths, recipe, window_index=0):
        try:
            parts = [{'inlineData': {'mimeType': 'image/jpeg', 'data': base64.b64encode(Path(p).read_bytes()).decode()}} for p in frame_paths]
            parts.append({'text': build_classification_prompt(recipe)})
            return parse_classification_json(self.client.generate(parts, json_output=True, metadata={'kind':'image_preflight','window_index':window_index}), recipe)
        except Exception as error:
            return Classification(confidence=0, reason=f'gemini error: {type(error).__name__}')

    def classify_video_window(self, video_path, window, recipe, window_index=0):
        try:
            start = max(0, window.start-2)
            duration = min(20, window.end-start+2)
            minimum = min(20, max(0, float(next((s.params.get('min_video_seconds', 0)
                          for s in recipe.scorer_signals() if s.type == 'vision_classify' and s.params), 0))))
            if duration < minimum:
                start = max(0, (window.start + window.end - minimum) / 2)
                duration = minimum
            with tempfile.TemporaryDirectory(prefix='hypereel-video-') as tmp:
                target = Path(tmp)/'clip.mp4'
                subprocess.run(['ffmpeg','-v','error','-nostdin','-ss',str(start),'-i',str(video_path),
                                '-t',str(duration),'-an','-c:v','libx264','-preset','ultrafast','-crf','20',str(target)],
                               check=True, capture_output=True, timeout=60)
                data = target.read_bytes()
            if len(data)>19_000_000:
                raise ValueError('Candidate exceeds inline media limit')
            prompt = build_classification_prompt(recipe)
            prompt += (f'\nYou are receiving continuous video, not sparse still images. Clip00:00 is source{start}s. '
                       f'The candidate action interval is [{window.start},{window.end}] source seconds. '
                       'Use surrounding video to verify the complete action. Classify the central action, not every frame. '
                       'For rebounds determine shooting and controlling teams; a rebound is permitted when present in the rubric.')
            parts = [{'inlineData': {'mimeType':'video/mp4','data':base64.b64encode(data).decode()}, 'videoMetadata':{'fps':4}}, {'text':prompt}]
            raw = self.client.generate(parts, json_output=True, metadata={'kind':'native_video', 'window_index':window_index,
                          'window':window.model_dump(), 'video_sha256':hashlib.sha256(data).hexdigest(), 'source_start':start,'duration':duration,'fps':4})
            return parse_classification_json(raw, recipe)
        except Exception as error:
            return Classification(confidence=0, reason=f'gemini error: {type(error).__name__}')

class GeminiVideoLLMProvider(LLMProvider):
    name = 'gemini'
    def __init__(self, settings):
        self.client = BudgetClient(settings)
    def generate(self, prompt, *, system='', max_tokens=800):
        try:
            return self.client.generate([{'text':system+'\n\n'+prompt}], max_tokens=min(2048,max(1024,max_tokens)), metadata={'kind':'text'})
        except Exception:
            return ''
