"""Build an additive, development-only all-event reference ledger.

This is not a legacy highlight-pipeline fixture: the latter has a single-label
output and cannot faithfully score multiple basketball events in one window.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAMES = ('east-bay-elite-vs-spartans', 'unlimited-vs-campus')
SHOT_TYPES = {'2PT': 'two_point', '3PT': 'three_point', 'FT': 'free_throw'}
EVENT_TYPES = {'TOV': 'turnover', 'DR': 'defensive_rebound', 'OR': 'offensive_rebound',
               'STL': 'steal', 'BLK': 'block', 'AST': 'assist'}
CLASSES = tuple(sorted([f'{kind}_{outcome}' for kind in SHOT_TYPES.values()
                        for outcome in ('made', 'miss')] + list(EVENT_TYPES.values())))


def event_label(event):
    source_type = event['event_type']
    if source_type in SHOT_TYPES:
        outcome = event.get('outcome')
        if outcome not in ('made', 'miss'):
            raise ValueError(f'Unmapped shot outcome: {source_type}/{outcome}')
        return f'{SHOT_TYPES[source_type]}_{outcome}'
    if source_type not in EVENT_TYPES:
        raise ValueError(f'Unmapped event type: {source_type}')
    return EVENT_TYPES[source_type]


def build(root=ROOT):
    rows, games = [], []
    for game in GAMES:
        source = root / 'evals/golden/source' / f'{game}.external-labels.json'
        data = json.loads(source.read_text())
        counts = Counter()
        for event in data['events']:
            label = event_label(event)
            counts[label] += 1
            rows.append({'reference_id': f'{game}:{event["event_id"]}',
                         'dataset_version': 'basketball-all-events-development-v2',
                         'split': 'development', 'game_id': game, 'label': label,
                         'source_event_type': event['event_type'],
                         'source_outcome': event.get('outcome'),
                         'source_timestamp_seconds': event['timestamp_seconds'],
                         'timestamp_semantics': 'external_clip_timestamp_unverified',
                         'action_start_seconds': None, 'action_end_seconds': None,
                         'team': event.get('team'), 'player_name': event.get('player_name'),
                         'jersey_number': event.get('jersey_number')})
        games.append({'game_id': game, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                      'event_count': len(data['events']),
                      'counts_by_type': {label: counts[label] for label in CLASSES}})
    ids = [row['reference_id'] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate reference IDs')
    pooled = Counter(row['label'] for row in rows)
    manifest = {'version': 'basketball-all-events-development-v2', 'split': 'development',
                'purpose': 'all-event recognition, independent of highlight selection',
                'classes': list(CLASSES), 'event_count': len(rows),
                'counts_by_type': {label: pooled[label] for label in CLASSES}, 'games': games,
                'status': 'reference_inventory_ready; multi-event_detector_and_timing_audit_required',
                'scoring_plan': {
                    'primary': 'unweighted macro F1 across supported event types',
                    'also_report': ['per-type TP/FP/FN, precision, recall, F1 and support',
                                    'micro precision/recall/F1', 'worst-type recall',
                                    'duplicate rate', 'background false positives per observed minute',
                                    'proposal recall and detection recall before highlight selection'],
                    'zero_predictions_with_positive_support': 'precision undefined; recall 0; F1 0',
                    'no_reference_support': 'not measured for recall/F1; never a passing class',
                    'release_gate': 'macro F1 >=0.7 AND per-type precision and recall >=0.7 with adequate support; otherwise fail or insufficient evidence',
                    'matching': 'one-to-one, same-label temporal match; tolerance/IoU policy frozen after timing audit',
                    'paired_events': 'a possession change may contain both steal and turnover; retain each reference separately',
                    'confidence': 'per-prediction model confidence is separate from evaluation quality and statistical uncertainty'},
                'sampling_plan': {
                    'diagnostic': 'freeze examples stratified by all 12 types across both games; declare label-informed sampling',
                    'validation': 'freeze continuous source-time intervals; score every reference inside, including repeated events and negatives; source-driven proposals',
                    'rare_types': 'report available support and insufficient evidence; never infer reliability from one example'},
                'holdout_used': False}
    return rows, manifest


def main():
    rows, manifest = build()
    destination = ROOT / 'evals/experiments/all-events-v2'
    destination.mkdir(parents=True, exist_ok=True)
    ledger = ''.join(json.dumps(row, sort_keys=True) + '\n' for row in rows)
    manifest['ledger_sha256'] = hashlib.sha256(ledger.encode()).hexdigest()
    (destination / 'references.jsonl').write_text(ledger)
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'event_count': len(rows), 'counts_by_type': manifest['counts_by_type']}, indent=2))


if __name__ == '__main__':
    main()
