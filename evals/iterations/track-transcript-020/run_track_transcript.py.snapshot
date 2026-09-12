"""020 paired MiniCPM extraction with/without continuous-track transcript."""
from pathlib import Path
import json,base64,time,shutil,hashlib
from openai import OpenAI
from hypereel.config import get_settings
from hypereel.observability import provider_budget_scope,authorize_provider_call,record_provider_usage
from hypereel.evaluation.transcript import observation_prompt,parse_transcript,extraction_prompt,parse_window_extracted_events
from hypereel.evaluation.basketball_events import score_events
from run_evidence_pilot import ROOT,sha,now
from eval_nebius_matched import request_arguments
OUT=ROOT/'evals/iterations/track-transcript-020';ARMS=['visual_transcript','track_augmented_transcript']
def note(s):
 with (ROOT/'evals/IMPLEMENTATION_NOTES.md').open('a') as f:f.write('\n### '+now()+' — track-transcript-020 inference\n\n'+s.rstrip()+'\n')
def event_prompt(rows,core):
 return extraction_prompt(rows,core['start'],core['end']).replace('You cannot see the video.','You also have chronological wide images for visual verification.').replace('ONLY from the supplied visual transcript.','from the supplied transcript and corroborating images. Treat every transcript observation as unverified evidence.') + (
  '\nTrack-derived observations, when present, are uncertain detector/tracker measurements, not confirmed actions. '+
  'Ball/person track IDs are not player jerseys or team identities. Track coordinates are native1280pixel-wide image coordinates; '+
  'the images are resized768wide. Camera motion is not compensated. Proximity alone cannot prove possession, a steal or a rebound. '+
  'Absent tracks mean unknown, not no event. Cite supplied observation IDs, but only emit events supported by actual evidence. '+
  'Image times are supplied in the next line.')
