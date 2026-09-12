"""Approval screens expose visual evidence and guard empty/unreviewable reels."""
from streamlit.testing.v1 import AppTest


def screen(tmp_path, gate, missing=False):
    media = tmp_path / 'reel.mp4'
    if not missing:
        media.write_bytes(b'preview media fixture')
    script = f'''
import streamlit as st
from hypereel.app import _render_gate1, _render_gate2
from hypereel.models import Clip
st.session_state.recipe = None
st.session_state.current = {{"video_path": {str(media)!r}, "output_path": {str(media)!r}, "selected_clips": [Clip(start=9, end=20.5, score=0.66, moment_type="layup_or_dunk", reason="Review this play")], "proposed_duration": 11.5}}
_render_{gate}(st)
'''
    result = AppTest.from_string(script).run()
    assert not result.exception
    return result


def test_clip_preview_boundaries_and_keep_control(tmp_path):
    app = screen(tmp_path, 'gate1')
    video = app.get('video')[0].proto
    assert video.start_time == 9
    assert video.end_time == 21  # Round outward so preview never cuts off the outcome.
    assert not app.button[0].disabled
    app.checkbox[0].uncheck().run()
    assert app.button[0].disabled


def test_missing_source_blocks_approval(tmp_path):
    app = screen(tmp_path, 'gate1', missing=True)
    assert app.error
    assert not app.get('video')
    assert app.button[0].disabled


def test_final_reel_player_and_download(tmp_path):
    app = screen(tmp_path, 'gate2')
    assert len(app.get('video')) == 1
    assert len(app.get('download_button')) == 1
    assert not app.button[0].disabled


def test_missing_render_blocks_share(tmp_path):
    app = screen(tmp_path, 'gate2', missing=True)
    assert app.error
    assert app.button[0].disabled
