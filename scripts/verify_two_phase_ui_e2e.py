"""Continue fresh real inference through the actual Streamlit approval and graph render.

Reuses completed W2 classification from 038; judge and summary calls are live.
Clicks local render approval for this test only, never the share button.
"""
import json
import argparse
import subprocess
from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'evals/iterations/two-phase-e2e-038'

SCRIPT = '''
import json
from pathlib import Path
from dataclasses import replace
import streamlit as st
from hypereel.app import _render_gate1, _render_gate2, _values
from hypereel.config import get_settings
from hypereel.graph.build import build_graph
from hypereel.graph.state import new_state
from hypereel.models import Recipe, CandidateWindow, Classification, PotentialEvent
from hypereel.analyze.two_phase import build_review_queue

root = Path.cwd()
out = root/'evals/iterations/two-phase-e2e-__ITERATION__'
if 'e2e_ready' not in st.session_state:
    report = json.loads((out/'report.json').read_text())
    case = next(c for c in report['cases'] if c['index']==__WINDOW__)
    if (out/'review-routing.json').exists():
        routing = json.loads((out/'review-routing.json').read_text())
        current_route = next(c for c in routing['cases'] if c['index']==__WINDOW__)
        case['arms']['two_phase']['classifications'] = [current_route['classification']]
        case['arms']['two_phase']['review_queue'] = current_route['review_queue']
    recipe = Recipe.model_validate(case['recipe'])
    recipe.id = 'two_phase_e2e___ITERATION___w__WINDOW_____ARTIFACT__'
    recipe.selection.max_duration = 15
    source = root/case['clip']
    window = CandidateWindow(start=case['core'][0]-case['source_offset'],
                             end=case['core'][1]-case['source_offset'])
    settings = replace(get_settings(), vision_provider='gemini', llm_provider='gemini',
        gemini_native_video=True, gemini_model='gemini-3.8-flash', tracing_enabled=False,
        two_phase_verification=True, output_dir=str(out/'render'))
    app = build_graph(settings=settings)
    config = {'configurable': {'thread_id': 'two-phase-038-ui'}}
    state = new_state(str(source), recipe, max_duration=15)
    import subprocess
    duration = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
        'format=duration', '-of', 'default=nw=1:nk=1', str(source)], text=True))
    event_windows = [CandidateWindow.model_validate(w) for w in
        case['arms']['two_phase'].get('candidates', [window.model_dump()])]
    state.update(video_path=str(source), video_duration=duration, candidates=event_windows,
       classifications=[Classification.model_validate(c) for c in case['arms']['two_phase']['classifications']],
       review_queue=[PotentialEvent.model_validate(q) for q in case['arms']['two_phase']['review_queue']])
    if 'candidates' in case['arms']['two_phase']:
        state['review_queue'] = build_review_queue(event_windows, state['classifications'])
    app.update_state(config, state, as_node='classify')
    st.session_state.current = _values(app.invoke(None, config))
    st.session_state.app = app
    st.session_state.config = config
    st.session_state.recipe = recipe
    st.session_state.stage = 'gate1'
    st.session_state.e2e_ready = True
if st.session_state.stage == 'gate1':
    _render_gate1(st)
else:
    _render_gate2(st)
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--iteration', default='038')
    parser.add_argument('--window', type=int, default=2)
    parser.add_argument('--simulate-confirm-potential', action='store_true')
    parser.add_argument('--artifact', default='render')
    parser.add_argument('--correct-potential-label')
    args = parser.parse_args()
    directory = ROOT/f'evals/iterations/two-phase-e2e-{args.iteration}'
    name = 'ui-potential-e2e' if args.simulate_confirm_potential else 'ui-e2e'
    if args.artifact != 'render': name += '-'+args.artifact
    target = directory/(name+'.json')
    if target.exists(): raise FileExistsError(target)
    script = SCRIPT.replace('__ITERATION__', args.iteration).replace('__WINDOW__', str(args.window)).replace('__ARTIFACT__', args.artifact)
    app = AppTest.from_string(script, default_timeout=180).run()
    if app.exception: raise RuntimeError(str(app.exception))
    graph = app.session_state['app']; config = app.session_state['config']
    assert graph.get_state(config).next == ('approve_clips',)
    before = app.session_state['current']
    assert not before.get('output_path')
    if args.simulate_confirm_potential:
        assert before['review_queue'] and not before['selected_clips']
        assert next(b for b in app.button if b.label == 'Approve & Render').disabled
        if args.correct_potential_label:
            app.selectbox[0].select('Correct label').run()
            app.text_input[0].set_value(args.correct_potential_label).run()
        else:
            app.selectbox[0].select('Confirm').run()
        assert not app.exception
    else:
        assert before['selected_clips']
    button = next(b for b in app.button if b.label == 'Approve & Render')
    assert not button.disabled
    button.click().run(timeout=180)
    if app.exception: raise RuntimeError(str(app.exception))
    after = app.session_state['current']
    assert after['proposed_duration'] == sum(c.duration for c in after['selected_clips'])
    assert app.session_state['stage'] == 'gate2'
    assert graph.get_state(config).next == ('approve_share',)
    output = Path(after['output_path'])
    assert output.suffix == '.mp4' and output.is_file()
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
        'format=duration,size', '-of', 'json', str(output)], text=True))
    assert float(probe['format']['duration']) > 0
    assert len(app.get('video')) >= 1 and app.get('download_button')
    assert not after.get('shared')
    saved_report = json.loads((directory/'report.json').read_text())
    inference_iteration = saved_report.get('inference_reused_from', args.iteration)
    record = dict(status='passed', inference_source=f'live {inference_iteration} W{args.window} classifications; pipeline replay {args.iteration}',
       simulated_review=args.simulate_confirm_potential,
       review_is_ground_truth=False,
       simulated_corrected_label=args.correct_potential_label,
       review_queue=[q.model_dump() for q in after.get('review_queue', [])],
       initial_gate='approve_clips', final_gate='approve_share', output_path=str(output),
       selected_clips=[c.model_dump() for c in after['selected_clips']],
       proposed_duration=after['proposed_duration'],
       summary=after.get('summary'), ffprobe=probe, download_visible=True, shared=False,
       notes=after['notes'])
    target.write_text(json.dumps(record, indent=2))
    print(json.dumps(record, indent=2))


if __name__ == '__main__': main()
