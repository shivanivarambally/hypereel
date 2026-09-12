"""019: frozen input-bundle comparison using corrected v2 semantics in both arms."""
from pathlib import Path
import base64,json,hashlib,shutil,time,subprocess,os
from openai import OpenAI
from hypereel.config import get_settings
from hypereel.observability import provider_budget_scope,authorize_provider_call,record_provider_usage
from hypereel.evaluation.ball_state_v2 import prompt,parse,derive
from hypereel.evaluation.basketball_events import score_events
from run_evidence_pilot import ROOT,sha,now
from eval_nebius_matched import request_arguments
OUT=ROOT/'evals/iterations/evidence-state-019'
def note(s):
 with (ROOT/'evals/IMPLEMENTATION_NOTES.md').open('a') as f:f.write('\n### '+now()+' — evidence-state-019\n\n'+s+'\n')
def main():
 if (OUT/'report.json').exists():raise FileExistsError('No overwrite')
 prep=json.loads((OUT/'preparation.json').read_text());old=json.loads((ROOT/'evals/iterations/evidence-pilot-013/report.json').read_text());sparse=json.loads((ROOT/'evals/iterations/evidence-pilot-013/prepared.json').read_text())
 ids={i for w in prep['windows'] for i in w['window']['reference_ids']};refs=[r for r in old['scored_references'] if r['reference_id'] in ids]
 assert sha(ROOT/'evals/experiments/all-events-v2/references.jsonl')==old['reference_sha256']
 plan=dict(name='evidence-state-019',created_at=now(),indices=[1,2,6],model='openbmb/MiniCPM-V-4_5',max_calls=57,cumulative_ceiling_usd=8,reserve_per_call=.30,
  arms=['sparse_wide','dense_rim'],hypothesis='Quarter-second sampling with optional native rim crops improves primitive recovery and event recognition over six wide frames, using corrected v2 state semantics in BOTH arms.',
  evidence='Same12second source spans/core intervals. Baseline six wide frames from013; dense49times at4fps and optional320native rim crops. BOTH arms use identical1088x432 canvases and up to3timestamps/3images per request; one image per instant. This is a predeclared compatibility correction to018 duplicate-view output, not silent retry. Previous raw018 results unchanged. Combined input/batching change, not separate density/crop causal estimates.',
  semantic_changes='Explicit shot versus pass releases, release-only shooter zone, explicit missed state allowing airballs, explicit interception rather than inferred steal, unknown-gap reset. No court homography implemented; model release-zone errors remain possible. Assist requires explicit pass and distinct known players; provisional8s linkage heuristic.',
  continuity='Combine chronological primitive rows before deriving events across all batches. No state is summarized by another model. Batch-boundary rederivation test required. Invalid batch invalidates window; two consecutive invalid batches stop that window. Independent windows continue, transport or budget failure stops entire run.',
  parsing='Predeclared frames-array or timestamp-keyed rows accepted; exact times/fields/vocabulary required, no post-hoc repair.',
  evaluation='Same HoopIQ references,all12definitions,five-second one-to-one matcher. Only common fully valid windows paired; failed coverage and supported types explicit. Frames outside core supply context only; both arms use identical boundary derivation.',
  quality_audit='Pre-inference crop QA rejected20campus false matches on advertising. Prepared manifests preserve rejected candidates. Subsequent model-state spot audit is qualitative, not independently labeled full-frame benchmark.',
  holdout_used=False,prepared_sha256=sha(OUT/'preparation.json'),reference_sha256=old['reference_sha256'],source_sha256=prep['source_sha256'])
 (OUT/'plan.json').write_text(json.dumps(plan,indent=2))
 for p in [Path(__file__),ROOT/'src/hypereel/evaluation/ball_state_v2.py',ROOT/'src/hypereel/evaluation/basketball_events.py',ROOT/'scripts/prepare_state_evidence.py',ROOT/'scripts/prepare_rim_crops.py',ROOT/'scripts/prepare_state_composites.py']:
  shutil.copy2(p,OUT/(p.name+'.snapshot'))
 settings=get_settings();settings.max_provider_calls=57;settings.max_provider_spend_usd=8;settings.provider_call_reserve_usd=.30;settings.nebius_input_cost_per_million_usd=10;settings.nebius_output_cost_per_million_usd=30
 settings.provider_spend_ledger_path=str(ROOT/'evals/iterations/spend-ledger.json');settings.provider_checkpoint_dir=str(OUT/'checkpoints')
 assert settings.nebius_base_url.rstrip('/')=='https://api.studio.nebius.com/v1'
 client=OpenAI(api_key=settings.nebius_api_key,base_url=settings.nebius_base_url,max_retries=0,timeout=180)
 rec=dict(name=plan['name'],status='running',started_at=now(),plan=plan,scored_references=refs,calls=[],windows=[],holdout_used=False)
 def save():
  tmp=OUT/'report.tmp';tmp.write_text(json.dumps(rec,indent=2));tmp.replace(OUT/'report.json')
 budget=None;started=time.monotonic();note('START '+json.dumps(plan));save()
 try:
  with provider_budget_scope(settings,checkpoint_context=plan) as budget:
   for w in prep['windows']:
    for arm in plan['arms']:
     core=w['window'];entry=dict(index=w['index'],arm=arm,window=core,started_at=now(),status='running',states=[],invalid_batches=[]);rec['windows'].append(entry);save()
     if arm=='sparse_wide':
      frames=w['sparse_frames'];batches=[frames[i:i+3] for i in range(0,len(frames),3)]
     else:batches=[w['frames'][i:i+3] for i in range(0,len(w['frames']),3)]
     invalid_streak=0
     for bi,frames in enumerate(batches):
      times=[f['time'] for f in frames];images=[];manifest=[]
      for f in frames:
       for view in ['wide','crop']:
        if view in f:
         item=f[view];path=ROOT/item['path'];assert sha(path)==item['sha256'];images.append(base64.b64encode(path.read_bytes()).decode());manifest.append(dict(time=f['time'],view=view,path=item['path'],sha256=item['sha256']))
      txt=prompt(times,[dict(image=i+1,time=x['time'],view='wide_left_optional_rim_right_same_instant') for i,x in enumerate(manifest)])+' Each supplied image shows ONE timestamp: wide view left, optional native rim crop right. The panels are the same instant; return ONE state row per IMAGE.'
      call=dict(index=w['index'],arm=arm,batch=bi,times=times,manifest=manifest,prompt=txt,started_at=now(),status='started');rec['calls'].append(call);save()
      authorize_provider_call(provider='nebius',model=plan['model'],operation='state_evidence_'+arm)
      ts=time.monotonic()
      try:
       args=request_arguments(images,txt);args['max_tokens']=1536;response=client.chat.completions.create(**args)
      except Exception as exc:
       call.update(status='provider_error',error_type=type(exc).__name__)
       pending=budget['calls'][-1];pending.update(status='error',usage_unknown=True,estimated_cost_usd=.30,error_type=type(exc).__name__);budget['estimated_spend_usd']+=.30
       Path(settings.provider_spend_ledger_path).write_text(json.dumps({'estimated_spend_usd':budget['estimated_spend_before_run_usd']+budget['estimated_spend_usd']}));budget['journal'].append('unknown_usage_reserved',call=pending);save();raise
      call.update(raw_completion=response.model_dump(),ended_at=now(),latency_seconds=time.monotonic()-ts,status='received');save();budget['journal'].append('raw_state_evidence',**call)
      if response.usage is None:
       pending=budget['calls'][-1];pending.update(status='error',usage_unknown=True,estimated_cost_usd=.30);budget['estimated_spend_usd']+=.30;Path(settings.provider_spend_ledger_path).write_text(json.dumps({'estimated_spend_usd':budget['estimated_spend_before_run_usd']+budget['estimated_spend_usd']}));raise RuntimeError('Missing usage; reserve retained')
      record_provider_usage(response,status='success' if response.choices and response.choices[0].finish_reason=='stop' else 'incomplete');rec['provider_usage']=budget['calls']
      call['client_rss_kib']=int(subprocess.check_output(['ps','-o','rss=','-p',str(os.getpid())],text=True));call['pressure_level']=int(subprocess.check_output(['sysctl','-n','kern.memorystatus_vm_pressure_level'],text=True))
      raw=response.choices[0].message.content or '' if response.choices else ''
      try:
       if not response.choices or response.choices[0].finish_reason!='stop':raise ValueError('Incomplete output')
       states=parse(raw,times);entry['states']+=states;call['status']='valid';invalid_streak=0
      except ValueError as exc:call.update(status='invalid',error=str(exc));entry['invalid_batches'].append(bi);invalid_streak+=1
      note(f'window{w["index"]} {arm} batch{bi}, {call["status"]}, {call["latency_seconds"]:.2f}s, '+call.get('error','')+'\n\n```json\n'+raw+'\n```');save()
      print(json.dumps(dict(index=w['index'],arm=arm,batch=bi,status=call['status'])),flush=True)
      if invalid_streak>=2:note('Two consecutive invalid batches; stop this window, no retries.');break
     entry['status']='invalid' if entry['invalid_batches'] else 'completed';entry['ended_at']=now()
     if entry['status']=='completed':
      events,notes=derive(entry['states'],core['start'],core['end']);entry.update(events=[dict(e,game_id=core['game_id']) for e in events],derivation_notes=notes)
     note('WINDOW '+json.dumps(entry));save()
  rec['status']='completed' if all(w['status']=='completed' for w in rec['windows']) else 'completed_with_invalid_windows'
 except BaseException as exc:
  rec.update(status='stopped',error_type=type(exc).__name__);note('STOP '+type(exc).__name__+'; raw results retained.')
 finally:
  common=set.intersection(*[{w['index'] for w in rec['windows'] if w['arm']==arm and w['status']=='completed'} for arm in plan['arms']]);rec['common_completed_indices']=sorted(common);rec['paired_metrics']={};rec['available_metrics']={}
  for arm in plan['arms']:
   for key,ws in [('paired_metrics',[w for w in rec['windows'] if w['arm']==arm and w['index'] in common]),('available_metrics',[w for w in rec['windows'] if w['arm']==arm and w['status']=='completed'])]:
    validids={i for w in ws for i in w['window']['reference_ids']};rec[key][arm]=score_events([r for r in refs if r['reference_id'] in validids],[e for w in ws for e in w['events']])
  rec.update(ended_at=now(),elapsed_seconds=time.monotonic()-started)
  if budget is not None:rec.update(provider_usage=budget['calls'],attempted_calls=budget['attempted_calls'],estimated_spend_usd=budget['estimated_spend_usd'])
  save();summary={k:rec.get(k) for k in ['name','status','started_at','ended_at','elapsed_seconds','attempted_calls','estimated_spend_usd','common_completed_indices']};summary['paired_metrics']={a:{k:m[k] for k in ['tp','fp','fn','micro_precision','micro_recall','micro_f1','macro_f1']} for a,m in rec['paired_metrics'].items()};note('FINAL '+json.dumps(summary))
  for name in ['iteration-log.md','all-events-history.jsonl']:
   with (ROOT/'evals/iterations'/name).open('a') as f:f.write(('\n### '+now()+' —019\n\n' if name.endswith('.md') else '')+json.dumps(summary)+'\n')
  print(json.dumps(summary),flush=True)
 return 0 if rec['status']=='completed' else 1
if __name__=='__main__':raise SystemExit(main())