def main():
 if (OUT/'report.json').exists():raise FileExistsError('No overwrite')
 track=json.loads((OUT/'tracking.json').read_text());assert track['status']=='completed' and len(track['windows'])==3
 sparse=json.loads((ROOT/'evals/iterations/evidence-pilot-013/prepared.json').read_text());base=json.loads((ROOT/'evals/iterations/evidence-pilot-013/report.json').read_text());assert track['plan']['source_sha256']==base['source_sha256'];assert sha(ROOT/'evals/experiments/all-events-v2/references.jsonl')==base['reference_sha256']
 ids={i for w in track['windows'] for i in w['window']['reference_ids']};refs=[r for r in base['scored_references'] if r['reference_id'] in ids]
 plan=dict(name='track-transcript-020',created_at=now(),indices=[1,2,6],model='openbmb/MiniCPM-V-4_5',max_calls=9,cumulative_ceiling=8,reserve=.30,
  hypothesis='Adding a deterministic transcript of every-native-frame YOLO/ByteTrack measurements to a shared visual transcript improves event precision/recall over the shared visual transcript alone.',
  arms=ARMS,controls='One fresh MiniCPM visual transcript per window reused identically in both arms; identical6wide JPEGs also supplied to both extraction calls. Same model,temperature0,seed0,max1536tokens,definitions,observation-ID validation,context/core filtering and scorer. Only additional track observations differ. This is not a pure text-only extraction replay of015.',
  tracking_sha256=sha(OUT/'tracking.json'),reference_sha256=base['reference_sha256'],source_sha256=base['source_sha256'],
  failure_policy='No retries; invalid narration skips dependent arms; invalid extraction invalidates only that window/arm; provider or budget error stops run. No semantic post-filter or score tuning.',
  caveats='Generic COCO detector, ByteTrack nativeFPS, no team/jersey identity, no court geometry, no camera-motion compensation. Availability/continuity are not detection recall. No reference labels are sent to models.',holdout_used=False)
 (OUT/'plan.json').write_text(json.dumps(plan,indent=2))
 for p in [Path(__file__),ROOT/'scripts/prepare_track_transcript.py',ROOT/'src/hypereel/evaluation/transcript.py',ROOT/'src/hypereel/evaluation/basketball_events.py']:
  shutil.copy2(p,OUT/(p.name+'.snapshot'))
 settings=get_settings();settings.max_provider_calls=9;settings.max_provider_spend_usd=8;settings.provider_call_reserve_usd=.30;settings.nebius_input_cost_per_million_usd=10;settings.nebius_output_cost_per_million_usd=30;settings.provider_spend_ledger_path=str(ROOT/'evals/iterations/spend-ledger.json');settings.provider_checkpoint_dir=str(OUT/'checkpoints');assert settings.nebius_base_url.rstrip('/')=='https://api.studio.nebius.com/v1'
 client=OpenAI(api_key=settings.nebius_api_key,base_url=settings.nebius_base_url,max_retries=0,timeout=180)
 rec=dict(name=plan['name'],status='running',started_at=now(),plan=plan,calls=[],windows=[],scored_references=refs,holdout_used=False)
 def save():
  p=OUT/'report.tmp';p.write_text(json.dumps(rec,indent=2));p.replace(OUT/'report.json')
 def call(stage,idx,txt,images,budget):
  c=dict(stage=stage,index=idx,started_at=now(),status='started',prompt=txt,image_sha256=[hashlib.sha256(base64.b64decode(i)).hexdigest() for i in images]);rec['calls'].append(c);save();authorize_provider_call(provider='nebius',model=plan['model'],operation='track_transcript_'+stage);ts=time.monotonic()
  try:
   args=request_arguments(images,txt);args['max_tokens']=1536;response=client.chat.completions.create(**args)
  except Exception as exc:
   c.update(status='provider_error',error_type=type(exc).__name__);pending=budget['calls'][-1];pending.update(status='error',usage_unknown=True,estimated_cost_usd=.30);budget['estimated_spend_usd']+=.30;Path(settings.provider_spend_ledger_path).write_text(json.dumps({'estimated_spend_usd':budget['estimated_spend_before_run_usd']+budget['estimated_spend_usd']}));budget['journal'].append('unknown_usage_reserved',call=pending);save();raise
  c.update(status='received',ended_at=now(),latency_seconds=time.monotonic()-ts,raw_completion=response.model_dump());save();budget['journal'].append('track_transcript_raw',**c)
  if response.usage is None:
   budget['calls'][-1].update(status='error',usage_unknown=True,estimated_cost_usd=.30);budget['estimated_spend_usd']+=.30;Path(settings.provider_spend_ledger_path).write_text(json.dumps({'estimated_spend_usd':budget['estimated_spend_before_run_usd']+budget['estimated_spend_usd']}));raise RuntimeError('Missing usage; reserve retained')
  record_provider_usage(response,status='success' if response.choices and response.choices[0].finish_reason=='stop' else 'incomplete');rec['provider_usage']=budget['calls'];save()
  raw=response.choices[0].message.content or '' if response.choices else '';note(f'window{idx}, {stage}, {c["latency_seconds"]:.2f}s. Raw output:\n\n```json\n'+raw+'\n```')
  if not response.choices or response.choices[0].finish_reason!='stop':raise ValueError('Incomplete output')
  return raw
 budget=None;started=time.monotonic();note('PREDECLARED START '+json.dumps(plan));save()
 try:
  with provider_budget_scope(settings,checkpoint_context=plan) as budget:
   for tw in track['windows']:
    idx=tw['index'];w=next(w for w in sparse['windows'] if w['index']==idx);core=w['window'];frames=w['sparse_frames'];times=[f['time'] for f in frames];images=[]
    for f in frames:
     p=ROOT/f['wide']['path'];assert sha(p)==f['wide']['sha256'];images.append(base64.b64encode(p.read_bytes()).decode())
    row=dict(index=idx,window=core,manifest=frames,narration_status='started',arms={});rec['windows'].append(row);save()
    try:observations=parse_transcript(call('narration',idx,observation_prompt(times),images,budget),times);row.update(narration_status='completed',visual_observations=observations)
    except ValueError as exc:row.update(narration_status='invalid',error=str(exc));note(f'window{idx} narration invalid: {exc}; skip dependent arms.');save();continue
    for arm in ARMS:
     evidence=observations+(tw['observations'] if arm==ARMS[1] else []);row['arms'][arm]=dict(status='started',observations=evidence);save()
     try:
      raw=call(arm,idx,event_prompt(evidence,core)+'\n'+json.dumps(times),images,budget)
      events,context=parse_window_extracted_events(raw,evidence,min(times),max(times),core['start'],core['end']);row['arms'][arm].update(status='completed',events=[dict(e,game_id=core['game_id']) for e in events],context_events=context)
     except ValueError as exc:row['arms'][arm].update(status='invalid',error=str(exc));note(f'window{idx} {arm} invalid: {exc}; no retry.')
     save()
    row['ended_at']=now();note('WINDOW '+json.dumps(row));save();print(idx,[(a,v['status']) for a,v in row['arms'].items()],flush=True)
  rec['status']='completed' if all(w['narration_status']=='completed' and all(w['arms'].get(a,{}).get('status')=='completed' for a in ARMS) for w in rec['windows']) else 'completed_with_invalid_windows'
 except BaseException as exc:rec.update(status='stopped',error_type=type(exc).__name__);note('STOP '+type(exc).__name__)
 finally:
  common={w['index'] for w in rec['windows'] if all(w['arms'].get(a,{}).get('status')=='completed' for a in ARMS)};rec['common_completed_indices']=sorted(common);rec['paired_metrics']={};rec['available_metrics']={}
  for arm in ARMS:
   for key,ws in [('paired_metrics',[w for w in rec['windows'] if w['index'] in common]),('available_metrics',[w for w in rec['windows'] if w['arms'].get(arm,{}).get('status')=='completed'])]:
    validids={i for w in ws for i in w['window']['reference_ids']};rec[key][arm]=score_events([r for r in refs if r['reference_id'] in validids],[e for w in ws for e in w['arms'][arm]['events']])
  rec.update(ended_at=now(),elapsed_seconds=time.monotonic()-started)
  if budget is not None:rec.update(provider_usage=budget['calls'],attempted_calls=budget['attempted_calls'],estimated_spend_usd=budget['estimated_spend_usd'])
  save();summary={k:rec.get(k) for k in ['name','status','started_at','ended_at','elapsed_seconds','attempted_calls','estimated_spend_usd','common_completed_indices']};summary['paired_metrics']={a:{k:m[k] for k in ['tp','fp','fn','micro_precision','micro_recall','micro_f1','macro_f1']} for a,m in rec['paired_metrics'].items()};note('FINAL '+json.dumps(summary))
  for name in ['iteration-log.md','all-events-history.jsonl']:
   with (ROOT/'evals/iterations'/name).open('a') as f:f.write(('\n### '+now()+' —020\n\n' if name.endswith('.md') else '')+json.dumps(summary)+'\n')
  print(json.dumps(summary),flush=True)
 return 0 if rec['status']=='completed' else 1
if __name__=='__main__':raise SystemExit(main())
