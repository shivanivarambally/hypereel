"""Bounded Gemini021 diagnostic. No production provider changes or holdout access."""
import base64, hashlib, json, resource, shutil, time, urllib.request, urllib.error, argparse
from pathlib import Path
from hypereel.evaluation.gemini_retry_policy import retry_delay
from datetime import datetime
from zoneinfo import ZoneInfo
from hypereel.config import get_settings
from hypereel.evaluation.basketball_events import parse_events, score_events
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evals/iterations/gemini-confirmation-023'
INDICES=[1,2,6]
ARMS=['images','video']
MEDIA=ROOT/'evals/iterations/gemini-development-media'
MODEL='gemini-3.8-flash'
CONFIG={'temperature':0,'maxOutputTokens':8192,'thinkingConfig':{'thinkingLevel':'LOW'},'responseMimeType':'application/json','mediaResolution':'MEDIA_RESOLUTION_HIGH'}
RATES={'input_per_million':.75,'output_including_thinking_per_million':3.75}
def now():return datetime.now(ZoneInfo('Asia/Kolkata')).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):
 t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,indent=2));t.replace(p)
def note(s):
 with (ROOT/'evals/IMPLEMENTATION_NOTES.md').open('a') as f:f.write('\n### '+now()+' — '+OUT.name+'\n\n'+s+'\n')
def post(key,method,body):
 req=urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:{method}',data=json.dumps(body).encode(),headers={'x-goog-api-key':key,'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=180) as r:return json.load(r)
 except urllib.error.HTTPError as e:
  # Error payload has no request headers; redact credential defensively.
  message=e.read().decode().replace(key,'[REDACTED]')
  raise RuntimeError(f'HTTP {e.code}: {message}') from None

