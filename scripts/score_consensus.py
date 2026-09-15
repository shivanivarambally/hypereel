"""Score a majority-vote ensemble over repeated identical two-phase runs.

Discovery output is non-deterministic: repeated runs of the same clip, prompt,
model and frame rate disagree on at least one event in most windows. Rather
than reporting whichever single run was sampled, this keeps a label only when it
appears in at least ``--threshold`` of the runs, which is the standard
self-consistency remedy for sampling variance.

Consumes recorded outputs only. No inference, no spend.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import sys
sys.path.insert(0, str(ROOT / 'scripts'))
from score_two_phase_e2e import REFS, ADJUDICATED, assign, metrics  # noqa: E402


def confirmed_labels(row) -> list[str]:
    """Labels the two-phase arm auto-accepted for this window."""
    return [c['moment_type'] for c in row['arms']['two_phase']['classifications']
            if c.get('decision') == 'confirmed' and c.get('moment_type')]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--iterations', required=True,
                        help='comma-separated iteration ids, e.g. 045,046,047,048')
    parser.add_argument('--threshold', type=float, default=0.5,
                        help='keep a label present in at least this fraction of runs')
    parser.add_argument('--out', default='consensus.json')
    args = parser.parse_args()

    ids = [x.strip() for x in args.iterations.split(',')]
    per_window: dict[int, list[list[str]]] = {}
    for iteration in ids:
        report = json.loads((ROOT / f'evals/iterations/two-phase-e2e-{iteration}/report.json').read_text())
        for row in report['cases']:
            per_window.setdefault(row['index'], []).append(confirmed_labels(row))

    need = args.threshold * len(ids)
    per_class: dict[str, list[int]] = {}
    windows = []
    for index in sorted(per_window):
        if index not in REFS:
            continue
        runs = per_window[index]
        # A window may legitimately contain the same label twice; vote on the
        # multiset by counting how many runs contained at least N copies.
        votes = Counter()
        for labels in runs:
            for label, n in Counter(labels).items():
                for k in range(1, n + 1):
                    votes[(label, k)] += 1
        consensus = [label for (label, _k), count in sorted(votes.items()) if count >= need]

        ignored = [l for l in consensus if ADJUDICATED[index] is not None and l not in ADJUDICATED[index]]
        predicted = [l for l in consensus if l not in ignored]
        pairs, fp, fn = assign(REFS[index], predicted)
        for ref, _p in pairs:
            per_class.setdefault(ref, [0, 0, 0])[0] += 1
        for label in fp:
            per_class.setdefault(label, [0, 0, 0])[1] += 1
        for label in fn:
            per_class.setdefault(label, [0, 0, 0])[2] += 1
        windows.append(dict(index=index, runs=[sorted(r) for r in runs], consensus=consensus,
                            unadjudicated=ignored, false_positives=fp, false_negatives=fn,
                            **metrics(len(pairs), len(fp), len(fn))))

    sums = [sum(c[i] for c in per_class.values()) for i in range(3)]
    result = dict(
        iterations=ids, runs=len(ids), threshold=args.threshold, votes_required=need,
        stage='confirmed (majority vote across runs)',
        overall=metrics(*sums),
        per_class={k: metrics(*v) for k, v in sorted(per_class.items())},
        windows=windows,
        limitations=[
            'Consensus over identical repeated runs; it reduces sampling variance, it does not add evidence.',
            'A label consistently wrong in every run survives the vote unchanged.',
            'Six positive labels; consensus cannot rescue a reference set this small.',
        ])
    target = ROOT / f'evals/iterations/{args.out}' if '/' in args.out else ROOT / 'evals/iterations' / args.out
    target.write_text(json.dumps(result, indent=2))
    print(json.dumps({k: result[k] for k in ('runs', 'votes_required', 'overall')}, indent=2))
    for w in windows:
        print('W%s consensus=%s FP=%s FN=%s' % (w['index'], w['consensus'], w['false_positives'], w['false_negatives']))


if __name__ == '__main__':
    main()
