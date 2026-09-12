"""Prepare fixed pilot frames and local YOLO ball-candidate crops; no cloud calls."""
from pathlib import Path
import hashlib,json,os,time,subprocess,threading
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evals/iterations/evidence-pilot-013'
os.environ['YOLO_CONFIG_DIR']=str(ROOT/'work/ultralytics-pilot')
import cv2
import torch
import psutil
from ultralytics import YOLO

def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def now():return datetime.now().astimezone().isoformat()
def note(s):
 with (ROOT/'evals/IMPLEMENTATION_NOTES.md').open('a') as f:f.write('\n### '+now()+' — pilot013 preparation\n\n'+s+'\n')
def encoded(im,path,edge=768):
 h,w=im.shape[:2];scale=min(1,edge/max(h,w))
 if scale<1:im=cv2.resize(im,(round(w*scale),round(h*scale)),interpolation=cv2.INTER_AREA)
 if not cv2.imwrite(str(path),im,[cv2.IMWRITE_JPEG_QUALITY,85]):raise RuntimeError('JPEG write failed')
 return {'path':str(path.relative_to(ROOT)),'sha256':sha(path),'width':im.shape[1],'height':im.shape[0]}
def main():
 media=OUT/'media';media.mkdir(exist_ok=False)
 fixture=json.loads((ROOT/'evals/experiments/all-events-v2/diagnostic-009.json').read_text())
 baseline=json.loads((ROOT/'evals/iterations/ollama-all-events-010/report.json').read_text())
 if set(fixture['source_files']) != {'east-bay-elite-vs-spartans','unlimited-vs-campus'}:raise ValueError('Invalid allowlist')
 for g,p in fixture['source_files'].items():
  if sha(ROOT/p)!=baseline['source_sha256'][g]:raise ValueError('Source drift')
 torch.set_num_threads(4)
 result={'started_at':now(),'status':'running','source_sha256':baseline['source_sha256'],'windows':[],'memory':[],'detector':{'name':'yolo11n','device':'cpu','imgsz':1280,'confidence':.20,'classes':[0,32],'threads':4},'script_sha256':sha(__file__)}
 start=time.monotonic();stop=threading.Event()
 def monitor():
  while not stop.is_set():
   sample={'elapsed':time.monotonic()-start,'rss_bytes':psutil.Process().memory_info().rss,'pressure':int(subprocess.check_output(['sysctl','-n','kern.memorystatus_vm_pressure_level'],text=True))}
   result['memory'].append(sample)
   with (OUT/'detector-memory.jsonl').open('a') as f:f.write(json.dumps(sample)+'\n')
   stop.wait(.5)
 monitor_thread=threading.Thread(target=monitor,daemon=True);monitor_thread.start()
 try:
  weights=ROOT/'work/yolo11n.pt';weights.parent.mkdir(exist_ok=True)
  model=YOLO(str(weights));result['weights_sha256']=sha(weights)
  if model.names[0]!='person' or model.names[32]!='sports ball':raise ValueError('Wrong detector class names')
  for i,w in enumerate(fixture['windows']):
   cap=cv2.VideoCapture(str(ROOT/fixture['source_files'][w['game_id']]))
   fps=cap.get(cv2.CAP_PROP_FPS);lo=max(0,w['start']-2);hi=w['end']+2
   if fps<=0:raise ValueError('Invalid video FPS')
   entry={'index':i,'window':w,'frames':[],'sparse_frames':[]}
   for j in range(12):
    t=lo+j*(hi-lo)/11;frame_index=int(t*fps);cap.set(cv2.CAP_PROP_POS_FRAMES,frame_index);ok,im=cap.read()
    if not ok:raise RuntimeError('Frame read failed')
    d=model.predict(im,imgsz=1280,conf=.20,classes=[0,32],device='cpu',verbose=False,max_det=100)[0]
    boxes=[{'class_id':int(c),'confidence':float(s),'xyxy':[float(x) for x in b]} for b,s,c in zip(d.boxes.xyxy.tolist(),d.boxes.conf.tolist(),d.boxes.cls.tolist())]
    frame={'time':t,'actual_time':frame_index/fps,'frame_index':frame_index,'wide':encoded(im,media/f'w{i}-dense{j}.jpg'),'detections':boxes}
    balls=[b for b in boxes if b['class_id']==32]
    if balls:
     ball=max(balls,key=lambda b:b['confidence']);x1,y1,x2,y2=ball['xyxy'];h,width=im.shape[:2];size=min(512,h,width)
     left=max(0,min(width-size,round((x1+x2-size)/2)));top=max(0,min(h-size,round((y1+y2-size)/2)))
     frame['crop']=encoded(im[top:top+size,left:left+size],media/f'w{i}-crop{j}.jpg')
     frame['crop'].update(source_box=[left,top,left+size,top+size],candidate=ball)
    entry['frames'].append(frame)
   for j in range(6):
    t=lo+j*(hi-lo)/5;fi=int(t*fps);cap.set(cv2.CAP_PROP_POS_FRAMES,fi);ok,im=cap.read()
    if not ok:raise RuntimeError('Sparse frame read failed')
    entry['sparse_frames'].append({'time':t,'actual_time':fi/fps,'wide':encoded(im,media/f'w{i}-sparse{j}.jpg')})
   cap.release();result['windows'].append(entry)
   (OUT/'prepared.json').write_text(json.dumps(result,indent=2)+'\n')
   count=sum('crop'in f for f in entry['frames']);note(f'Window{i}:12dense+6sparse wide images prepared;ballcandidate crops={count}/12. All boxes/confidences retained. Candidate frequency is not measured ballrecall.')
   print(json.dumps({'window':i,'ball_candidate_frames':count}),flush=True)
  result['status']='completed'
 except BaseException as e:
  result['status']='failed';result['error_type']=type(e).__name__;note('Preparation failed '+type(e).__name__);raise
 finally:
  stop.set();monitor_thread.join(2);result['elapsed_seconds']=time.monotonic()-start;result['peak_sampled_rss_gib']=max((x['rss_bytes'] for x in result['memory']),default=0)/2**30
  (OUT/'prepared.json').write_text(json.dumps(result,indent=2)+'\n');note('Preparation final '+json.dumps({k:result.get(k) for k in ['status','elapsed_seconds','peak_sampled_rss_gib','error_type']}))
if __name__=='__main__':main()
