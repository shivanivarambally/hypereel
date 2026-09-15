"""Replay only deterministic routing on captured live responses; zero inference."""
import argparse
import json
from pathlib import Path
from hypereel.analyze.two_phase import resolve, build_review_queue
from hypereel.models import CandidateWindow, Recipe
from hypereel.providers._util import parse_classification_json

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--iteration', default='039')
    args = parser.parse_args()
    directory = ROOT/f'evals/iterations/two-phase-e2e-{args.iteration}'
    report = json.loads((directory/'report.json').read_text())
    rows = []
    for row in report['cases']:
        arm = row['arms']['two_phase']; calls = arm['calls']
        recipe = Recipe.model_validate(row['recipe'])
        discovery = parse_classification_json(calls[0]['raw_text'], recipe, permissive=True)
        result = discovery
        if len(calls) == 2:
            verification = parse_classification_json(calls[1]['raw_text'], recipe)
            result = resolve(discovery, verification)
        window = CandidateWindow(start=row['core'][0]-row['source_offset'],
                                 end=row['core'][1]-row['source_offset'])
        rows.append(dict(index=row['index'], classification=result.model_dump(),
                         review_queue=[q.model_dump() for q in build_review_queue([window], [result])],
                         original_classification=arm['classifications'][0]))
    target = directory/'review-routing.json'
    if target.exists(): raise FileExistsError(target)
    target.write_text(json.dumps(dict(inference_calls=0, source='captured provider responses', cases=rows), indent=2))


if __name__ == '__main__': main()
