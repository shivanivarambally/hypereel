"""020 native-frame YOLO+ByteTrack; reference-free observational transcript."""
from pathlib import Path
from datetime import datetime
from types import SimpleNamespace
import os,json,time,hashlib,collections,math
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evals/iterations/track-transcript-020'
os.environ['YOLO_CONFIG_DIR']=str(ROOT/'work/ultralytics-track-020');os.environ['YOLO_AUTOINSTALL']='false'
import cv2,torch,psutil
from ultralytics import YOLO
from ultralytics.trackers.byte_tracker import BYTETracker

def now():return datetime.now().astimezone().isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def note(s):
 with (ROOT/'evals/IMPLEMENTATION_NOTES.md').open('a') as f:f.write('\n### '+now()+' — track-transcript-020 preparation\n\n'+s+'\n')
def run():
 if (OUT/'tracking.json').exists():raise FileExistsError('No overwrite')
 fixture=json.loads((ROOT/'evals/experiments/all-events-v2/diagnostic-009.json').read_text());base=json.loads((ROOT/'evals/iterations/evidence-pilot-013/prepared.json').read_text());assert set(fixture['source_files'])=={'east-bay-elite-vs-spartans','unlimited-vs-campus'}
 for g,p in fixture['source_files'].items():assert sha(ROOT/p)==base['source_sha256'][g]
 weights=ROOT/'work/yolo11n.pt';assert sha(weights)=='0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1'
 plan=dict(created_at=now(),indices=[1,2,6],sampling='Every native frame, source30/25fps,12seconds including2s context each side',detector='YOLO11n COCO,1280 input,CPU4threads,conf0.10,classes person0/sportsball32',tracker='Separate ByteTrack instance per class;high0.25,low0.10,new0.25,match0.8,buffer15 at30fps,fuse_score true; no ID sharing across classes/windows',
  transcript='One observational row per0.5second bin. Pick the longest consecutive observed ball-track run in that bin, confidence tie-break. Preserve no-ball bins. Nearest person is pixel-box proximity, never possession or team identity. Stable proximity requires0.3s consecutive observed same ball/person IDs. No interpolation, no labels or event-target coordinates.',
  limits='No basketball-specific fine-tuning, camera-motion compensation, jersey/team recognition or court calibration. Track IDs are local algorithm IDs, not verified player identities.',source_sha256=base['source_sha256'],weights_sha256=sha(weights))
 (OUT/'tracking-plan.json').write_text(json.dumps(plan,indent=2));note('START '+json.dumps(plan)+' Added lap0.5.12 only to isolated detector environment. Initial package inspection created default Ultralytics settings; actual run uses task-local YOLO_CONFIG_DIR. No cloud inference in this preparation stage.')
 torch.set_num_threads(4);model=YOLO(str(weights));result=dict(status='running',started_at=now(),plan=plan,windows=[]);start=time.monotonic();peak=0
 try:
  for idx in [1,2,6]:
   w=fixture['windows'][idx];cap=cv2.VideoCapture(str(ROOT/fixture['source_files'][w['game_id']]));fps=cap.get(cv2.CAP_PROP_FPS);lo=w['start']-2;count=round(12*fps)+1;cap.set(cv2.CAP_PROP_POS_FRAMES,round(lo*fps))
   cfg=SimpleNamespace(track_high_thresh=.25,track_low_thresh=.10,new_track_thresh=.25,track_buffer=15,match_thresh=.8,fuse_score=True)
   trackers={c:BYTETracker(cfg,frame_rate=round(fps)) for c in [0,32]};rows=[];runs={};proximity={};maxrun=0;maxprox=0;ids=set();jumps=0;previouscenters={};ts=time.monotonic()
   for j in range(count):
    ok,im=cap.read()
    if not ok:raise RuntimeError('Source decode failure')
    t=lo+j/fps;det=model.predict(im,imgsz=1280,conf=.10,classes=[0,32],device='cpu',verbose=False,max_det=100)[0];tracked={}
    raw=[dict(class_id=int(c),confidence=float(s),xyxy=b) for b,s,c in zip(det.boxes.xyxy.tolist(),det.boxes.conf.tolist(),det.boxes.cls.tolist())]
    for c in [0,32]:
     boxes=det.boxes[det.boxes.cls==c].cpu().numpy();arr=trackers[c].update(boxes,im);tracked[c]=[dict(id=f'{c}:{int(a[4])}',box=[float(x) for x in a[:4]],confidence=float(a[5])) for a in arr]
    current=set();currentprox=set();ballrows=[]
    for b in tracked[32]:
     bid=b['id'];ids.add(bid);current.add(bid);runs[bid]=runs.get(bid,0)+1;maxrun=max(maxrun,runs[bid]);cx=(b['box'][0]+b['box'][2])/2;cy=(b['box'][1]+b['box'][3])/2
     if bid in previouscenters and math.dist(previouscenters[bid],(cx,cy))>im.shape[1]*.25:jumps+=1
     previouscenters[bid]=(cx,cy);near=None
     for p in tracked[0]:
      x1,y1,x2,y2=p['box'];dist=math.hypot(max(x1-cx,0,cx-x2),max(y1-cy,0,cy-y2))/max(y2-y1,1)
      if near is None or dist<near['distance_player_heights']:near=dict(player_track=p['id'],distance_player_heights=dist,player_box=p['box'])
     if near and near['distance_player_heights']<=.15:
      pair=(bid,near['player_track']);currentprox.add(pair);proximity[pair]=proximity.get(pair,0)+1;maxprox=max(maxprox,proximity[pair]);near['consecutive_seconds']=(proximity[pair]-1)/fps
     else:near=None
     ballrows.append(dict(b,center=[cx,cy],consecutive_seconds=(runs[bid]-1)/fps,near_player=near))
    runs={k:v for k,v in runs.items() if k in current};proximity={k:v for k,v in proximity.items() if k in currentprox};previouscenters={k:v for k,v in previouscenters.items() if k in current}
    row=dict(time_seconds=t,frame_index=round(lo*fps)+j,raw_detections=raw,person_tracks=tracked[0],ball_tracks=ballrows);rows.append(row)
    with (OUT/f'w{idx}-tracks.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
    rss=psutil.Process().memory_info().rss;peak=max(peak,rss)
    if j%30==0:
     with (OUT/'memory.jsonl').open('a') as f:f.write(json.dumps(dict(timestamp=now(),index=idx,frame=j,rss_bytes=rss))+'\n')
    if j%120==0:print(idx,j,'/',count,flush=True)
   cap.release();obs=[]
   for bi in range(24):
    sub=[r for r in rows if lo+bi*.5<=r['time_seconds']<lo+(bi+1)*.5];candidates=[(r,b) for r in sub for b in r['ball_tracks']]
    if not candidates:
     text='No observed ball track in this half-second interval. Ball location, possession, and event outcome unknown.';t=lo+bi*.5
    else:
     r,b=max(candidates,key=lambda x:(x[1]['consecutive_seconds'],x[1]['confidence']));t=r['time_seconds'];near=b['near_player'];text=f"Candidate ball track {b['id']} at image pixel center ({b['center'][0]:.0f},{b['center'][1]:.0f}); continuously observed {b['consecutive_seconds']:.2f}s. "
     if near:text+=f"Nearest person track {near['player_track']} box {','.join(str(round(v)) for v in near['player_box'])}; proximity observed {near['consecutive_seconds']:.2f}s. "
     text+='Proximity is not possession; team, jersey, shot outcome and event cause unverified.'
    obs.append(dict(observation_id=f't{bi+1}',time_seconds=t,observation=text,visibility='uncertain'))
   stats=dict(frames=count,detected_ball_frames=sum(any(b['class_id']==32 for b in r['raw_detections']) for r in rows),tracked_ball_frames=sum(bool(r['ball_tracks']) for r in rows),unique_ball_track_ids=len(ids),longest_observed_ball_run_seconds=max(0,maxrun-1)/fps,longest_same_ball_person_proximity_seconds=max(0,maxprox-1)/fps,suspect_large_track_jumps=jumps,elapsed_seconds=time.monotonic()-ts,
    person_track_frames=sum(bool(r['person_tracks']) for r in rows),note='Availability/continuity, not ball recall, identity accuracy, or possession accuracy; no box ground truth.')
   entry=dict(index=idx,window=w,stats=stats,observations=obs,raw_tracks_sha256=sha(OUT/f'w{idx}-tracks.jsonl'));result['windows'].append(entry);note('TRACKING WINDOW COMPLETE '+json.dumps(entry));(OUT/'tracking-progress.json').write_text(json.dumps(result,indent=2));print(json.dumps(stats),flush=True)
  result['status']='completed'
 finally:
  result.update(ended_at=now(),elapsed_seconds=time.monotonic()-start,peak_sampled_rss_gib=peak/1024**3);(OUT/'tracking.json').write_text(json.dumps(result,indent=2));note('TRACKING FINAL '+json.dumps({k:v for k,v in result.items() if k not in ['windows','plan']}))
if __name__=='__main__':run()
