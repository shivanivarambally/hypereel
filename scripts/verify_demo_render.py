"""Bounded real-media demo smoke test. No evaluation labels used for inference."""
from pathlib import Path
import json,uuid,subprocess
from datetime import datetime
from hypereel.config import get_settings
from hypereel.recipe import load_recipe
from hypereel.graph.build import build_graph
from hypereel.graph.state import new_state
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evals/iterations/demo-integration-029'
s=get_settings();s.vision_provider=s.llm_provider='gemini';s.gemini_native_video=True;s.gemini_model='gemini-3.8-flash';s.tracing_enabled=False;s.output_dir=str(ROOT/'output/demo-verified')
recipe=load_recipe(ROOT/'recipes/basketball_demo_video.yaml')
graph=build_graph(settings=s);config={'configurable':{'thread_id':'demo-verify-'+uuid.uuid4().hex}}
state=graph.invoke(new_state(str(ROOT/'downloads/east-bay-demo-excerpt-750-790.mp4'),recipe,max_duration=30,max_candidates=8),config)
def serial(value):
 if hasattr(value,'model_dump'):return value.model_dump(mode='json')
 raise TypeError(type(value).__name__)
(OUT/'pipeline-before-render.json').write_text(json.dumps(state,default=serial,indent=2))
clips=state.get('selected_clips',[]);print('Selected:',[serial(c) for c in clips],flush=True)
if not clips:raise RuntimeError('No real clips selected; demo not verified')
# User explicitly asked for actual demo clips; render locally, stop before delivery.
state=graph.invoke(None,config)
(OUT/'pipeline-after-render.json').write_text(json.dumps(state,default=serial,indent=2))
path=state.get('output_path');assert path and Path(path).suffix=='.mp4' and Path(path).exists(),state.get('notes')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',path]));assert any(x['codec_type']=='video' for x in probe['streams']);assert float(probe['format']['duration'])>0
(OUT/'render-verification.json').write_text(json.dumps({'time':datetime.now().astimezone().isoformat(),'output':path,'clips':[serial(c) for c in clips],'probe':probe,'holdout_used':False},indent=2));print('Verified real MP4:',path,probe['format']['duration'],flush=True)
