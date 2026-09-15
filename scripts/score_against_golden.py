"""Score recorded two-phase runs against the full golden set, not the hand-adjudicated subset.

`evals/golden/golden_events.jsonl` holds 462 source-annotated events covering both
development games. It was built for *highlight selection*, so `expected_moment_type`
is populated only for the four reel-worthy labels and is null for the other 362 rows
(a miss or a turnover is an explicit negative for a highlight reel). That is why the
existing scorer fell back to a six-label hand-adjudicated subset.

For *all-event detection* the information is all there: `source_event_type` plus
`source_outcome` map onto the fourteen-label taxonomy exactly. This scorer uses that
mapping, which raises the reference set inside the seven recorded windows from 6 to
14 and brings W6 and W7 into scope for the first time.

Consumes recorded predictions only. No inference, no spend.

Boundary caveat: every golden row carries `boundary_status: provisional`, with
action bounds derived as event_time-5s/+4s. Matching is therefore by window
membership, not by timestamp proximity — a prediction is credited if it names an
event the window genuinely contains.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import sys
sys.path.insert(0, str(ROOT / 'scripts'))
from score_two_phase_e2e import assign, metrics  # noqa: E402

GOLDEN = ROOT / 'evals/golden/golden_events.jsonl'

#: source feed -> detection taxonomy. Outcome disambiguates shots; the rest are
#: outcome-free event types.
SHOT_TYPES = {'2PT': ('two_point_made', 'two_point_miss'),
              '3PT': ('three_point_made', 'three_point_miss'),
              'FT': ('free_throw_made', 'free_throw_miss')}
PLAIN_TYPES = {'DR': 'defensive_rebound', 'OR': 'offensive_rebound', 'STL': 'steal',
               'TOV': 'turnover', 'AST': 'assist', 'BLK': 'block'}

#: Which game each recorded window belongs to.
GAME_BY_WINDOW = {1: 'east-bay-elite-vs-spartans', 2: 'east-bay-elite-vs-spartans'}
DEFAULT_GAME = 'unlimited-vs-campus'


def golden_label(row) -> str | None:
    kind, outcome = row['source_event_type'], row['source_outcome']
    if kind in SHOT_TYPES:
        made, missed = SHOT_TYPES[kind]
        if outcome == 'made':
            return made
        if outcome == 'miss':
            return missed
        return None
    return PLAIN_TYPES.get(kind)


def references_for(core, game, rows, boundary='inclusive') -> list[str]:
    labels = []
    for row in rows:
        if row['game_id'] != game:
            continue
        # Contiguous sweeps need half-open windows so boundary events count once.
        # Inclusive is retained solely for replaying older isolated-window reports.
        inside = (core[0] <= row['event_time'] < core[1] if boundary == 'half-open'
                  else core[0] <= row['event_time'] <= core[1])
        if inside:
            label = golden_label(row)
            if label:
                labels.append(label)
    return labels


def predictions_for(arm, stage) -> list[str]:
    results = arm['classifications']
    if stage == 'discovery':
        return [c.get('phase1_moment_type') or c['moment_type'] for c in results
                if c.get('phase1_moment_type') or c['moment_type']]
    if stage == 'confirmed':
        return [c['moment_type'] for c in results
                if c.get('decision') in (None, 'confirmed') and c['moment_type']]
    if stage == 'confirmed_plus_potential':
        return [c['moment_type'] for c in results
                if c.get('decision') in (None, 'confirmed', 'potential_event') and c['moment_type']]
    raise ValueError(stage)


def score(report, rows, stage, arm_name='two_phase', boundary='inclusive'):
    per_class: dict[str, list[int]] = {}
    windows = []
    for case in report['cases']:
        index = case['index']
        arm = case['arms'].get(arm_name)
        if arm is None:
            continue
        game = case.get('game_id') or report.get('game_id')
        if game is None:
            if index not in range(1, 8):
                raise ValueError('Non-legacy windows require explicit game_id')
            game = GAME_BY_WINDOW.get(index, DEFAULT_GAME)
        if game not in {DEFAULT_GAME, 'east-bay-elite-vs-spartans'}:
            raise ValueError('Only the two development games may be scored')
        refs = references_for(case['core'], game, rows, boundary)
        preds = predictions_for(arm, stage)
        pairs, false_pos, false_neg = assign(refs, preds)
        for ref, _p in pairs:
            per_class.setdefault(ref, [0, 0, 0])[0] += 1
        for label in false_pos:
            per_class.setdefault(label, [0, 0, 0])[1] += 1
        for label in false_neg:
            per_class.setdefault(label, [0, 0, 0])[2] += 1
        windows.append(dict(index=index, references=refs, predictions=preds,
                            matched=[{'reference': r, 'predicted': p} for r, p in pairs],
                            false_positives=false_pos, false_negatives=false_neg,
                            **metrics(len(pairs), len(false_pos), len(false_neg))))
    sums = [sum(c[i] for c in per_class.values()) for i in range(3)]
    return dict(overall=metrics(*sums),
                per_class={k: metrics(*v) for k, v in sorted(per_class.items())},
                windows=windows)


def main():
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--iterations', help='comma-separated, e.g. 045,046,050,053')
    source.add_argument('--report', type=Path, help='Saved development report, including a contiguous sweep')
    parser.add_argument('--boundary', choices=['inclusive', 'half-open'], default='inclusive')
    parser.add_argument('--out', default='golden-scored.json')
    args = parser.parse_args()
    rows = [json.loads(line) for line in GOLDEN.read_text().splitlines() if line.strip()]

    results = {}
    paths = ([args.report] if args.report else
             [ROOT/f'evals/iterations/two-phase-e2e-{x.strip()}/report.json'
              for x in args.iterations.split(',')])
    for path in paths:
        report = json.loads(path.read_text())
        if report.get('status') != 'completed':
            raise ValueError('Only completed reports may be scored')
        iteration = report['iteration']
        results[iteration] = {stage: score(report, rows, stage, boundary=args.boundary)
                              for stage in ('discovery', 'confirmed', 'confirmed_plus_potential')}

    payload = dict(
        source='evals/golden/golden_events.jsonl',
        golden_total=len(rows),
        scope='all-event detection; references derived from source_event_type + source_outcome',
        matching='window membership (golden boundaries are provisional, event_time-5s/+4s)',
        boundary=args.boundary,
        iterations=results,
        limitations=[
            'Golden rows are source-annotated and unverified for this project; only a small subset has human adjudication.',
            'Boundaries are provisional, so a prediction is credited for naming an event the window contains, not for timing it.',
            'Coverage depends on the supplied report; no full-game or holdout accuracy claim.',
        ])
    target = ROOT / 'evals/iterations' / args.out
    with target.open('x') as handle:
        handle.write(json.dumps(payload, indent=2))
    for iteration, stages in results.items():
        o = stages['discovery']['overall']
        print('%s discovery  %d/%d/%d  P=%s R=%s F1=%s' % (
            iteration, o['tp'], o['fp'], o['fn'],
            '%.2f' % o['precision'] if o['precision'] is not None else '-',
            '%.2f' % o['recall'] if o['recall'] is not None else '-',
            '%.3f' % o['f1'] if o['f1'] is not None else '-'))
    print('written:', target)


if __name__ == '__main__':
    main()
