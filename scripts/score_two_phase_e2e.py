"""Score actual production classifications without injecting reference labels into inference.

Production returns one label/window with no event timestamp or structured team.
This therefore reports window label coverage, not timestamped event accuracy.
Only independently adjudicated label families are scored; others stay unknown.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFS = {1: ['free_throw_made'], 2: ['steal', 'two_point_made'], 3: [],
        4: ['free_throw_miss'], 5: ['block', 'missed_field_goal']}
SHOT_LABELS = {'free_throw_made', 'free_throw_miss', 'two_point_made', 'two_point_miss',
               'three_point_made', 'three_point_miss', 'made_field_goal', 'missed_field_goal'}

# --- Label families -------------------------------------------------------
# The emitted taxonomy contains overlapping labels, so exact string equality
# understates accuracy. Two relationships are credited:
#
#   subsumption  a generic label covers its specific children, in either
#                direction. Predicting `two_point_miss` against a reference of
#                `missed_field_goal` is a correct, more specific answer; the
#                reverse is a correct but vaguer one.
#   alias        two labels describe the same event from opposite sides. A
#                steal always creates a turnover, so a model emitting both is
#                describing one event twice, not inventing a second.
#
# Exact matches are assigned before family matches so a specific prediction is
# never consumed by a generic reference that some other prediction needed.
SUBTYPES = {
    'made_field_goal': {'two_point_made', 'three_point_made'},
    'missed_field_goal': {'two_point_miss', 'three_point_miss'},
}
ALIAS_GROUPS = [{'steal', 'turnover'}]


def labels_match(pred: str, ref: str) -> bool:
    """True when ``pred`` should be credited against ``ref``."""
    if pred == ref:
        return True
    if pred in SUBTYPES.get(ref, ()) or ref in SUBTYPES.get(pred, ()):
        return True
    return any(pred in group and ref in group for group in ALIAS_GROUPS)


def assign(refs: list[str], preds: list[str]) -> tuple[list[tuple[str, str]], list[str], list[str]]:
    """Greedy one-to-one assignment of predictions to references.

    Returns ``(pairs, unmatched_preds, unmatched_refs)`` where each pair is
    ``(reference_label, predicted_label)``. Exact equality is assigned in a
    first sweep, family relationships in a second.
    """
    open_refs, open_preds, pairs = list(refs), list(preds), []
    for exact_only in (True, False):
        for pred in list(open_preds):
            for ref in list(open_refs):
                hit = (pred == ref) if exact_only else labels_match(pred, ref)
                if hit:
                    pairs.append((ref, pred))
                    open_refs.remove(ref)
                    open_preds.remove(pred)
                    break
    return pairs, open_preds, open_refs
ADJUDICATED = {
    1: SHOT_LABELS,
    2: SHOT_LABELS | {'steal'},
    3: None,
    4: SHOT_LABELS,
    5: {'block', 'missed_field_goal', 'two_point_miss', 'three_point_miss',
        'made_field_goal', 'two_point_made', 'three_point_made'},
}


def metrics(tp, fp, fn):
    return dict(tp=tp, fp=fp, fn=fn, precision=tp/(tp+fp) if tp+fp else None,
                recall=tp/(tp+fn) if tp+fn else None,
                f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None)


def stage_labels(row, stage):
    arms = row['arms']
    if stage == 'selected':
        clips = arms['two_phase']['selected_clips']
        return [label for c in clips for label in
                ([e['moment_type'] for e in c['events']] if c.get('events')
                 else [c['moment_type']]) if label]
    if stage == 'single_pass':
        return [c['moment_type'] for c in arms[stage]['classifications'] if c['moment_type']]
    results = arms['two_phase']['classifications']
    if stage == 'discovery':
        return [c.get('phase1_moment_type') or c['moment_type'] for c in results
                if c.get('phase1_moment_type') or c['moment_type']]
    if stage == 'confirmed':
        return [c['moment_type'] for c in results if c['decision'] == 'confirmed' and c['moment_type']]
    if stage == 'confirmed_plus_potential':
        return [c['moment_type'] for c in results if c['decision'] in {'confirmed', 'potential_event'} and c['moment_type']]
    raise ValueError(stage)


def score(rows, stage):
    per_class = {}
    windows = []
    for row in rows:
        index = row['index']
        if index not in REFS:
            continue
        labels = stage_labels(row, stage)
        ignored = [label for label in labels if ADJUDICATED[index] is not None and label not in ADJUDICATED[index]]
        predicted = [label for label in labels if label not in ignored]

        pairs, false_pos, false_neg = assign(REFS[index], predicted)
        for ref, _pred in pairs:
            per_class.setdefault(ref, [0, 0, 0])[0] += 1
        for label in false_pos:
            per_class.setdefault(label, [0, 0, 0])[1] += 1
        for label in false_neg:
            per_class.setdefault(label, [0, 0, 0])[2] += 1
        t, f, n = len(pairs), len(false_pos), len(false_neg)

        windows.append(dict(index=index, predictions=labels, unadjudicated_predictions=ignored,
                            matched=[{'reference': r, 'predicted': p} for r, p in pairs],
                            inexact=[{'reference': r, 'predicted': p} for r, p in pairs if r != p],
                            false_positives=false_pos, false_negatives=false_neg,
                            **metrics(t, f, n)))
    sums = [sum(c[i] for c in per_class.values()) for i in range(3)]
    return dict(overall=metrics(*sums), per_class={k: metrics(*v) for k,v in sorted(per_class.items())},
                windows=windows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--iteration', default='038')
    parser.add_argument('--out', default='metrics.json',
                        help='filename written inside the iteration directory')
    parser.add_argument('--force', action='store_true',
                        help='overwrite an existing output file')
    args = parser.parse_args()
    directory = ROOT/f'evals/iterations/two-phase-e2e-{args.iteration}'
    report = json.loads((directory/'report.json').read_text())
    if report['status'] != 'completed': raise ValueError('Run incomplete')
    rows = report['cases']
    stages = {stage: score(rows, stage) for stage in
              ['single_pass', 'discovery', 'confirmed', 'confirmed_plus_potential', 'selected']}
    result = dict(
        scope='W1-W5; 6 reviewed positive labels and confirmed-negative W3; fixed window label coverage',
        stages=stages,
        decisions=dict(Counter(c['decision'] or 'unclassified'
                               for row in rows for c in row['arms']['two_phase']['classifications'])),
        new_provider_calls=0 if report.get('inference_reused_from') else sum(len(arm['calls']) for row in rows for name, arm in row['arms'].items()
                               if not (name == 'single_pass' and row.get('baseline_reused_from'))),
        provider_errors=[dict(index=row['index'], arm=name, reason=result['reason'])
                         for row in rows for name, arm in row['arms'].items()
                         for result in arm['classifications']
                         if 'error:' in (result['reason']+' '+result['verification_reason']).lower()],
        limitations=[
            'Single-pass control is the frozen single-label production baseline, not a multi-event single-pass ablation.',
            'These metrics measure window label coverage only; timestamp/team correctness requires separate scoring.',
            'W6 overlapping shot events and W7 unaudited timestamp are qualitative, outside primary score.',
            'Unadjudicated extra predictions ignored for both arms, so precision is conditional.',
            'Confirmed-plus-potential measures retained candidate coverage, not final human-reviewed accuracy.',
            'Six positive labels across two development games is too small for generalized claims.',
            'Labels are matched by family, not string equality: generic/specific shot labels credit '
            'each other and steal/turnover are treated as one event. Per-window "inexact" lists every '
            'match that was not exact, so family credit can be audited.',
            'The "confirmed" stage excludes items routed to human review, so a correctly flagged '
            'uncertain event scores as a miss. "confirmed_plus_potential" is the honest measure of '
            'what the system produced; "confirmed" measures only what it was willing to auto-accept.',
        ])
    target = directory/args.out
    if target.exists() and not args.force: raise FileExistsError(target)
    target.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
