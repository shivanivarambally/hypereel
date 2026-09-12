"""Pilot016: temporal density at fixed image count, both arms, shared boundary policy.

Single declared change from 013/015: frame spacing 2.4s across 12s -> 1.6s across the 8s core.
Model, prompts, references, definitions, matcher and output cap are unchanged.

Unlike 015 this applies the SAME core/context policy to both arms from the outset, and records
the entailment screen inline as a FLAG. The screen never filters: applying it to one arm's
predictions would confound the comparison, so label/time scores stay directly comparable.
"""
from pathlib import Path
import base64, hashlib, json, shutil, time, subprocess, os
from openai import OpenAI
from hypereel.config import get_settings
from hypereel.observability import provider_budget_scope, authorize_provider_call, record_provider_usage
from hypereel.evaluation.basketball_events import parse_window_events, score_events
from hypereel.evaluation.transcript import (observation_prompt, parse_transcript, extraction_prompt,
                                            parse_window_extracted_events, screen_extracted_events)
from run_evidence_pilot import sha, now, pilot_prompt
from eval_nebius_matched import request_arguments
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evals/iterations/dense-pilot-016'
PAIRED=[1,2,6]

def note(message):
    with (ROOT/'evals/IMPLEMENTATION_NOTES.md').open('a') as f:
        f.write('\n### '+now()+' — dense-pilot-016\n\n'+message+'\n')

