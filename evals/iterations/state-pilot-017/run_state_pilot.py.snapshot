"""Pilot017: grounded state derivation. The model reports ball state; code derives events.

Single declared change from 016: the SAME dense frames, the same model and decoding settings,
but the model is no longer asked what events happened. It reports per-frame ball state from a
closed vocabulary and events are derived deterministically in src/hypereel/evaluation/ball_state.py.

Predeclared expectation: precision rises sharply because an unseen outcome yields nothing, and
recall falls for the same reason. Contradictory label pairs become impossible by construction.
A fall in recall is a real cost and is reported, not explained away.
"""
from pathlib import Path
import base64, hashlib, json, shutil, time, subprocess, os
from openai import OpenAI
from hypereel.config import get_settings
from hypereel.observability import provider_budget_scope, authorize_provider_call, record_provider_usage
from hypereel.evaluation.basketball_events import score_events
from hypereel.evaluation.ball_state import contradictory_pairs, derive_events, parse_states, state_prompt
from run_evidence_pilot import sha, now
from eval_nebius_matched import request_arguments
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evals/iterations/state-pilot-017'
DENSE=ROOT/'evals/iterations/dense-pilot-016'

def note(message):
    with (ROOT/'evals/IMPLEMENTATION_NOTES.md').open('a') as f:
        f.write('\n### '+now()+' — state-pilot-017\n\n'+message+'\n')

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'report.json').exists():raise FileExistsError('No overwrite or automatic rerun')
    prepared=json.loads((DENSE/'prepared.json').read_text())
    dense=json.loads((DENSE/'report.json').read_text())
    if prepared['status']!='completed' or len(prepared['windows'])!=8:raise ValueError('Preparation incomplete')
    refs=dense['scored_references']
    plan=dict(name='state-pilot-017',created_at=now(),indices=[w['index'] for w in prepared['windows']],
        model='openbmb/MiniCPM-V-4_5',
        hypothesis='The binding failure is assertion under uncertainty, not evidence sparsity. Asking only for per-frame ball state and deriving events in code should raise precision substantially and eliminate contradictory labels, at a cost in recall.',
        declared_change='Output contract only. Identical dense frames from016 (same JPEG bytes), same model, temperature0, seed0, output cap1536, references, definitions and five-second one-to-one matcher. The model no longer names events.',
        derivation='Deterministic transitions in src/hypereel/evaluation/ball_state.py. A shot outcome requires an observed through_net, or observed rim_contact followed by observed possession. An unknown court zone yields no typed shot. A possession change is a turnover only with no shot in between. Every non-emission is recorded as a derivation note.',
        structural_properties='Mutually exclusive labels are impossible by construction. A scoreboard cannot produce an event because it is not in the vocabulary.',
        expected_cost='Recall is expected to fall. That is the declared trade and will be reported as a loss, not reframed.',
        controls='016 dense direct and transcript arms on the identical images; 013 sparse direct across the same eight windows.',
        budget=dict(max_calls=8,cumulative_ceiling=8,reserve_per_call=.30),output_limit=1536,temperature=0,seed=0,
        failures='No retries. Record the failed window; continue independent windows unless transport or budget failure.',
        holdout_used=False,prepared_sha256=sha(DENSE/'prepared.json'))
    (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    for p in [Path(__file__),ROOT/'src/hypereel/evaluation/ball_state.py',ROOT/'src/hypereel/evaluation/basketball_events.py']:
        shutil.copy2(p,OUT/(p.name+'.snapshot'))
    settings=get_settings();settings.max_provider_calls=8;settings.max_provider_spend_usd=8;settings.provider_call_reserve_usd=.30
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
    def call(index,prompt,images,budget):
        entry=dict(stage='ball_state',index=index,started_at=now(),status='started',prompt=prompt,
            prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
            image_sha256=[hashlib.sha256(base64.b64decode(i)).hexdigest() for i in images])
        record['calls'].append(entry);save()
        authorize_provider_call(provider='nebius',model=plan['model'],operation='state_pilot_ball_state')
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
            note(f'Window {index} PROVIDER ERROR {type(exc).__name__}: {str(exc)[:400]}. Reserve retained, no retry.');raise
        entry.update(raw_completion=response.model_dump(),ended_at=now(),latency_seconds=time.monotonic()-ts,status='received')
        save();budget['journal'].append('state_raw_response',**entry)
        if response.usage is None:
            pending=budget['calls'][-1];pending.update(status='error',usage_unknown=True,estimated_cost_usd=.30)
            budget['estimated_spend_usd']+=.30
            Path(settings.provider_spend_ledger_path).write_text(json.dumps({'estimated_spend_usd':budget['estimated_spend_before_run_usd']+budget['estimated_spend_usd']})+'\n')
            raise RuntimeError('Missing usage; reserve retained')
        record_provider_usage(response,status='success' if response.choices and response.choices[0].finish_reason=='stop' else 'incomplete')
        entry['client_rss_kib']=int(subprocess.check_output(['ps','-o','rss=','-p',str(os.getpid())],text=True).strip())
        record['provider_usage']=budget['calls'];save()
        raw=response.choices[0].message.content or '' if response.choices else ''
        note(f'window {index}, ball_state, received at {entry["ended_at"]}, latency {entry["latency_seconds"]:.2f}s, '
             f'{response.usage.total_tokens} tokens. Raw output:\n\n```json\n'+raw+'\n```')
        if not response.choices or response.choices[0].finish_reason!='stop':raise ValueError('Incomplete output')
        return raw
    note('PREDECLARED START. Architectural change: the model reports ball state only and code derives events. '
         +json.dumps(plan)+f' Same {sum(len(w["frames"]) for w in prepared["windows"])} JPEGs as016, byte-identical. '
         f'Reference support: {len(refs)} events over8 windows. No reference enters the prompt. '
         'Recall is expected to fall and will be reported as a loss.')
    save();started=time.monotonic();budget=None
    try:
        with provider_budget_scope(settings,checkpoint_context=plan) as budget:
            for w in prepared['windows']:
                core=w['window'];items=w['frames'];times=[x['time'] for x in items];images=[]
                for x in items:
                    if sha(ROOT/x['path'])!=x['sha256']:raise RuntimeError('Image changed since preparation')
                    images.append(base64.b64encode((ROOT/x['path']).read_bytes()).decode())
                entry=dict(index=w['index'],window=core,manifest=items,status='not_started')
                record['windows'].append(entry);save()
                try:
                    raw=call(w['index'],state_prompt(times),images,budget)
                    states=parse_states(raw,times)
                    events,notes=derive_events(states,core['start'],core['end'])
                    contradictions=contradictory_pairs(events)
                    if contradictions:raise AssertionError(f'Derivation produced contradictory labels: {contradictions}')
                    entry.update(states=states,events=[dict(e,game_id=core['game_id']) for e in events],
                                 derivation_notes=notes,contradictory_pairs=contradictions,status='completed')
                except ValueError as exc:
                    entry.update(status='invalid',error=str(exc));note(f'Window {w["index"]} invalid: {exc}. No retry.')
                entry['ended_at']=now();save()
                note('WINDOW COMPLETE '+json.dumps({k:v for k,v in entry.items() if k!='manifest'}))
                print(json.dumps({k:v for k,v in entry.items() if k!='manifest'}),flush=True)
        record['status']='completed' if all(w['status']=='completed' for w in record['windows']) else 'completed_with_invalid_windows'
    except BaseException as exc:
        record.update(status='stopped',error_type=type(exc).__name__)
        note('STOP '+type(exc).__name__+'. Raw results and ledger retained; no retry.')
    finally:
        done=[w for w in record['windows'] if w['status']=='completed']
        ids={i for w in done for i in w['window']['reference_ids']}
        record['metrics']=dict(indices=[w['index'] for w in done],references=len(ids),
            derived=score_events([r for r in refs if r['reference_id'] in ids],[e for w in done for e in w['events']]))
        record['derivation']=dict(events=sum(len(w['events']) for w in done),
            notes=sum(len(w['derivation_notes']) for w in done),
            contradictory_pairs=sum(len(w['contradictory_pairs']) for w in done),
            note='Derivation notes record every point where no event was emitted because the evidence did not support one. They are lost recall made visible, not errors.')
        record.update(ended_at=now(),elapsed_seconds=time.monotonic()-started)
        if budget is not None:record.update(provider_usage=budget['calls'],attempted_calls=budget['attempted_calls'],estimated_spend_usd=budget['estimated_spend_usd'])
        save()
        summary={k:record.get(k) for k in ['name','started_at','ended_at','status','elapsed_seconds','attempted_calls','estimated_spend_usd']}
        summary['metrics']=dict(indices=record['metrics']['indices'],references=record['metrics']['references'],
            **{m:record['metrics']['derived'][m] for m in ('tp','fp','fn','micro_precision','micro_recall','micro_f1','macro_f1')})
        summary['derivation']={k:v for k,v in record['derivation'].items() if k!='note'}
        note('FINAL '+json.dumps(summary))
        for name in ['all-events-history.jsonl','iteration-log.md']:
            with (ROOT/'evals/iterations'/name).open('a') as f:
                f.write(('\n### '+now()+' — state-pilot-017\n\n' if name.endswith('.md') else '')+json.dumps(summary)+'\n')
        print(json.dumps(summary,indent=2),flush=True)
    return 0 if record['status']=='completed' else 1
if __name__=='__main__':raise SystemExit(main())