def main():
 if (OUT/'report.json').exists():raise FileExistsError('Refusing to overwrite run')
 key=get_settings().gemini_api_key;assert key
 base=json.loads((ROOT/'evals/iterations/evidence-pilot-013/report.json').read_text())
 assert sha(ROOT/'evals/experiments/all-events-v2/references.jsonl')==base['reference_sha256']
 controls=[w for w in base['windows'] if w['arm']=='wide6_context' and w['index'] in INDICES];assert len(controls)==len(INDICES)
 ids={i for w in controls for i in w['window']['reference_ids']};refs=[r for r in base['scored_references'] if r['reference_id'] in ids]
 plan=json.loads((OUT/'plan.json').read_text());plan.update(status='frozen_before_inference',model=MODEL,generation_config=CONFIG,rates=RATES,pricing_source='https://ai.google.dev/gemini-api/docs/pricing',api_source='https://ai.google.dev/api/generate-content',implementation='Standard-library REST generateContent; no SDK installation needed. Documented videoMetadata.fps=4 (deprecated compatibility field).',comparison_caveats='Identical image bytes and prompt, but provider decoding differs: Gemini LOW thinking and8192 total output cap vs MiniCPM1536. Native video also changes resolution and sampling, so video effect is combined evidence change, not FPS alone.',failure_policy='At most one retry per transient503/429 request, maximum2 retries per run,20sbackoff; reserve each attempt. Other provider errors stop. Invalid schema not retried. Unknown usage reservation retained.',started_at=now());write(OUT/'plan.json',plan)
 shutil.copy2(Path(__file__),OUT/'run_gemini_pilot.py.snapshot');shutil.copy2(ROOT/'src/hypereel/evaluation/basketball_events.py',OUT/'basketball_events.py.snapshot')
 ledger=ROOT/'evals/iterations/spend-ledger.json';before=json.loads(ledger.read_text())['estimated_spend_usd'];rec={'status':'running','started_at':now(),'plan':plan,'calls':[],'scored_references':refs,'historical_control':controls,'spend_before_usd':before,'holdout_used':False};start=time.monotonic()
 note('Frozen pilot: '+json.dumps(plan));write(OUT/'report.json',rec)
 try:
  for w in controls:
   core=w['window'];lo=min(x['time'] for x in w['manifest']);hi=max(x['time'] for x in w['manifest'])
   for arm in ARMS:
    parts=[];manifest=[];prompt=w['prompt']
    if arm=='images':
     for m in w['manifest']:
      p=ROOT/m['path'];assert sha(p)==m['sha256'];manifest.append(m);parts.append({'inlineData':{'mimeType':'image/jpeg','data':base64.b64encode(p.read_bytes()).decode()}})
    else:
     p=MEDIA/f'w{w["index"]}-continuous.mp4'
     assert p.stat().st_size<20_000_000
     manifest=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'source_start':lo,'source_end':hi,'fps_requested':4,'audio':'muted','source_width':1280}]
     parts=[{'inlineData':{'mimeType':'video/mp4','data':base64.b64encode(p.read_bytes()).decode()},'videoMetadata':{'fps':4}}]
     prompt=prompt[prompt.index('\ntwo_point_made:'):].split(' Ordered image manifest:')[0]
     prompt=('Analyze ALL basketball events in this continuous video, not just highlights. Video 00:00 corresponds to source time '+str(lo)+' seconds. Return numeric SOURCE time_seconds by adding this offset to clip time.\n'+prompt).replace('between images','outside the visible video').replace('Images outside that interval','Video portions outside that interval').replace('one event per image','one event per frame')
    parts.append({'text':prompt});body={'contents':[{'role':'user','parts':parts}],'generationConfig':CONFIG}
    call={'index':w['index'],'arm':arm,'window':core,'started_at':now(),'status':'preflight','manifest':manifest,'prompt':prompt,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'generation_config':CONFIG};rec['calls'].append(call);write(OUT/'report.json',rec)
    count=post(key,'countTokens',{'generateContentRequest':dict(body,model='models/'+MODEL)});call['token_preflight']=count
    tokens=count['totalTokens'];reserve=(tokens*1.25*RATES['input_per_million']+CONFIG['maxOutputTokens']*RATES['output_including_thinking_per_million'])/1e6+.01
    spent=json.loads(ledger.read_text())['estimated_spend_usd'];assert spent+reserve<=8,'Budget ceiling'
    call.update(status='reserved',reserved_usd=reserve);write(ledger,{'estimated_spend_usd':spent+reserve});write(OUT/'report.json',rec)
    note(f'window{w["index"]} {arm}: token count{tokens}, reserved${reserve:.6f}; request starting.');ts=time.monotonic()
    call['attempts']=[]
    for attempt in range(2):
     attempt_row={'started_at':now(),'reservation_usd':reserve};call['attempts'].append(attempt_row);write(OUT/'report.json',rec)
     try:
      raw=post(key,'generateContent',body);attempt_row['status']='received';break
     except RuntimeError as error:
      attempt_row.update(status='provider_error',error=str(error),ended_at=now());write(OUT/'report.json',rec);note('Provider attempt failure '+json.dumps(attempt_row))
      delay=retry_delay(error)
      if attempt or rec.get('retry_count',0)>=2 or delay is None:raise
      rec['retry_count']=rec.get('retry_count',0)+1;time.sleep(delay)
      spent=json.loads(ledger.read_text())['estimated_spend_usd'];assert spent+reserve<=8,'Retry budget ceiling';write(ledger,{'estimated_spend_usd':spent+reserve});ts=time.monotonic()
    call.update(raw_response=raw,latency_seconds=time.monotonic()-ts,ended_at=now(),status='received');write(OUT/'report.json',rec)
    usage=raw.get('usageMetadata',{});assert 'promptTokenCount' in usage and 'totalTokenCount' in usage,'Missing usage; reservation retained'
    output=max(usage.get('candidatesTokenCount',0)+usage.get('thoughtsTokenCount',0),usage['totalTokenCount']-usage['promptTokenCount'])
    cost=(usage['promptTokenCount']*RATES['input_per_million']+output*RATES['output_including_thinking_per_million'])/1e6
    call.update(estimated_cost_usd=cost,usage=usage);write(ledger,{'estimated_spend_usd':spent+cost})
    try:
     candidates=raw.get('candidates',[]);assert candidates and candidates[0].get('finishReason')=='STOP','Incomplete output'
     text=''.join(p.get('text','') for p in candidates[0].get('content',{}).get('parts',[]) if not p.get('thought'));call['raw_text']=text
     events=[dict(e.model_dump(),game_id=core['game_id']) for e in parse_events(text,lo,hi)]
     call.update(status='completed',events=[e for e in events if core['start']<=e['time_seconds']<=core['end']],context_events=[e for e in events if not core['start']<=e['time_seconds']<=core['end']])
    except (ValueError,AssertionError) as e:call.update(status='invalid',error=str(e))
    write(OUT/'report.json',rec);write(OUT/f'w{w["index"]}-{arm}-checkpoint.json',call);note('CALL RESULT '+json.dumps(call));print(w['index'],arm,call['status'],call.get('events'),flush=True)
  rec['status']='completed' if all(c['status']=='completed' for c in rec['calls']) else 'completed_with_invalid_windows'
 except Exception as e:
  rec.update(status='stopped',error=str(e).replace(key,'[REDACTED]'));note('STOP '+rec['error']);print(rec['error'],flush=True)
 finally:
  common=[w['index'] for w in controls if all(any(c['index']==w['index'] and c['arm']==a and c['status']=='completed' for c in rec['calls']) for a in ARMS)]
  validids={i for w in controls if w['index'] in common for i in w['window']['reference_ids']};pairedrefs=[r for r in refs if r['reference_id'] in validids];rec['common_completed_indices']=common;rec['paired_metrics']={}
  for arm in ['historical_minicpm']+ARMS:
   rows=controls if arm=='historical_minicpm' else [c for c in rec['calls'] if c['arm']==arm and c['status']=='completed']
   rec['paired_metrics'][arm]=score_events(pairedrefs,[e for w in rows if w['index'] in common for e in w.get('events',[])])
  rec.update(ended_at=now(),elapsed_seconds=time.monotonic()-start,peak_client_rss_gib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024**3,spend_after_usd=json.loads(ledger.read_text())['estimated_spend_usd']);rec['incremental_estimated_spend_usd']=rec['spend_after_usd']-before;write(OUT/'report.json',rec)
  summary={k:rec[k] for k in ['status','elapsed_seconds','peak_client_rss_gib','spend_after_usd','incremental_estimated_spend_usd','common_completed_indices']};summary['metrics']={a:{k:m[k] for k in ['tp','fp','fn','micro_precision','micro_recall','micro_f1']} for a,m in rec['paired_metrics'].items()};note('FINAL '+json.dumps(summary));print(json.dumps(summary),flush=True)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--broad',action='store_true');parser.add_argument('--images-recovery',action='store_true');parser.add_argument('--output-name');parser.add_argument('--indices');parser.add_argument('--arms',choices=['images','video']);args=parser.parse_args()
 if args.broad:
  OUT=ROOT/'evals/iterations/gemini-development-024';INDICES=list(range(8));ARMS=['video']
 if args.images_recovery:
  OUT=ROOT/'evals/iterations/gemini-images-recovery-026';INDICES=[2,6];ARMS=['images']
 if args.output_name:
  assert '/' not in args.output_name and '..' not in args.output_name
  OUT=ROOT/'evals/iterations'/args.output_name
 if args.indices:INDICES=[int(i) for i in args.indices.split(',')];assert all(0<=i<8 for i in INDICES)
 if args.arms:ARMS=[args.arms]
 main()
