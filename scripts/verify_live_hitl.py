"""Manual PAID live UI verification; requires explicit Gemini runtime env. Never run via pytest."""
from pathlib import Path
import json,time,subprocess
from datetime import datetime
from streamlit.testing.v1 import AppTest
root=Path(__file__).resolve().parents[1]
out=root/'evals/iterations/live-hitl-030'
app=AppTest.from_file(str(root/'src/hypereel/app.py'))
app.query_params['demo']='live-demo'
app.run(timeout=20)
assert not app.exception
start=time.time()
next(b for b in app.button if b.label=='Analyze game excerpt').click().run(timeout=180)
assert not app.exception
state=app.session_state.current
serial=lambda x:x.model_dump(mode='json') if hasattr(x,'model_dump') else str(x)
(out/'before-approval.json').write_text(json.dumps(state,default=serial,indent=2))
assert app.session_state.stage=='gate1'
assert state['selected_clips'],state.get('notes')
assert app.get('video')
assert not state.get('output_path'), 'Rendered before human approval!'
print('Fresh analysis paused for human review:',len(state['selected_clips']),'clips',flush=True)
next(b for b in app.button if b.label=='Approve & Render').click().run(timeout=180)
assert not app.exception
state=app.session_state.current
assert app.session_state.stage=='gate2'
assert app.get('video') and app.get('download_button')
path=state['output_path'];assert Path(path).is_file()
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-of','json',path]))
assert float(probe['format']['duration'])>0
(out/'after-approval.json').write_text(json.dumps(state,default=serial,indent=2))
(out/'verification.json').write_text(json.dumps({'timestamp':datetime.now().astimezone().isoformat(),'elapsed_seconds':time.time()-start,'output':path,'probe':probe,'fresh_inference':True,'approval_clicked_by_test':True,'share_clicked':False,'holdout_used':False},indent=2))
print('Fresh LIVE UI analysis → approval pause → render → video/download passed:',path,flush=True)
