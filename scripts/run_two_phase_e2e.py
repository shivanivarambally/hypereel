"""Live production-provider comparison on fixed reviewed development windows.

Every arm uses classify_candidates, the real native-video adapter, and select_node.
Provider instrumentation records actual outputs; it never substitutes responses.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from hypereel.analyze.classifier import classify_moments, last_run_transitions
from hypereel.analyze.phase_transitions import transition_metrics
from hypereel.analyze.two_phase import build_review_queue
from hypereel.config import get_settings
from hypereel.evaluation.basketball_events import DEFINITIONS
from hypereel.graph.nodes import select_node
from hypereel.graph.state import new_state
from hypereel.models import CandidateWindow, Recipe
from hypereel.providers.gemini_video import GeminiVideoVisionProvider

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / 'evals/iterations/gemini-human-review-034/report.json'


def save(path, data):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data, indent=2))
    temp.replace(path)


def make_recipe(index, teams, verify=None):
    definitions = dict(DEFINITIONS, made_field_goal='A visibly made field goal with unknown point value.',
                       missed_field_goal='A visibly missed field goal with unknown point value.')
    return Recipe.model_validate({
        'id': f'two_phase_w{index}', 'name': 'All basketball events', 'domain': 'basketball',
        'moment_types': [{'name': key, 'description': value} for key, value in definitions.items()],
        'signals': [{'type': 'vision_classify', 'role': 'scorer', 'weight': 1}],
        'subject_selector': {'type': 'none', 'audience': 'team', 'description': teams},
        'verify_events': verify,
        'selection': {'min_score': 0.5, 'min_clip': 4, 'max_clip': 15, 'max_duration': 60,
                      'lead_in': 2, 'lead_out': 2},
    })


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--iteration', default='038')
    parser.add_argument('--baseline-iteration', help='Reuse that frozen single-pass control; rerun two-phase only')
    parser.add_argument('--fps', type=int, default=None,
                        help='Sampled frame rate for native-video calls (default: settings value, 4). '
                             'Raising this is the shot-outcome temporal-resolution experiment.')
    parser.add_argument('--discovery-only', action='store_true',
                        help='Skip the verification call; keep multi-event discovery. Halves cost.')
    parser.add_argument('--windows', default=None,
                        help='Comma-separated window indices to run, e.g. 1,4,5. Default: all.')
    args = parser.parse_args()
    out = ROOT / f'evals/iterations/two-phase-e2e-{args.iteration}'
    out.mkdir(exist_ok=False)
    settings = replace(get_settings(), vision_provider='gemini', llm_provider='gemini',
                       gemini_native_video=True, gemini_model='gemini-3.8-flash', tracing_enabled=False)
    if args.fps:
        settings = replace(settings, gemini_video_fps=args.fps)
    only = {int(x) for x in args.windows.split(',')} if args.windows else None
    if not settings.gemini_api_key:
        raise RuntimeError('Gemini API key missing')
    cases = json.loads(BASELINE.read_text())['calls']
    controls = {}
    if args.baseline_iteration:
        control_path = ROOT/f'evals/iterations/two-phase-e2e-{args.baseline_iteration}/report.json'
        control_report = json.loads(control_path.read_text())
        if control_report['status'] != 'completed': raise ValueError('Control incomplete')
        controls = {row['index']: row for row in control_report['cases']}
    ledger = ROOT / settings.provider_spend_ledger_path
    report = {'iteration': args.iteration, 'started_at': datetime.now(timezone.utc).isoformat(),
              'status': 'running', 'holdout_used': False,
              'scope': 'fixed reviewed development windows; temporal_events_v1 two-phase; no proposer recall claim',
              'gemini_video_fps': settings.gemini_video_fps,
              'windows_requested': sorted(only) if only else 'all',
              'discovery_only': bool(args.discovery_only),
              'spend_before_usd': json.loads(ledger.read_text())['estimated_spend_usd'], 'cases': []}
    save(out/'report.json', report)
    started = time.monotonic()
    try:
        for case in cases:
            index = case['index']
            if only is not None and index not in only:
                continue
            source = ROOT / case['clip']
            duration = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
                'format=duration', '-of', 'default=nw=1:nk=1', str(source)], text=True).strip())
            offset = case['source_start']
            window = CandidateWindow(start=case['core'][0]-offset, end=case['core'][1]-offset)
            teams = ('Both teams; East Bay Elite wears blue, Spartans black.' if index in (1, 2)
                     else 'Both teams; Campus wears yellow, Unlimited white.')
            recipe = make_recipe(index, teams, verify=False if args.discovery_only else None)
            row = {'index': index, 'clip': case['clip'], 'source_offset': offset,
                   'media_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                   'core': case['core'], 'recipe': recipe.model_dump(), 'arms': {}}
            report['cases'].append(row)
            arms = [('single_pass', False), ('two_phase', True)]
            if controls:
                control = controls[index]
                if control['media_sha256'] != row['media_sha256'] or control['core'] != row['core']:
                    raise ValueError('Control media/core differs')
                row['arms']['single_pass'] = control['arms']['single_pass']
                row['baseline_reused_from'] = args.baseline_iteration
                arms = [('two_phase', True)]
            for name, enabled in arms:
                arm_settings = replace(settings, two_phase_verification=enabled)
                provider = GeminiVideoVisionProvider(arm_settings)
                provider.client.logs = out/'provider-calls'
                calls = []
                original_generate = provider.client.generate

                def recorded_generate(parts, **kwargs):
                    metadata = dict(kwargs.get('metadata') or {}, iteration=args.iteration,
                                    window_id=f'W{index}', arm=name)
                    kwargs['metadata'] = metadata
                    raw = original_generate(parts, **kwargs)
                    calls.append({'metadata': metadata, 'raw_text': raw})
                    return raw

                provider.client.generate = recorded_generate
                event_windows, results = classify_moments([window], recipe, provider, arm_settings, str(source))
                transitions = [t.as_dict() for t in last_run_transitions]
                queue = build_review_queue(event_windows, results)
                state = new_state(str(source), recipe)
                state.update(video_path=str(source), video_duration=duration, candidates=event_windows,
                             classifications=results, review_queue=queue)
                selected = select_node(state)
                row['arms'][name] = {
                    'phase_transitions': transitions,
                    'transition_metrics': transition_metrics(last_run_transitions),
                    'candidates': [w.model_dump() for w in event_windows],
                    'calls': calls, 'classifications': [r.model_dump() for r in results],
                    'review_queue': [q.model_dump() for q in queue],
                    'selected_clips': [c.model_dump() for c in selected['selected_clips']],
                    'proposed_duration': selected['proposed_duration'],
                }
                save(out/'report.json', report)
                print(f"W{index} {name}: {[r.model_dump() for r in results]}", flush=True)
        report['status'] = 'completed'
    finally:
        report.update(elapsed_seconds=time.monotonic()-started,
                      ended_at=datetime.now(timezone.utc).isoformat(),
                      spend_after_usd=json.loads(ledger.read_text())['estimated_spend_usd'])
        report['incremental_estimated_spend_usd'] = report['spend_after_usd']-report['spend_before_usd']
        save(out/'report.json', report)


if __name__ == '__main__':
    main()
