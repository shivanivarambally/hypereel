"""Separate interval-support audit; never treat approximate human intervals as exact anchors."""
import argparse
import json
from pathlib import Path

from hypereel.evaluation.metrics import _maximum_matching
from score_two_phase_e2e import ADJUDICATED, metrics

ROOT = Path(__file__).resolve().parents[1]


def canonical(index, label):
    return 'missed_field_goal' if index == 5 and label in {'two_point_miss','three_point_miss'} else label


def score(rows, references, stage, tolerance):
    windows = []
    for row in rows:
        index = row['index']
        if index not in ADJUDICATED:
            continue
        refs = references[f'W{index}']['observations']
        preds = []
        for event in row['arms']['two_phase']['classifications']:
            if stage == 'confirmed' and event['decision'] != 'confirmed':
                continue
            if stage == 'retained' and event['decision'] not in {'confirmed','potential_event'}:
                continue
            label = event.get('phase1_moment_type') if stage == 'discovery' else event['moment_type']
            timestamp = event.get('phase1_event_time') if stage == 'discovery' else event.get('event_time')
            if not label or (ADJUDICATED[index] is not None and label not in ADJUDICATED[index]):
                continue
            preds.append(dict(label=canonical(index,label), source_time=None if timestamp is None
                              else timestamp+row['source_offset']))
        edges = [[j for j, ref in enumerate(refs) if pred['source_time'] is not None
                  and pred['label'] == ref['label']
                  and ref['start']-tolerance <= pred['source_time'] <= ref['end']+tolerance]
                 for pred in preds]
        matches = _maximum_matching(edges)
        windows.append(dict(index=index, predictions=preds, matched_pairs=matches,
                            **metrics(len(matches),len(preds)-len(matches),len(refs)-len(matches))))
    return dict(overall=metrics(*(sum(w[k] for w in windows) for k in ('tp','fp','fn'))),windows=windows)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--iteration', required=True)
    args = parser.parse_args()
    directory = ROOT/f'evals/iterations/two-phase-e2e-{args.iteration}'
    report = json.loads((directory/'report.json').read_text())
    if report['status'] != 'completed': raise ValueError('Incomplete run')
    refs = json.loads((ROOT/'evals/golden/revisions/development-human-review-v1.json').read_text())
    refs = {r['window_id']:r for r in refs['windows']}
    result = dict(scope='W1-W5 partially adjudicated, conditional precision; approximate human intervals',
        stages={stage:{str(t):score(report['cases'],refs,stage,t) for t in (0,2,5)}
                for stage in ('discovery','confirmed','retained')},
        limitations=['Interval containment is not exact timestamp error or video-grounding proof.',
                     '0/2/5-second tolerance sweep was specified before scoring.',
                     'Teams and W6/W7 require further independent adjudication.',
                     'Single-pass baseline lacks timestamps; no paired timestamp-improvement claim.'])
    target = directory/'temporal-support.json'
    if target.exists(): raise FileExistsError(target)
    target.write_text(json.dumps(result,indent=2))
    print(json.dumps({s:{t:v['overall'] for t,v in values.items()} for s,values in result['stages'].items()},indent=2))


if __name__ == '__main__': main()
