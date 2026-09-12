"""Three-arm, development-only input evidence pilot; strict budgets and notes."""
from pathlib import Path
from datetime import datetime
import json,base64,hashlib,time,shutil,subprocess,threading,os
from openai import OpenAI
from hypereel.config import get_settings
from hypereel.evaluation.basketball_events import build_prompt,parse_events,score_events
from hypereel.observability import provider_budget_scope,authorize_provider_call,record_provider_usage,ProviderBudgetExceeded
from eval_nebius_matched import request_arguments
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evals/iterations/evidence-pilot-013'
ARMS=['wide6_context','wide12_context','wide12_ball_crops']

def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def now():return datetime.now().astimezone().isoformat()
def note(s):
 with (ROOT/'evals/IMPLEMENTATION_NOTES.md').open('a') as f:f.write('\n### '+now()+' — evidence pilot013\n\n'+s+'\n')
def make_manifest(w,arm):
 frames=w['sparse_frames'] if arm=='wide6_context' else w['frames'];items=[]
 for f in frames:
  items.append(dict(f['wide'],time=f['time'],view='wide'))
  if arm=='wide12_ball_crops' and 'crop' in f:items.append(dict(f['crop'],time=f['time'],view='ball_candidate_crop'))
 return items

def pilot_prompt(w,items):
 times=[x['time'] for x in items];core=w['window']
 return build_prompt(times) + (f'\nEvaluation interval: [{core["start"]}, {core["end"]}] seconds. '
  'Images outside that interval provide context only; report events occurring inside it. '
  'Return at most12events. Multiple views at the same timestamp are the SAME instant,not separate events. '
  'A ball-candidate crop is an unverified detector suggestion,not proof of ball presence or an event. '
  'Do not emit one event per image; only distinct supported actions. Ordered image manifest: '+
  json.dumps([{'image':i+1,'time':x['time'],'view':x['view']} for i,x in enumerate(items)]))

