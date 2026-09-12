"""Video-only template calibration for018; no event labels used for ROI selection."""
from pathlib import Path
import cv2,json
from run_evidence_pilot import ROOT,sha,now
OUT=ROOT/'evals/iterations/evidence-state-018'
p=OUT/'preparation.json';d=json.loads(p.read_text())
# Manually located backboards from source images, never from HoopIQ event locations.
specs=[('east-bay','media/w1-native-0.jpg',(714,46,840,148)),('campus','media/w6-native-28.jpg',(419,144,562,261))]
templates={}
for name,file,(x1,y1,x2,y2) in specs:
 im=cv2.imread(str(OUT/file));templates[name]=cv2.cvtColor(im[y1:y2,x1:x2],cv2.COLOR_BGR2GRAY)
 cv2.imwrite(str(OUT/f'{name}-backboard-template.jpg'),im[y1:y2,x1:x2])
for w in d['windows']:
 template=templates['campus' if w['index']==6 else 'east-bay'];hits=0
 for j,f in enumerate(w['frames']):
  im=cv2.imread(str(ROOT/f['native']));gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY);best=(-1,None)
  for scale in [.65,.8,1.,1.2,1.4]:
   t=cv2.resize(template,None,fx=scale,fy=scale);res=cv2.matchTemplate(gray[:450],t,cv2.TM_CCOEFF_NORMED);_,val,_,loc=cv2.minMaxLoc(res)
   if val>best[0]:best=(val,(loc[0]+t.shape[1]//2,loc[1]+t.shape[0]//2))
  f['rim_match_score']=best[0]
  if best[0]>=.60:
   cx,cy=best[1];x=max(0,min(im.shape[1]-320,cx-160));y=max(0,min(im.shape[0]-320,cy-100));crop=im[y:y+320,x:x+320]
   path=OUT/f'media/w{w["index"]}-rim-{j}.jpg';cv2.imwrite(str(path),crop,[cv2.IMWRITE_JPEG_QUALITY,85])
   f['crop']=dict(path=str(path.relative_to(ROOT)),sha256=sha(path),bounds=[x,y,x+320,y+320],width=320,height=320);hits+=1
 print(w['index'],hits,'rim crop candidates /49')
d['rim_calibration']=dict(created_at=now(),specs=specs,threshold=.60,scales=[.65,.8,1.,1.2,1.4],crop_pixels=320,note='Video-only backboard templates; candidate crops not guaranteed correct. No player position/court homography implemented. No upscaling.');p.write_text(json.dumps(d,indent=2))
