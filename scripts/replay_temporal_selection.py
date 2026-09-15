"""Zero-inference replay of frozen temporal outputs after selection bookkeeping fixes."""
import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from hypereel.analyze.two_phase import build_review_queue
from hypereel.graph.nodes import select_node
from hypereel.graph.state import new_state
from hypereel.models import CandidateWindow, Classification, Recipe

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-iteration', required=True)
    parser.add_argument('--iteration', required=True)
    args = parser.parse_args()
    out = ROOT/f'evals/iterations/two-phase-e2e-{args.iteration}'
    out.mkdir(exist_ok=False)
    report = json.loads((ROOT/f'evals/iterations/two-phase-e2e-{args.source_iteration}/report.json').read_text())
    if report['status'] != 'completed': raise ValueError('Incomplete source')
    report.update(iteration=args.iteration, inference_reused_from=args.source_iteration,
                  replayed_at=datetime.now(timezone.utc).isoformat(),
                  incremental_estimated_spend_usd=0)
    for row in report['cases']:
        arm = row['arms']['two_phase']
        recipe = Recipe.model_validate(row['recipe'])
        source = ROOT/row['clip']
        duration = float(subprocess.check_output(['ffprobe','-v','error','-show_entries',
            'format=duration','-of','default=nw=1:nk=1',str(source)],text=True))
        windows = [CandidateWindow.model_validate(w) for w in arm['candidates']]
        results = [Classification.model_validate(c) for c in arm['classifications']]
        state = new_state(str(source),recipe)
        state.update(video_path=str(source),video_duration=duration,candidates=windows,classifications=results)
        selected = select_node(state)
        arm.update(selected_clips=[c.model_dump() for c in selected['selected_clips']],
                   proposed_duration=selected['proposed_duration'],
                   review_queue=[q.model_dump() for q in build_review_queue(windows,results)])
    report['spend_before_usd'] = report['spend_after_usd']
    (out/'report.json').write_text(json.dumps(report,indent=2))
    print(f'Saved zero-provider-call replay {args.iteration}')


if __name__ == '__main__': main()
