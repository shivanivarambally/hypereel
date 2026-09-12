"""Replay frozen local evaluation inputs through the authorized Nebius model."""
from pathlib import Path
from datetime import datetime
import base64
import hashlib
import json
import shutil
import tempfile
import time

from openai import OpenAI
from hypereel.config import get_settings
from hypereel.analyze.classifier import extract_frames
from hypereel.models import CandidateWindow
from hypereel.evaluation.basketball_events import (
    OllamaEventDetector, build_prompt, build_observation_prompt,
    parse_events, parse_observed_events, score_events,
)
from hypereel.observability import (
    provider_budget_scope, authorize_provider_call, record_provider_usage,
)

ROOT = Path(__file__).resolve().parents[1]
MODEL = 'openbmb/MiniCPM-V-4_5'
BASELINES = ['009', '010', '011']


def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def now():
    return datetime.now().astimezone().isoformat()


def request_arguments(images, prompt):
    """Transport-only difference: the same JPEG bytes and text go to Nebius."""
    return dict(model=MODEL, temperature=0, seed=0, max_tokens=768,
                response_format={'type': 'json_object'},
                messages=[{'role': 'user', 'content': [
                    {'type': 'text', 'text': prompt},
                    *[{'type': 'image_url', 'image_url': {
                        'url': 'data:image/jpeg;base64,' + x}} for x in images],
                ]}])


