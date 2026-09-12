from pathlib import Path
import json,cv2,subprocess
from PIL import Image,ImageDraw
from run_evidence_pilot import ROOT,sha,now
OUT=ROOT/'evals/iterations/evidence-state-018'
def main():
 fixture=json.loads((ROOT/'evals/experiments/all-events-v2/diagnostic-009.json').read_text());old=json.loads((ROOT/'evals/iterations/evidence-pilot-013/prepared.json').read_text())
 assert set(fixture['source_files'])==set(old['source_sha256'])=={'east-bay-elite-vs-spartans','unlimited-vs-campus'}
 for g,p in fixture['source_files'].items():assert sha(ROOT/p)==old['source_sha256'][g]
 result=dict(created_at=now(),source_sha256=old['source_sha256'],windows=[])
 for idx in [1,2,6]:
  w=fixture['windows'][idx];src=ROOT/fixture['source_files'][w['game_id']];start=w['start']-2;end=w['end']+2
  clip=OUT/f'media/w{idx}-continuous.mp4'
  subprocess.run(['ffmpeg','-v','error','-ss',str(start),'-i',str(src),'-t','12','-an','-c:v','libx264','-crf','18','-y',str(clip)],check=True)
  cap=cv2.VideoCapture(str(src));fps=cap.get(cv2.CAP_PROP_FPS);rows=[];sheet=Image.new('RGB',(1280,4*390),'white');draw=ImageDraw.Draw(sheet)
  for j in range(49):
   t=start+j*.25;fi=round(t*fps);cap.set(cv2.CAP_PROP_POS_FRAMES,fi);ok,im=cap.read();assert ok
   p=OUT/f'media/w{idx}-native-{j}.jpg';cv2.imwrite(str(p),im,[cv2.IMWRITE_JPEG_QUALITY,95])
   wp=OUT/f'media/w{idx}-wide-{j}.jpg';wide=cv2.resize(im,(768,round(im.shape[0]*768/im.shape[1])));cv2.imwrite(str(wp),wide,[cv2.IMWRITE_JPEG_QUALITY,85])
   rows.append(dict(time=t,actual_time=fi/fps,native=str(p.relative_to(ROOT)),wide=dict(path=str(wp.relative_to(ROOT)),sha256=sha(wp)),frame_index=fi))
   if j%4==0 and j<48:
    n=j//4;x=n%2*640;y=n//2*260
    pic=Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB));pic.thumbnail((640,235));sheet.paste(pic,(x,y+25));draw.text((x+8,y+5),str(t),fill='black')
  sheet.save(OUT/f'w{idx}-inspection.jpg');cap.release()
  result['windows'].append(dict(index=idx,window=w,frames=rows,fps=fps,clip=str(clip.relative_to(ROOT))))
 (OUT/'preparation.json').write_text(json.dumps(result,indent=2))
 print('Native frames, continuous clips and inspection sheets prepared.')
if __name__=='__main__':main()