def main():
    if (OUT/'report.json').exists():raise FileExistsError('No overwrite or automatic rerun')
    prepared=json.loads((OUT/'prepared.json').read_text())
    if prepared['status']!='completed' or len(prepared['windows'])!=8:raise ValueError('Preparation incomplete')
    baseline=json.loads((ROOT/'evals/iterations/evidence-pilot-013/report.json').read_text())
    control=json.loads((ROOT/'evals/iterations/transcript-pilot-015/report.json').read_text())
    fixture=json.loads((ROOT/'evals/experiments/all-events-v2/diagnostic-009.json').read_text())
    if set(fixture['source_files'])!={'east-bay-elite-vs-spartans','unlimited-vs-campus'}:raise ValueError('Source allowlist')
    for g,p in fixture['source_files'].items():
        if sha(ROOT/p)!=baseline['source_sha256'][g]:raise ValueError('Source changed')
    if sha(ROOT/'evals/experiments/all-events-v2/references.jsonl')!=baseline['reference_sha256']:raise ValueError('References changed')
    refs=baseline['scored_references']
    plan=dict(name='dense-pilot-016',created_at=now(),indices=[w['index'] for w in prepared['windows']],
        model='openbmb/MiniCPM-V-4_5',
        hypothesis='Sparse evidence, not the output representation, is the binding constraint. Six frames1.6s apart across the8s core should improve event recognition over six frames2.4s apart across12s, in BOTH the direct and transcript arms.',
        declared_change='Frame timestamps only. Same6 images, same768px/JPEG85 decode path, same prompts, model, temperature0, seed0, output cap1536, references, definitions and five-second one-to-one matcher.',
        known_confound='At the6-image provider limit found in013, density and span cannot be varied independently. The dense arm gains temporal resolution and loses the2s outer context either side. A difference cannot be attributed to density alone.',
        boundary_policy='Identical for both arms from the outset via parse_window_events and parse_window_extracted_events. For the dense arm the context span equals the core window, so no context events are possible by construction.',
        entailment='Recorded inline as a flag via screen_extracted_events. NEVER filters. The screen is over-permissive and is not a correctness test; gate-replay.json measured it at precision0.50 on eight015 events.',
        controls='013 wide6_context direct across all8 windows (same model/prompt/output cap) and015 direct plus transcript across windows1,2,6.',
        budget=dict(max_calls=24,cumulative_ceiling=8,reserve_per_call=.30),output_limit=1536,temperature=0,seed=0,
        failures='No retries. Record the failed window/stage; skip dependent extraction if narration is invalid; continue independent windows unless transport or budget failure.',
        holdout_used=False,reference_sha256=baseline['reference_sha256'],source_sha256=baseline['source_sha256'],
        prepared_sha256=sha(OUT/'prepared.json'))
    (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    for p in [Path(__file__),ROOT/'scripts/prepare_dense_pilot.py',ROOT/'src/hypereel/evaluation/transcript.py',
              ROOT/'src/hypereel/evaluation/basketball_events.py']:
        shutil.copy2(p,OUT/(p.name+'.snapshot'))
    settings=get_settings();settings.max_provider_calls=24;settings.max_provider_spend_usd=8;settings.provider_call_reserve_usd=.30
    settings.nebius_input_cost_per_million_usd=10;settings.nebius_output_cost_per_million_usd=30
    settings.provider_spend_ledger_path=str(ROOT/'evals/iterations/spend-ledger.json');settings.provider_checkpoint_dir=str(OUT/'checkpoints')
    if settings.nebius_base_url.rstrip('/')!='https://api.studio.nebius.com/v1':raise ValueError('Endpoint mismatch')
    spent=json.loads(Path(settings.provider_spend_ledger_path).read_text())['estimated_spend_usd']
    if not 0<=spent<8:raise ValueError('Invalid or exhausted ledger')
    client=OpenAI(api_key=settings.nebius_api_key,base_url=settings.nebius_base_url,max_retries=0,timeout=180)
    record=dict(name=plan['name'],started_at=now(),status='running',plan=plan,plan_sha256=sha(OUT/'plan.json'),
        scored_references=refs,spend_before_usd=spent,calls=[],windows=[],holdout_used=False)
    def save():
        p=OUT/'report.tmp';p.write_text(json.dumps(record,indent=2)+'\n');p.replace(OUT/'report.json')
    def call(stage,index,prompt,images,budget):
        entry=dict(stage=stage,index=index,started_at=now(),status='started',prompt=prompt,
            prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
            image_sha256=[hashlib.sha256(base64.b64decode(i)).hexdigest() for i in images])
        record['calls'].append(entry);save()
        authorize_provider_call(provider='nebius',model=plan['model'],operation='dense_pilot_'+stage)
        ts=time.monotonic()
        try:
            args=request_arguments(images,prompt);args['max_tokens']=1536
            response=client.chat.completions.create(**args)
        except Exception as exc:
            entry.update(status='provider_error',error_type=type(exc).__name__,error_text=str(exc)[:2000],ended_at=now())
            pending=budget['calls'][-1];pending.update(status='error',usage_unknown=True,estimated_cost_usd=.30,error_type=type(exc).__name__)
            budget['estimated_spend_usd']+=.30
            Path(settings.provider_spend_ledger_path).write_text(json.dumps({'estimated_spend_usd':budget['estimated_spend_before_run_usd']+budget['estimated_spend_usd']})+'\n')
            budget['journal'].append('unknown_usage_reserved',call=pending);save()
            note(f'Window {index} {stage} PROVIDER ERROR {type(exc).__name__}: {str(exc)[:400]}. Reserve retained, no retry.')
            raise
        entry.update(raw_completion=response.model_dump(),ended_at=now(),latency_seconds=time.monotonic()-ts,status='received')
        save();budget['journal'].append('dense_raw_response',**entry)
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
        note(f'window {index}, {stage}, received at {entry["ended_at"]}, latency {entry["latency_seconds"]:.2f}s, '
             f'{response.usage.total_tokens} tokens. Raw output:\n\n```json\n'+raw+'\n```')
        if not response.choices or response.choices[0].finish_reason!='stop':raise ValueError('Incomplete output')
        return raw
    note('PREDECLARED START. Owner raised the ceiling to $8 and asked for the necessary changes and a conclusion. '
         +json.dumps(plan)+f' Reference support: {len(refs)} events across {len({r["label"] for r in refs})} types over8 windows. '
         'No reference enters any prompt. Both arms share one boundary policy from the outset. Entailment is recorded, never filtered.')
    save();started=time.monotonic();budget=None
    try:
        with provider_budget_scope(settings,checkpoint_context=plan) as budget:
            for w in prepared['windows']:
                core=w['window'];items=w['frames'];times=[x['time'] for x in items];images=[]
                for x in items:
                    if sha(ROOT/x['path'])!=x['sha256']:raise RuntimeError('Image changed since preparation')
                    images.append(base64.b64encode((ROOT/x['path']).read_bytes()).decode())
                entry=dict(index=w['index'],window=core,manifest=items,spacing_seconds=w['spacing_seconds'],
                    direct_status='not_started',transcript_status='not_started',narration_status='not_started')
                record['windows'].append(entry);save()
                try:
                    raw=call('direct',w['index'],pilot_prompt(w,items),images,budget)
                    inside,outside=parse_window_events(raw,min(times),max(times),core['start'],core['end'])
                    entry['direct_events']=[dict(e,game_id=core['game_id']) for e in inside]
                    entry['direct_context_events']=outside;entry['direct_status']='completed'
                except ValueError as exc:
                    entry.update(direct_status='invalid',direct_error=str(exc));note(f'Window {w["index"]} direct invalid: {exc}. No retry.')
                save()
                try:
                    raw=call('narration',w['index'],observation_prompt(times),images,budget)
                    rows=parse_transcript(raw,times);entry['observations']=rows;entry['narration_status']='completed';save()
                    raw=call('extraction',w['index'],extraction_prompt(rows,core['start'],core['end']),[],budget)
                    inside,outside=parse_window_extracted_events(raw,rows,min(times),max(times),core['start'],core['end'])
                    entry['transcript_events']=[dict(e,game_id=core['game_id']) for e in screen_extracted_events(inside,rows)]
                    entry['transcript_context_events']=screen_extracted_events(outside,rows)
                    entry['transcript_status']='completed'
                except ValueError as exc:
                    entry.update(transcript_status='invalid',transcript_error=str(exc))
                    note(f'Window {w["index"]} transcript branch invalid: {exc}. No retry, no dependent extraction after invalid narration.')
                entry['ended_at']=now();save()
                note('WINDOW COMPLETE '+json.dumps({k:v for k,v in entry.items() if k!='manifest'}))
                print(json.dumps({k:v for k,v in entry.items() if k not in ('manifest','observations')}),flush=True)
        record['status']='completed' if all(w['direct_status']==w['transcript_status']=='completed' for w in record['windows']) else 'completed_with_invalid_windows'
    except BaseException as exc:
        record.update(status='stopped',error_type=type(exc).__name__)
        note('STOP '+type(exc).__name__+'. Raw results and ledger retained; no retry.')
    finally:
        record['metrics']={}
        def scored(ws,arm):
            ids={i for x in ws for i in x['window']['reference_ids']}
            return score_events([r for r in refs if r['reference_id'] in ids],
                                [{k:v for k,v in e.items() if k!='entailment'} for x in ws for e in x[arm+'_events']])
        for label,indices in [('all_windows',[w['index'] for w in prepared['windows']]),('paired_with_015',PAIRED)]:
            common={w['index'] for w in record['windows']
                    if w['index'] in indices and w['direct_status']==w['transcript_status']=='completed'}
            ws=[w for w in record['windows'] if w['index'] in common]
            record['metrics'][label]=dict(indices=sorted(common),
                **{arm:scored(ws,arm) for arm in ('direct','transcript')})
        screened=[e for w in record['windows'] if w.get('transcript_events') for e in w['transcript_events']]
        record['entailment_screen']=dict(note='Recorded, never filtered. Over-permissive lexical screen; not a correctness test.',
            events=len(screened),supported=sum(1 for e in screened if e['entailment']['screen']=='supported'),
            unsupported=sum(1 for e in screened if e['entailment']['screen']=='unsupported'),
            clear_but_hedged=sum(1 for w in record['windows'] for o in w.get('observations',[])
                                 if o['visibility']=='clear' and any(t in o['observation'].lower() for t in ('uncertain','possibly','unclear','appears','might','seems'))),
            observations=sum(len(w.get('observations',[])) for w in record['windows']))
        record.update(ended_at=now(),elapsed_seconds=time.monotonic()-started)
        if budget is not None:record.update(provider_usage=budget['calls'],attempted_calls=budget['attempted_calls'],estimated_spend_usd=budget['estimated_spend_usd'])
        save()
        summary={k:record.get(k) for k in ['name','started_at','ended_at','status','elapsed_seconds','attempted_calls','estimated_spend_usd']}
        summary['metrics']={k:{'indices':v['indices'],**{a:{m:v[a][m] for m in ('tp','fp','fn','micro_precision','micro_recall','micro_f1','macro_f1')} for a in ('direct','transcript')}} for k,v in record['metrics'].items()}
        summary['entailment_screen']=record['entailment_screen']
        note('FINAL '+json.dumps(summary))
        for name in ['all-events-history.jsonl','iteration-log.md']:
            with (ROOT/'evals/iterations'/name).open('a') as f:
                f.write(('\n### '+now()+' — dense-pilot-016\n\n' if name.endswith('.md') else '')+json.dumps(summary)+'\n')
        print(json.dumps(summary,indent=2),flush=True)
    return 0 if record['status']=='completed' else 1
if __name__=='__main__':raise SystemExit(main())