def main():
 report_path=OUT/'report.json'
 if report_path.exists():raise FileExistsError('Pilot report already exists; no overwrite')
 prepared=json.loads((OUT/'prepared.json').read_text());plan=json.loads((OUT/'plan.json').read_text())
 if prepared['status']!='completed' or len(prepared['windows'])!=8:raise ValueError('Preparation incomplete')
 b=json.loads((ROOT/'evals/iterations/ollama-all-events-010/report.json').read_text())
 fixture=json.loads((ROOT/'evals/experiments/all-events-v2/diagnostic-009.json').read_text())
 if set(fixture['source_files'])!={'east-bay-elite-vs-spartans','unlimited-vs-campus'}:raise ValueError('Source allowlist')
 for g,p in fixture['source_files'].items():
  if sha(ROOT/p)!=prepared['source_sha256'][g]:raise ValueError('Source changed')
 if sha(ROOT/'evals/experiments/all-events-v2/references.jsonl')!=b['references_sha256']:raise ValueError('References changed')
 settings=get_settings();settings.max_provider_calls=24;settings.max_provider_spend_usd=5
 settings.provider_call_reserve_usd=.30;settings.nebius_input_cost_per_million_usd=10;settings.nebius_output_cost_per_million_usd=30
 settings.provider_spend_ledger_path=str(ROOT/'evals/iterations/spend-ledger.json');settings.provider_checkpoint_dir=str(OUT/'checkpoints')
 if settings.nebius_base_url.rstrip('/')!='https://api.studio.nebius.com/v1':raise ValueError('Unexpected endpoint')
 spent=json.loads(Path(settings.provider_spend_ledger_path).read_text())['estimated_spend_usd']
 if not 0<=spent<5:raise ValueError('Invalid or exhausted ledger')
 client=OpenAI(api_key=settings.nebius_api_key,base_url=settings.nebius_base_url,max_retries=0,timeout=180)
 record={'name':'evidence-pilot-013','status':'running','started_at':now(),'plan':plan,'plan_sha256':sha(OUT/'plan.json'),'prepared_sha256':sha(OUT/'prepared.json'),'source_sha256':prepared['source_sha256'],'reference_sha256':b['references_sha256'],'windows':[],'arms':{},'spend_before_usd':spent,'memory':[],'scored_references':b['scored_references'],'holdout_used':False,'script_sha256':sha(__file__)}
 for script in ['run_evidence_pilot.py','prepare_evidence_pilot.py']:shutil.copy2(ROOT/'scripts'/script,OUT/(script+'.snapshot'))
 shutil.copy2(ROOT/'src/hypereel/evaluation/basketball_events.py',OUT/'scorer.snapshot.py')
 def save():
  tmp=OUT/'report.tmp';tmp.write_text(json.dumps(record,indent=2)+'\n');tmp.replace(report_path)
 def reserve_unknown(budget,exc):
  call=budget['calls'][-1];call.update(status='error',error_type=type(exc).__name__,usage_unknown=True,estimated_cost_usd=.30)
  budget['estimated_spend_usd']+=.30
  p=Path(settings.provider_spend_ledger_path);tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps({'estimated_spend_usd':budget['estimated_spend_before_run_usd']+budget['estimated_spend_usd']})+'\n');tmp.replace(p)
  budget['journal'].append('unknown_usage_reserved',call=call)
 start=time.monotonic();stop=threading.Event()
 def monitor():
  while not stop.is_set():
   try:
    s={'elapsed':time.monotonic()-start,'rss_kib':int(subprocess.check_output(['ps','-o','rss=','-p',str(os.getpid())],text=True).strip()),'pressure':int(subprocess.check_output(['sysctl','-n','kern.memorystatus_vm_pressure_level'],text=True))}
    record['memory'].append(s)
    with (OUT/'cloud-client-memory.jsonl').open('a') as f:f.write(json.dumps(s)+'\n')
   except Exception:break
   stop.wait(1)
 thread=threading.Thread(target=monitor,daemon=True);thread.start();budget=None;save()
 note('Cloud arms START. Same eventmodel/promptpolicy/outputcap1536 acrossarms;2scontext with unchangedcore scoring. Baseline refreshed tocontrolcontext/promptchanges; old012retained,historicalonly. Detector process finished beforecloudstage. Up to24calls;no retries.')
 try:
  with provider_budget_scope(settings,checkpoint_context={'name':record['name'],'plan':plan}) as budget:
   for arm in ARMS:
    record['arms'][arm]={'status':'running'};arm_start=time.monotonic()
    try:
     for w in prepared['windows']:
      items=make_manifest(w,arm);prompt=pilot_prompt(w,items);images=[]
      for x in items:
       p=ROOT/x['path']
       if sha(p)!=x['sha256']:raise ValueError('Input image hash mismatch')
       images.append(base64.b64encode(p.read_bytes()).decode())
      entry={'arm':arm,'index':w['index'],'window':w['window'],'status':'started','manifest':items,'prompt':prompt,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest()}
      record['windows'].append(entry);save();budget['journal'].append('pilot_window_started',**entry)
      authorize_provider_call(provider='nebius',model='openbmb/MiniCPM-V-4_5',operation='evidence_pilot')
      call_start=time.monotonic()
      try:
       args=request_arguments(images,prompt);args['max_tokens']=1536
       response=client.chat.completions.create(**args)
      except Exception as exc:reserve_unknown(budget,exc);raise
      raw=response.model_dump();entry['raw_completion']=raw;entry['latency_seconds']=time.monotonic()-call_start
      budget['journal'].append('raw_response',arm=arm,index=w['index'],response=raw)
      if response.usage is None:
       reserve_unknown(budget,ValueError('Missing usage'));raise ValueError('Missing usage')
      record_provider_usage(response,status='success' if response.choices and response.choices[0].finish_reason=='stop' else 'incomplete')
      budget['calls'][-1]['latency_seconds']=entry['latency_seconds'];record['provider_usage']=budget['calls'];save()
      if not response.choices or response.choices[0].finish_reason!='stop':raise ValueError('Incomplete output')
      text=response.choices[0].message.content or '';entry['raw']=text
      events=[dict(e.model_dump(),game_id=w['window']['game_id']) for e in parse_events(text,min(x['time'] for x in items),max(x['time'] for x in items))]
      core=w['window'];entry['events']=[e for e in events if core['start']<=e['time_seconds']<=core['end']]
      entry['context_events']=[e for e in events if not core['start']<=e['time_seconds']<=core['end']]
      entry['status']='completed';budget['journal'].append('pilot_window_finished',**entry);save()
      note(f'{arm} window{w["index"]}:images={len(items)},coreevents='+json.dumps(entry['events'])+',context_events='+json.dumps(entry['context_events'])+f',latency={entry["latency_seconds"]:.2f}s. Raw response and image hashes retained.')
      print(json.dumps({'arm':arm,'window':w['index'],'events':entry['events']}),flush=True)
     record['arms'][arm]['status']='completed'
    except Exception as exc:
     record['arms'][arm].update(status='failed',error_type=type(exc).__name__)
     if record['windows'] and record['windows'][-1]['status']=='started':record['windows'][-1].update(status='failed',error_type=type(exc).__name__)
     note(f'{arm} stopped on {type(exc).__name__}; no retry. Other input arms are separate experiments. Raw response retained when received.')
     if isinstance(exc,ProviderBudgetExceeded):raise
    finally:
     record['arms'][arm]['elapsed_seconds']=time.monotonic()-arm_start;save()
  record['status']='completed' if all(x['status']=='completed' for x in record['arms'].values()) else 'completed_with_arm_failures'
 except BaseException as exc:
  record.update(status='failed_or_interrupted',error_type=type(exc).__name__)
 finally:
  stop.set();thread.join(2)
  record['ended_at']=now();record['elapsed_seconds']=time.monotonic()-start
  if budget is not None:
   record['provider_usage']=budget['calls'];record['attempted_calls']=budget['attempted_calls'];record['estimated_spend_usd']=budget['estimated_spend_usd']
  for arm in ARMS:
   ws=[w for w in record['windows'] if w['arm']==arm and w['status']=='completed'];ids={i for w in ws for i in w['window']['reference_ids']};refs=[x for x in b['scored_references'] if x['reference_id']in ids];preds=[e for w in ws for e in w['events']]
   record['arms'].setdefault(arm,{'status':'not_started'}).update(completed_windows=len(ws),planned_windows=8,metrics=score_events(refs,preds),per_game={g:score_events([x for x in refs if x['game_id']==g],[x for x in preds if x['game_id']==g]) for g in prepared['source_sha256']})
  common=set.intersection(*[{w['index'] for w in record['windows'] if w['arm']==a and w['status']=='completed'} for a in ARMS]);record['common_completed_indices']=sorted(common)
  ids={rid for w in prepared['windows'] if w['index']in common for rid in w['window']['reference_ids']};refs=[r for r in b['scored_references'] if r['reference_id']in ids]
  record['paired_metrics']={a:score_events(refs,[e for w in record['windows'] if w['arm']==a and w['index']in common and w['status']=='completed' for e in w['events']]) for a in ARMS}
  record['peak_client_rss_gib']=max((x['rss_kib'] for x in record['memory']),default=0)/1048576;save()
  summary={k:record.get(k) for k in ['name','status','attempted_calls','elapsed_seconds','estimated_spend_usd']};summary['arms']={a:{'status':v['status'],'completed':v['completed_windows'],**{k:v['metrics'][k] for k in ['tp','fp','fn','micro_f1','macro_f1']}} for a,v in record['arms'].items()}
  note('FINAL '+json.dumps(summary)+'. Same originalreferences/pointmatcher;provisionaltiming,label-informeddiagnostic,no releasepass. See pairedmetrics when armcoverage differs.')
  for name in ['iteration-log.md','all-events-history.jsonl']:
   with (ROOT/'evals/iterations'/name).open('a') as f:f.write(('\n### '+now()+' evidence-pilot-013\n\n' if name.endswith('.md') else '')+json.dumps(summary)+'\n')
  print(json.dumps(summary),flush=True)
 return 0 if record['status']=='completed' else 1
if __name__=='__main__':raise SystemExit(main())
