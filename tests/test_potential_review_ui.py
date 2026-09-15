"""Exercise the actual approval form, including the queue-only empty reel case."""
from streamlit.testing.v1 import AppTest


def screen(tmp_path):
    source = tmp_path / 'video.mp4'
    source.write_bytes(b'UI fixture, not inference media')
    return AppTest.from_string(f'''
import streamlit as st
from hypereel.app import _render_gate1
from hypereel.models import PotentialEvent
st.session_state.recipe = None
st.session_state.current = {{"video_path": {str(source)!r}, "selected_clips": [],
 "review_queue": [PotentialEvent(candidate_index=2, start=3, end=9, proposed_label="block",
 confidence=.4, uncertainty_reason="Contact occluded", expert_review_required=True)]}}
_render_gate1(st)
''').run()


def test_pending_event_requires_explicit_confirmation(tmp_path):
    app = screen(tmp_path)
    assert not app.exception
    assert app.button[0].disabled
    assert app.get('video')[0].proto.start_time == 3
    app.selectbox[0].select('Confirm').run()
    assert not app.exception
    assert not app.button[0].disabled
    app.selectbox[0].select('Reject').run()
    assert app.button[0].disabled


def test_correct_label_can_be_reviewed_when_no_auto_clips(tmp_path):
    app = screen(tmp_path)
    app.selectbox[0].select('Correct label').run()
    app.text_input[0].set_value('missed_field_goal').run()
    assert not app.exception
    assert not app.button[0].disabled
