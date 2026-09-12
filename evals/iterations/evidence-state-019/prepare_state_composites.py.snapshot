"""019 compatibility: each image represents one instant, same canvas in both arms."""
import json,cv2
from pathlib import Path
from run_evidence_pilot import ROOT,sha,now
OUT=ROOT/'evals/iterations/evidence-state-019';OUT.mkdir(exist_ok=False);(OUT/'media').mkdir()
d=json.loads((ROOT/'evals/iterations/evidence-state-018/preparation.json').read_text());s=json.loads((ROOT/'evals/iterations/evidence-pilot-013/prepared.json').read_text())
def packed(wide,crop,path):
 import numpy as np
 im=cv2.imread(str(ROOT/wide['path']));canvas=np.zeros((432,1088,3),dtype=np.uint8);canvas[:im.shape[0],:768]=im
 if crop:canvas[:320,768:]=cv2.imread(str(ROOT/crop['path']))
 cv2.imwrite(str(path),canvas,[cv2.IMWRITE_JPEG_QUALITY,85]);return dict(path=str(path.relative_to(ROOT)),sha256=sha(path))
for w in d['windows']:
 for j,f in enumerate(w['frames']):f['wide']=packed(f['wide'],f.get('crop'),OUT/f'media/w{w["index"]}-dense-{j}.jpg');f.pop('crop',None)
 sw=next(x for x in s['windows'] if x['index']==w['index'])
 w['sparse_frames']=[dict(time=f['time'],wide=packed(f['wide'],None,OUT/f'media/w{w["index"]}-sparse-{j}.jpg')) for j,f in enumerate(sw['sparse_frames'])]
d['composite_policy']='One1088x432 image per timestamp:768wide left, optional320native rim crop right. Baseline same canvas, empty right. No upscaling. Internal provider resizing unknown.'
d['created_at']=now();(OUT/'preparation.json').write_text(json.dumps(d,indent=2))