def main():
    out = ROOT / 'evals/iterations/nebius-matched-012'
    out.mkdir(exist_ok=False)
    shutil.copy2(__file__, out / 'runner-snapshot.py')
    shutil.copy2(ROOT / 'src/hypereel/evaluation/basketball_events.py', out / 'detector-snapshot.py')
    settings = get_settings()
    settings.max_provider_calls = 18
    settings.max_provider_spend_usd = 5.0
    settings.provider_call_reserve_usd = .50
    settings.provider_spend_ledger_path = str(ROOT / 'evals/iterations/spend-ledger.json')
    settings.provider_checkpoint_dir = str(out / 'checkpoints')
    # Preserve historical conservative ledger rates; do not claim invoice pricing.
    settings.nebius_input_cost_per_million_usd = 10.0
    settings.nebius_output_cost_per_million_usd = 30.0
    settings.ollama_image_max_edge = 768
    encoder = OllamaEventDetector(settings)  # encoding only; no Ollama calls
    record = dict(name='nebius-matched-012', started_at=now(), status='preflight',
                  model=MODEL, baseline_ids=BASELINES, windows=[], planned_calls=18,
                  holdout_used=False, authorization='User explicitly requested Nebius MiniCPM comparison',
                  prompt_policy='Exact baseline prompt; no reference labels sent',
                  transport=dict(temperature=0, seed=0, max_tokens=768, json_mode=True,
                                 timeout_seconds=180, retries=0),
                  spend_policy=dict(cumulative_ceiling_usd=5, reservation_per_call_usd=.5,
                                    input_rate_per_million=10, output_rate_per_million=30,
                                    note='Conservative historical accounting estimates, not verified invoice pricing'),
                  differences=['Provider/model and internal tokenizer/image processing',
                               'Nebius server context/precision not controlled by Ollama options'],
                  code_sha256={str(p): digest(ROOT / p) for p in [
                      'scripts/eval_nebius_matched.py', 'src/hypereel/evaluation/basketball_events.py']})

    def save():
        tmp = out / 'report.tmp'
        tmp.write_text(json.dumps(record, indent=2) + '\n')
        tmp.replace(out / 'report.json')

    def note(message):
        with (ROOT / 'evals/IMPLEMENTATION_NOTES.md').open('a') as f:
            f.write('\n### ' + now() + ' — nebius-matched-012\n\n' + message + '\n')

    note('STARTED matched replay of009/010/011. User authorizes Nebius cloud inference for this comparison, superseding earlier local-only constraint for this run. Same cached source bytes,encoded JPEGs,prompt text,ordered timestamps,reference IDs,output cap,temperature,seed and scorer. No YOLO change or label editing. Max18 serial calls,no retries,existing$5 estimated-spend ceiling. Guard against silently using configured Qwen: explicit MiniCPM model ID. Preflight and raw completions retained; stop on actual failure.')
    started = time.monotonic()
    budget = None
    baselines = {}
    try:
        if not settings.nebius_api_key:
            raise ValueError('Nebius credential missing')
        if settings.nebius_base_url.rstrip('/') != 'https://api.studio.nebius.com/v1':
            raise ValueError('Unexpected Nebius endpoint')
        ledger = json.loads(Path(settings.provider_spend_ledger_path).read_text())
        if not 0 <= ledger['estimated_spend_usd'] < 5:
            raise ValueError('Invalid or exhausted spend ledger')
        record['spend_before_usd'] = ledger['estimated_spend_usd']
        client = OpenAI(api_key=settings.nebius_api_key, base_url=settings.nebius_base_url,
                        max_retries=0, timeout=180)
        matches = [m.model_dump() for m in client.models.list().data if m.id == MODEL]
        if len(matches) != 1:
            raise ValueError('Requested model unavailable')
        record['model_metadata'] = matches[0]
        fixture_path = ROOT / 'evals/experiments/all-events-v2/diagnostic-009.json'
        fixture = json.loads(fixture_path.read_text())
        if set(fixture['source_files']) != {'east-bay-elite-vs-spartans', 'unlimited-vs-campus'}:
            raise ValueError('Development source allowlist mismatch')
        current_refs = digest(ROOT / 'evals/experiments/all-events-v2/references.jsonl')
        for n in BASELINES:
            folder = ROOT / f'evals/iterations/ollama-all-events-{n}'
            b = json.loads((folder / 'report.json').read_text())
            if b['status'] != 'completed' or b['references_sha256'] != current_refs or b['fixture_sha256'] != digest(fixture_path):
                raise ValueError('Baseline reference/fixture drift')
            for game, sha in b['source_sha256'].items():
                if digest(ROOT / fixture['source_files'][game]) != sha:
                    raise ValueError('Source drift')
            # Use immutable snapshot to prove current prompt and scorer have not changed.
            import importlib.util
            spec = importlib.util.spec_from_file_location('hypereel.evaluation.frozen_' + n, folder / 'detector-snapshot.py')
            frozen = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(frozen)
            for w in b['windows']:
                t = w['frame_times']
                variant = b['settings']['prompt_variant']
                expected = frozen.build_observation_prompt(t) if variant == 'observations' else frozen.build_prompt(t, variant)
                actual = build_observation_prompt(t) if variant == 'observations' else build_prompt(t, variant)
                if expected != actual:
                    raise ValueError('Prompt drift')
            original_preds = [e for w in b['windows'] for e in w['events']]
            if score_events(b['scored_references'], original_preds) != b['metrics']:
                raise ValueError('Scoring drift')
            baselines[n] = b
        record['baseline_sha256'] = {n: digest(ROOT / f'evals/iterations/ollama-all-events-{n}/report.json') for n in BASELINES}
        record['source_sha256'] = baselines['009']['source_sha256']
        record['references_sha256'] = current_refs
        record['status'] = 'running'
        save()
        with provider_budget_scope(settings, checkpoint_context={k: v for k, v in record.items() if k != 'windows'}) as budget:
            for n, b in baselines.items():
                # 011 uses original010 window1 and6, with identical images.
                audit_n = '010' if n == '011' else n
                audit = json.loads((ROOT / f'evals/iterations/ollama-all-events-{audit_n}/input-image-audit.json').read_text())
                for w in b['windows']:
                    index = w['index']
                    source_index = [1, 6][index] if n == '011' else index
                    times = w['frame_times']
                    variant = b['settings']['prompt_variant']
                    prompt = build_observation_prompt(times) if variant == 'observations' else build_prompt(times, variant)
                    source_window = w['window']
                    with tempfile.TemporaryDirectory() as tmp:
                        paths = extract_frames(str(ROOT / fixture['source_files'][source_window['game_id']]),
                                               CandidateWindow(start=source_window['start'], end=source_window['end']), len(times), tmp)
                        images = encoder._images(paths)
                    hashes = [hashlib.sha256(base64.b64decode(x)).hexdigest() for x in images]
                    expected = [x['encoded_jpeg_sha256'] for x in audit['frames'] if x['window'] == source_index]
                    if hashes != expected:
                        raise ValueError('Encoded images differ from local baseline')
                    entry = dict(baseline=n, index=index, window=source_window, frame_times=times,
                                 prompt=prompt, prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
                                 image_sha256=hashes, status='started')
                    record['windows'].append(entry)
                    budget['journal'].append('matched_window_started', **entry)
                    save()
                    authorize_provider_call(provider='nebius', model=MODEL, operation='basketball_event_detection_v2')
                    call_start = time.monotonic()
                    try:
                        response = client.chat.completions.create(**request_arguments(images, prompt))
                    except Exception as exc:
                        # Unknown billable usage: retain a conservative reservation, never zero it.
                        call = budget['calls'][-1]
                        call.update(status='error', error_type=type(exc).__name__, http_status=getattr(exc, 'status_code', None),
                                    latency_seconds=time.monotonic()-call_start, usage_unknown=True,
                                    estimated_cost_usd=settings.provider_call_reserve_usd)
                        budget['estimated_spend_usd'] += settings.provider_call_reserve_usd
                        Path(settings.provider_spend_ledger_path).write_text(json.dumps({'estimated_spend_usd': budget['estimated_spend_before_run_usd'] + budget['estimated_spend_usd']})+'\n')
                        budget['journal'].append('call_failed', call=call)
                        raise
                    elapsed = time.monotonic() - call_start
                    # Raw completion is durable before strict parsing, including finish reason.
                    budget['journal'].append('raw_nebius_response', baseline=n, index=index, response=response.model_dump())
                    entry['raw_completion'] = response.model_dump()
                    if response.usage is None:
                        call = budget['calls'][-1]
                        call.update(status='usage_unknown', usage_unknown=True, estimated_cost_usd=settings.provider_call_reserve_usd)
                        budget['estimated_spend_usd'] += settings.provider_call_reserve_usd
                        Path(settings.provider_spend_ledger_path).write_text(json.dumps({'estimated_spend_usd': budget['estimated_spend_before_run_usd'] + budget['estimated_spend_usd']})+'\n')
                        budget['journal'].append('call_usage_unknown', call=call)
                        raise ValueError('Missing usage; do not continue paid inference')
                    record_provider_usage(response, status='success' if response.choices and response.choices[0].finish_reason == 'stop' else 'incomplete')
                    budget['calls'][-1]['latency_seconds'] = elapsed
                    entry['latency_seconds'] = elapsed
                    raw = response.choices[0].message.content or ''
                    entry['raw'] = raw
                    save()
                    if response.choices[0].finish_reason != 'stop':
                        raise ValueError('Incomplete model output')
                    events = parse_observed_events(raw, times) if variant == 'observations' else parse_events(raw, times[0], times[-1])
                    entry['events'] = [dict(e.model_dump(), game_id=source_window['game_id']) for e in events]
                    entry['status'] = 'completed'
                    budget['journal'].append('matched_window_finished', **entry)
                    record['provider_usage'] = budget['calls']
                    save()
                    note(f'Baseline{n},window{index} completed in{elapsed:.2f}s;events='+json.dumps(entry['events'])+'. Exact input/prompt parity verified; raw response and usage retained.')
                    print(json.dumps({'baseline': n, 'window': index, 'events': entry['events']}), flush=True)
        record['status'] = 'completed'
    except BaseException as exc:
        record['status'] = 'failed_or_interrupted'
        record['error_type'] = type(exc).__name__
        record['http_status'] = getattr(exc, 'status_code', None)
        note('STOPPED actual '+type(exc).__name__+'; raw responses and partial coverage retained. No automatic retry; unprocessed windows are not counted as negatives.')
    finally:
        record['ended_at'] = now()
        record['elapsed_seconds'] = time.monotonic() - started
        if budget is not None:
            record['provider_usage'] = budget['calls']
            record['attempted_calls'] = budget['attempted_calls']
            record['estimated_spend_usd'] = budget['estimated_spend_usd']
        record['comparisons'] = {}
        for n, b in baselines.items():
            done = [w for w in record['windows'] if w['baseline'] == n and w['status'] == 'completed']
            ids = {rid for w in done for rid in w['window']['reference_ids']}
            refs = [r for r in b['scored_references'] if r['reference_id'] in ids]
            preds = [e for w in done for e in w['events']]
            local_preds = [e for w in b['windows'] if w['index'] in {x['index'] for x in done} for e in w['events']]
            record['comparisons'][n] = dict(completed_windows=len(done), planned_windows=len(b['windows']),
                nebius=score_events(refs, preds), local_same_completed_subset=score_events(refs, local_preds),
                per_game={g: score_events([r for r in refs if r['game_id'] == g], [p for p in preds if p['game_id'] == g]) for g in b['source_sha256']})
        save()
        summary={k: record.get(k) for k in ['name','status','error_type','http_status','attempted_calls','elapsed_seconds','estimated_spend_usd']}
        summary['metrics'] = {n: {k:c['nebius'][k] for k in ['tp','fp','fn','micro_f1','macro_f1']} for n,c in record['comparisons'].items()}
        note('FINAL '+json.dumps(summary)+'. Same-input diagnostic comparison; provisional5s point timing,small label-informed support,no release pass or generalization claim.')
        for filename in ['iteration-log.md', 'all-events-history.jsonl']:
            with (ROOT / 'evals/iterations' / filename).open('a') as f:
                f.write(('\n### '+now()+' nebius-matched-012\n\n' if filename.endswith('.md') else '')+json.dumps(summary)+'\n')
        print(json.dumps(summary), flush=True)
    return 0 if record['status'] == 'completed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
