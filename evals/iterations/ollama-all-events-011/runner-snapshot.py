"""Bounded, serial development-only all-event evaluation with durable evidence."""
from pathlib import Path
import argparse,hashlib,json,subprocess,tempfile,time,threading
from datetime import datetime
from hypereel.config import Settings
from hypereel.analyze.classifier import extract_frames
from hypereel.models import CandidateWindow
from hypereel.evaluation.basketball_events import OllamaEventDetector,score_events
from hypereel.observability import provider_budget_scope

ROOT=Path(__file__).resolve().parents[1]

def digest(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def now():return datetime.now().astimezone().isoformat()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--iteration',required=True,choices=['009','010','011']);ap.add_argument('--frames',type=int,choices=[4,6],default=4);ap.add_argument('--variant',choices=['direct','evidence_first','observations'],default='direct');args=ap.parse_args()
 name=f'ollama-all-events-{args.iteration}';out=ROOT/'evals/iterations'/name;out.mkdir(exist_ok=False)
 fixture_path=ROOT/'evals/experiments/all-events-v2/diagnostic-009.json';fixture=json.loads(fixture_path.read_text())
 if args.iteration == '011':
  if args.variant != 'observations' or args.frames != 6:raise ValueError('011 requires six-frame observations diagnostic')
  fixture['windows']=[fixture['windows'][i] for i in [1,6]]
  fixture['selection'] += '; 011 post-result explanatory subset: original windows1 and6, one per game; not a whole-batch comparison'
 refs=[json.loads(l) for l in (ROOT/'evals/experiments/all-events-v2/references.jsonl').read_text().splitlines()]
 sources=fixture['source_files'];assert set(sources)=={'east-bay-elite-vs-spartans','unlimited-vs-campus'}
 expected={'east-bay-elite-vs-spartans':'9ad93efe89b26265ed354c32d3fcc844ce06376b4f0ef577c121047463f7750a','unlimited-vs-campus':'5d0c2bcc274bb7335e3aa42817855484ea5c25ca0e01d9f4ccfb1d926017e1b2'}
 for game,path in sources.items():assert digest(ROOT/path)==expected[game]
 model=json.loads(subprocess.check_output(['curl','--noproxy','*','-sf','http://127.0.0.1:11434/api/tags'],text=True))
 assert any(m['name']=='qwen3-vl:4b-instruct' and m['digest']=='ee4b975b58c17ce268cd19d40db35d5edc64603035d2ffc1fee1968eb0947f7b' for m in model['models'])
 settings=Settings(ollama_num_ctx=8192,ollama_num_predict=768,ollama_num_batch=128,ollama_image_max_edge=768,ollama_timeout_seconds=180,max_provider_calls=len(fixture['windows']),provider_checkpoint_dir=str(out/'checkpoints'))
 record={'name':name,'started_at':now(),'status':'running','fixture_sha256':digest(fixture_path),'references_sha256':digest(ROOT/'evals/experiments/all-events-v2/references.jsonl'),'source_sha256':expected,'model':'qwen3-vl:4b-instruct','model_digest':'ee4b975b58c17ce268cd19d40db35d5edc64603035d2ffc1fee1968eb0947f7b','settings':{'frames':args.frames,'edge':768,'context':8192,'output_limit':768,'batch':128,'timeout':180,'temperature':0,'seed':0,'prompt_variant':args.variant},'code_sha256':{p:digest(ROOT/p) for p in ['scripts/eval_all_events_local.py','src/hypereel/evaluation/basketball_events.py','src/hypereel/providers/ollama.py']},'windows':[],'memory_samples':[],'holdout_used':False,'sampling_note':fixture['selection'],'reference_timing':'provisional clip timestamps; 5s point tolerance; no action IoU claim'}
 def save():
  temp=out/'report.tmp';temp.write_text(json.dumps(record,indent=2)+'\n');temp.replace(out/'report.json')
 def note(text):
  with (ROOT/'evals/IMPLEMENTATION_NOTES.md').open('a') as f:f.write('\n### '+now()+' — '+name+'\n\n'+text+'\n')
 note('STARTED: '+json.dumps({k:v for k,v in record.items() if k not in ['windows','memory_samples']})+'. Frozen diagnostic subset; exact windows,reference support and measured types in report; annotation-empty controls not human-verified. No highlight selector or metadata judge. Memory pressure observed only; stop actual failure; no automatic retries.')
 start=time.monotonic();stop=threading.Event()
 def monitor():
  while not stop.is_set():
   try:
    rss=sum(int(l.strip().split(None,1)[0]) for l in subprocess.check_output(['ps','-axo','rss=,comm='],text=True).splitlines() if 'llama-server' in l)
    sample={'at':now(),'elapsed_seconds':time.monotonic()-start,'llama_rss_kib':rss,'pressure':int(subprocess.check_output(['sysctl','-n','kern.memorystatus_vm_pressure_level'],text=True)),'swap':subprocess.check_output(['sysctl','-n','vm.swapusage'],text=True).strip()};record['memory_samples'].append(sample)
    with (out/'memory.jsonl').open('a') as f:f.write(json.dumps(sample)+'\n')
   except Exception as e:
    record['memory_monitor_error']=type(e).__name__;break
   stop.wait(2)
 thread=threading.Thread(target=monitor,daemon=True);thread.start();save()
 budget=None
 try:
  with provider_budget_scope(settings,checkpoint_context={k:v for k,v in record.items() if k not in ['windows','memory_samples']}) as budget:
   record['checkpoint_path']=budget['checkpoint_path'];detector=OllamaEventDetector(settings)
   for i,w in enumerate(fixture['windows']):
    times=[w['start']+i*(w['end']-w['start'])/(args.frames-1) for i in range(args.frames)]
    with tempfile.TemporaryDirectory() as tmp:
     paths=extract_frames(str(ROOT/sources[w['game_id']]),CandidateWindow(start=w['start'],end=w['end']),args.frames,tmp)
     if len(paths)!=args.frames:raise ValueError('Incomplete frame extraction')
     budget['journal'].append('event_window_started',window_index=i,window=w,frame_times=times)
     raw,events=detector.detect(paths,times,args.variant,on_response=lambda raw:budget['journal'].append('raw_event_response',window_index=i,raw=raw))
    predictions=[dict(e.model_dump(),game_id=w['game_id']) for e in events]
    result={'index':i,'window':w,'frame_times':times,'events':predictions,'raw':raw}
    budget['journal'].append('event_window_finished',**result);record['windows'].append(result);record['provider_usage']=budget['calls'];save()
    print(json.dumps({'window':i,'game':w['game_id'],'events':predictions}),flush=True)
    note(f'Window{i} completed; source[{w["start"]},{w["end"]}],game={w["game_id"]},events='+json.dumps(predictions)+'. Durable raw response,usage and timestamps saved.')
  record['status']='completed'
 except BaseException as e:
  record['status']='failed_or_interrupted';record['error_type']=type(e).__name__
  note('STOPPED actual exception '+type(e).__name__+'. Checkpoint retains completed windows and raw response when received. Unfinished windows are unprocessed, not evidence of absent events.')
 finally:
  stop.set();thread.join(timeout=5);record['elapsed_seconds']=time.monotonic()-start;record['ended_at']=now()
  if budget is not None:record['provider_usage']=budget['calls'];record['attempted_calls']=budget['attempted_calls']
  selected_ids={rid for x in record['windows'] for rid in x['window']['reference_ids']}
  scored_refs=[dict(r,time_seconds=r['source_timestamp_seconds']) for r in refs if r['reference_id'] in selected_ids]
  preds=[p for x in record['windows'] for p in x['events']]
  record['scored_references']=scored_refs;record['metrics']=score_events(scored_refs,preds)
  record['per_game_metrics']={g:score_events([r for r in scored_refs if r['game_id']==g],[p for p in preds if p['game_id']==g]) for g in sources}
  record['completed_windows']=len(record['windows']);record['planned_windows']=len(fixture['windows']);record['peak_sampled_llama_rss_gib']=max((m['llama_rss_kib'] for m in record['memory_samples']),default=0)/1048576
  save();summary={k:record.get(k) for k in ['name','status','elapsed_seconds','attempted_calls','completed_windows','planned_windows','peak_sampled_llama_rss_gib','error_type']};summary.update({k:record['metrics'][k] for k in ['tp','fp','fn','macro_f1','micro_f1','measured_types']})
  note('FINAL '+json.dumps(summary)+'. Point matching is provisional; support is small,greedy label-informed coverage is not generalization. Full evidence report.json,checkpoints,memory.jsonl. No holdout/cloud inference. No quality gate pass inferred from completion.')
  for file in ['iteration-log.md','all-events-history.jsonl']:
   with (ROOT/'evals/iterations'/file).open('a') as f:f.write(('\n### '+now()+' '+name+'\n\n' if file.endswith('.md') else '')+json.dumps(summary)+'\n')
  print(json.dumps(summary),flush=True)
 return 0 if record['status']=='completed' else 1

if __name__=='__main__':raise SystemExit(main())
