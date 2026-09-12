"""Bounded three-window direct vs transcript comparison, with append-only notes."""
from pathlib import Path
import base64, hashlib, json, shutil, time, subprocess, os
from openai import OpenAI
from hypereel.config import get_settings
from hypereel.observability import provider_budget_scope, authorize_provider_call, record_provider_usage, ProviderBudgetExceeded
from hypereel.evaluation.basketball_events import parse_events, score_events
from hypereel.evaluation.transcript import observation_prompt, parse_transcript, extraction_prompt, parse_extracted_events
from run_evidence_pilot import sha, now, make_manifest, pilot_prompt
from eval_nebius_matched import request_arguments
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evals/iterations/transcript-pilot-015'

def note(message):
    with (ROOT/'evals/IMPLEMENTATION_NOTES.md').open('a') as f:
        f.write('\n### '+now()+' — transcript-pilot-015\n\n'+message+'\n')

def main():
    if (OUT/'report.json').exists():raise FileExistsError('No overwrite or automatic rerun')
    prepared=json.loads((ROOT/'evals/iterations/evidence-pilot-013/prepared.json').read_text())
    baseline=json.loads((ROOT/'evals/iterations/evidence-pilot-013/report.json').read_text())
    fixture=json.loads((ROOT/'evals/experiments/all-events-v2/diagnostic-009.json').read_text())
    if set(fixture['source_files'])!={'east-bay-elite-vs-spartans','unlimited-vs-campus'}:raise ValueError('Source allowlist')
    for g,p in fixture['source_files'].items():
        if sha(ROOT/p)!=baseline['source_sha256'][g]:raise ValueError('Source changed')
    if sha(ROOT/'evals/experiments/all-events-v2/references.jsonl')!=baseline['reference_sha256']:raise ValueError('References changed')
    windows=[w for w in prepared['windows'] if w['index'] in [1,2,6]]
    ids={i for w in windows for i in w['window']['reference_ids']}
    refs=[r for r in baseline['scored_references'] if r['reference_id'] in ids]
    plan=dict(name='transcript-pilot-015',created_at=now(),indices=[1,2,6],model='openbmb/MiniCPM-V-4_5',
        hypothesis='Explicit observation transcript followed by text-only extraction improves event precision/F1 without hiding lost recall.',
        evidence='Identical six JPEGs and timestamps per direct/transcript window, reused from013;12second context;768wide;not native continuous video.',
        budget=dict(max_calls=9,cumulative_ceiling=5,reserve_per_call=.30),output_limit=1536,temperature=0,seed=0,
        extraction='Same model, text only, observation-ID links required; semantic support checked in post-run observations, not assumed from citations.',
        failures='No retries. Record failed window/stage; skip dependent extraction if narration invalid; proceed independent windows unless transport/budget failure.',
        scoring='Frozen HoopIQ development references,12 label definitions,five-second matcher;only completed common windows compared;unsupported types unmeasured.',
        holdout_used=False,reference_sha256=baseline['reference_sha256'],source_sha256=baseline['source_sha256'])
    (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    for p in [Path(__file__),ROOT/'src/hypereel/evaluation/transcript.py',ROOT/'src/hypereel/evaluation/basketball_events.py']:
        shutil.copy2(p,OUT/(p.name+'.snapshot'))
    settings=get_settings();settings.max_provider_calls=9;settings.max_provider_spend_usd=5;settings.provider_call_reserve_usd=.30
    settings.nebius_input_cost_per_million_usd=10;settings.nebius_output_cost_per_million_usd=30
    settings.provider_spend_ledger_path=str(ROOT/'evals/iterations/spend-ledger.json');settings.provider_checkpoint_dir=str(OUT/'checkpoints')
    if settings.nebius_base_url.rstrip('/')!='https://api.studio.nebius.com/v1':raise ValueError('Endpoint mismatch')
    client=OpenAI(api_key=settings.nebius_api_key,base_url=settings.nebius_base_url,max_retries=0,timeout=180)
    record=dict(name=plan['name'],started_at=now(),status='running',plan=plan,plan_sha256=sha(OUT/'plan.json'),scored_references=refs,calls=[],windows=[],holdout_used=False)
    def save():
        p=OUT/'report.tmp';p.write_text(json.dumps(record,indent=2)+'\n');p.replace(OUT/'report.json')
    def call(stage,index,prompt,images,budget):
        entry=dict(stage=stage,index=index,started_at=now(),status='started',prompt=prompt,prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),image_sha256=[hashlib.sha256(base64.b64decode(i)).hexdigest() for i in images])
        record['calls'].append(entry);save()
        authorize_provider_call(provider='nebius',model=plan['model'],operation='transcript_pilot_'+stage)
        ts=time.monotonic()
        try:
            args=request_arguments(images,prompt);args['max_tokens']=1536
            response=client.chat.completions.create(**args)
        except Exception as exc:
            entry.update(status='provider_error',error_type=type(exc).__name__,ended_at=now())
            pending=budget['calls'][-1];pending.update(status='error',usage_unknown=True,estimated_cost_usd=.30,error_type=type(exc).__name__)
            budget['estimated_spend_usd']+=.30
            Path(settings.provider_spend_ledger_path).write_text(json.dumps({'estimated_spend_usd':budget['estimated_spend_before_run_usd']+budget['estimated_spend_usd']})+'\n')
            budget['journal'].append('unknown_usage_reserved',call=pending);save();raise
        entry.update(raw_completion=response.model_dump(),ended_at=now(),latency_seconds=time.monotonic()-ts,status='received')
        save();budget['journal'].append('transcript_raw_response',**entry)
        if response.usage is None:
            pending=budget['calls'][-1];pending.update(status='error',usage_unknown=True,estimated_cost_usd=.30)
            budget['estimated_spend_usd']+=.30
            Path(settings.provider_spend_ledger_path).write_text(json.dumps({'estimated_spend_usd':budget['estimated_spend_before_run_usd']+budget['estimated_spend_usd']})+'\n')
            raise RuntimeError('Missing usage; reserve retained')
        record_provider_usage(response,status='success' if response.choices and response.choices[0].finish_reason=='stop' else 'incomplete')
        entry['client_rss_kib']=int(subprocess.check_output(['ps','-o','rss=','-p',str(os.getpid())],text=True).strip())
        entry['pressure_level']=int(subprocess.check_output(['sysctl','-n','kern.memorystatus_vm_pressure_level'],text=True))
        record['provider_usage']=budget['calls'];save()
        raw=response.choices[0].message.content or '' if response.choices else ''
        note(f'window {index}, {stage}, received at {entry["ended_at"]}, latency {entry["latency_seconds"]:.2f}s. Raw output:\n\n```json\n'+raw+'\n```')
        if not response.choices or response.choices[0].finish_reason!='stop':raise ValueError('Incomplete output')
        return raw
    note('PREDECLARED START. User identifies HoopIQ as specialist label source and authorizes transcript test. '+json.dumps(plan)+f' Reference support: {len(refs)} events across {len({r["label"] for r in refs})} types. No references passed to inference. Fresh direct baseline; same visual inputs; extraction sees transcript only. Known sparse evidence limitation retained to isolate representation change. Historical cost estimates, not invoice pricing.')
    save();started=time.monotonic();budget=None
    try:
        with provider_budget_scope(settings,checkpoint_context=plan) as budget:
            for w in windows:
                core=w['window'];items=make_manifest(w,'wide6_context');times=[x['time'] for x in items];images=[]
                for x in items:
                    if sha(ROOT/x['path'])!=x['sha256']:raise RuntimeError('Image changed')
                    images.append(base64.b64encode((ROOT/x['path']).read_bytes()).decode())
                entry=dict(index=w['index'],window=core,manifest=items,direct_status='not_started',transcript_status='not_started')
                record['windows'].append(entry);save()
                try:
                    raw=call('direct',w['index'],pilot_prompt(w,items),images,budget)
                    events=[e.model_dump() for e in parse_events(raw,min(times),max(times))]
                    entry['direct_events']=[dict(e,game_id=core['game_id']) for e in events if core['start']<=e['time_seconds']<=core['end']]
                    entry['direct_context_events']=[e for e in events if not core['start']<=e['time_seconds']<=core['end']]
                    entry['direct_status']='completed'
                except ValueError as exc:
                    entry.update(direct_status='invalid',direct_error=str(exc));note(f'Window {w["index"]} direct invalid: {exc}. No retry.')
                save()
                try:
                    raw=call('narration',w['index'],observation_prompt(times),images,budget)
                    rows=parse_transcript(raw,times);entry['observations']=rows;entry['narration_status']='completed';save()
                    raw=call('extraction',w['index'],extraction_prompt(rows,core['start'],core['end']),[],budget)
                    events=parse_extracted_events(raw,rows,core['start'],core['end'])
                    entry['transcript_events']=[dict(e,game_id=core['game_id']) for e in events];entry['transcript_status']='completed'
                except ValueError as exc:
                    entry.update(transcript_status='invalid',transcript_error=str(exc));note(f'Window {w["index"]} transcript branch invalid: {exc}. No retry or dependent extraction after invalid narration.')
                entry['ended_at']=now();save()
                note('WINDOW COMPLETE '+json.dumps(entry));print(json.dumps({k:v for k,v in entry.items() if k!='manifest'}),flush=True)
        record['status']='completed' if all(w['direct_status']==w['transcript_status']=='completed' for w in record['windows']) else 'completed_with_invalid_windows'
    except BaseException as exc:
        record.update(status='stopped',error_type=type(exc).__name__);note('STOP '+type(exc).__name__+'. Raw results and ledger retained; no retry.')
    finally:
        common={w['index'] for w in record['windows'] if w['direct_status']==w['transcript_status']=='completed'}
        record['common_completed_indices']=sorted(common);record['paired_metrics']={};record['available_metrics']={}
        for arm in ['direct','transcript']:
            for key,ws in [('paired_metrics',[w for w in record['windows'] if w['index'] in common]),('available_metrics',[w for w in record['windows'] if w[arm+'_status']=='completed'])]:
                validids={i for w in ws for i in w['window']['reference_ids']}
                record[key][arm]=score_events([r for r in refs if r['reference_id'] in validids],[e for w in ws for e in w[arm+'_events']])
        record.update(ended_at=now(),elapsed_seconds=time.monotonic()-started)
        if budget is not None:record.update(provider_usage=budget['calls'],attempted_calls=budget['attempted_calls'],estimated_spend_usd=budget['estimated_spend_usd'])
        save()
        summary={k:record.get(k) for k in ['name','started_at','ended_at','status','elapsed_seconds','attempted_calls','estimated_spend_usd','common_completed_indices']}
        summary['paired_metrics']={a:{k:m[k] for k in ['tp','fp','fn','micro_precision','micro_recall','micro_f1','macro_f1','measured_types']} for a,m in record['paired_metrics'].items()}
        note('FINAL '+json.dumps(summary))
        for name in ['all-events-history.jsonl','iteration-log.md']:
            with (ROOT/'evals/iterations'/name).open('a') as f:f.write(('\n### '+now()+' — transcript-pilot-015\n\n' if name.endswith('.md') else '')+json.dumps(summary)+'\n')
        print(json.dumps(summary),flush=True)
    return 0 if record['status']=='completed' else 1
if __name__=='__main__':raise SystemExit(main())
