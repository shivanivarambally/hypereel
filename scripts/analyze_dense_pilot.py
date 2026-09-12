"""Offline like-for-like analysis of pilot016 against its 013 and 015 controls; zero inference.

report.json is left exactly as written. This adds the comparisons its own metrics block cannot
express, and records one naming correction: that block's 'all_windows' key actually covers the
windows where BOTH arms completed, which is four of eight, not all eight.
"""
from pathlib import Path
import json
from hypereel.evaluation.basketball_events import score_events
from hypereel.evaluation.transcript import parse_window_extracted_events
from run_evidence_pilot import now
ROOT=Path(__file__).resolve().parents[1]
D16=ROOT/'evals/iterations/dense-pilot-016'
D15=ROOT/'evals/iterations/transcript-pilot-015'
D13=ROOT/'evals/iterations/evidence-pilot-013'

dense=json.loads((D16/'report.json').read_text())
sparse=json.loads((D15/'report.json').read_text())
pilot13=json.loads((D13/'report.json').read_text())
refs={r['reference_id']:r for r in dense['scored_references']}


def strip(events):
    return [{k:v for k,v in e.items() if k!='entailment'} for e in events]


def measure(reference_ids, predictions):
    return score_events([refs[i] for i in sorted(reference_ids) if i in refs], predictions)


def sparse_parity(indices):
    """Re-derive the 015 arms on `indices` under the shared boundary policy. No new inference."""
    ids=set();direct=[];transcript=[]
    for w in sparse['windows']:
        if w['index'] not in indices:continue
        core=w['window'];times=[x['time'] for x in w['manifest']]
        ids|=set(core['reference_ids'])
        direct+=[dict(e,game_id=core['game_id']) for e in w.get('direct_events',[])]
        calls=[c for c in sparse['calls'] if c['index']==w['index'] and c['stage']=='extraction' and c.get('raw_completion')]
        raw=calls[0]['raw_completion']['choices'][0]['message']['content']
        inside,_=parse_window_extracted_events(raw,w['observations'],min(times),max(times),core['start'],core['end'])
        transcript+=[dict(e,game_id=core['game_id']) for e in inside]
    return ids,direct,transcript


out=dict(created_at=now(),kind='post_run_offline_analysis',inference_calls=0,primary_report_unchanged=True,
    analyses='dense-pilot-016',
    naming_correction="dense-pilot-016/report.json metrics.all_windows is labelled misleadingly. Its indices are the windows where BOTH arms completed, [0,1,3,6], not all eight. Four extraction outputs were invalid so their windows are absent. The report is left unchanged and the correction recorded here; the direct arm completed 8/8 and is measured across all eight below.",
    comparisons={})

# 1. Direct arm, all eight windows, dense016 vs sparse013. Same model, prompt, output cap and windows.
d13=[dict(e,game_id=w['window']['game_id']) for w in pilot13['windows']
     if w['arm']=='wide6_context' and w['status']=='completed' for e in w['events']]
ids13={i for w in pilot13['windows'] if w['arm']=='wide6_context' and w['status']=='completed'
       for i in w['window']['reference_ids']}
d16=[e for w in dense['windows'] if w['direct_status']=='completed' for e in w['direct_events']]
ids16={i for w in dense['windows'] if w['direct_status']=='completed' for i in w['window']['reference_ids']}
out['comparisons']['direct_all_eight_windows']=dict(
    description='Direct arm only, all eight frozen windows, 14 references. Identical model, prompt template, temperature, seed and 1536 output cap; only the frame timestamps differ.',
    sparse_013=dict(indices=sorted({w['index'] for w in pilot13['windows'] if w['arm']=='wide6_context' and w['status']=='completed'}),
                    references=len(ids13),metrics=measure(ids13,d13)),
    dense_016=dict(indices=sorted({w['index'] for w in dense['windows'] if w['direct_status']=='completed'}),
                   references=len(ids16),metrics=measure(ids16,d16)))

# 2. Both arms on the windows where dense016 completed both AND sparse015 has data.
common=sorted({w['index'] for w in dense['windows'] if w['direct_status']==w['transcript_status']=='completed'}
              & {w['index'] for w in sparse['windows'] if w['direct_status']=='completed' and 'observations' in w})
sids,sdirect,stranscript=sparse_parity(common)
dwin=[w for w in dense['windows'] if w['index'] in common]
dids={i for w in dwin for i in w['window']['reference_ids']}
assert sids==dids, (sids,dids)
out['comparisons']['both_arms_paired']=dict(
    description='Windows where pilot016 completed both arms and pilot015 also ran. Sparse figures are re-derived from retained 015 raw output under the SAME boundary policy, so the only difference is frame timestamps.',
    indices=common,references=len(dids),
    sparse_015=dict(direct=measure(sids,sdirect),transcript=measure(sids,stranscript)),
    dense_016=dict(direct=measure(dids,[e for w in dwin for e in w['direct_events']]),
                   transcript=measure(dids,strip([e for w in dwin for e in w['transcript_events']]))))

# 3. Operational and evidence-quality comparison.
def hedged(windows,key='observations'):
    rows=[o for w in windows for o in w.get(key,[])]
    flags=[o for o in rows if o['visibility']=='clear' and any(t in o['observation'].lower()
           for t in ('uncertain','possibly','unclear','appears','might','seems','unknown'))]
    return len(rows),len(flags)
s_obs,s_hedge=hedged(sparse['windows']);d_obs,d_hedge=hedged(dense['windows'])
screened=[e for w in dense['windows'] if w.get('transcript_events') for e in w['transcript_events']]
out['operational']=dict(
    dense_016=dict(calls=dense['attempted_calls'],provider_errors=0,
        direct_valid=sum(1 for w in dense['windows'] if w['direct_status']=='completed'),
        narration_valid=sum(1 for w in dense['windows'] if w['narration_status']=='completed'),
        extraction_valid=sum(1 for w in dense['windows'] if w['transcript_status']=='completed'),
        extraction_failures=[dict(index=w['index'],error=w['transcript_error']) for w in dense['windows'] if w.get('transcript_error')],
        observations=d_obs,clear_but_hedged=d_hedge,
        screened_events=len(screened),screen_supported=sum(1 for e in screened if e['entailment']['screen']=='supported'),
        elapsed_seconds=dense['elapsed_seconds'],estimated_spend_usd=dense['estimated_spend_usd']),
    sparse_015=dict(calls=sparse['attempted_calls'],provider_errors=0,
        direct_valid=sum(1 for w in sparse['windows'] if w['direct_status']=='completed'),
        narration_valid=sum(1 for w in sparse['windows'] if w.get('narration_status')=='completed'),
        extraction_valid=sum(1 for w in sparse['windows'] if w['transcript_status']=='completed'),
        observations=s_obs,clear_but_hedged=s_hedge,
        elapsed_seconds=sparse['elapsed_seconds'],estimated_spend_usd=sparse['estimated_spend_usd']),
    note='Extraction validity is a SCHEMA outcome, not a quality measure. A window with no valid extraction contributes no predictions and is excluded from paired scoring; it is never counted as a correct empty result.')

# 4. Outcome hedging: mutually exclusive labels emitted for the same action.
EXCLUSIVE=[{'two_point_made','two_point_miss'},{'three_point_made','three_point_miss'},
           {'free_throw_made','free_throw_miss'},{'offensive_rebound','defensive_rebound'}]

def hedging(windows,getter):
    """Count contradictory label pairs. Within-window pairs matter because one-to-one matching
    credits whichever guess is right while the other only costs a false positive."""
    within=0;tolerance=0;examples=[];hit=set()
    for w in windows:
        events=getter(w) or []
        for i,a in enumerate(events):
            for b in events[i+1:]:
                if {a['label'],b['label']} not in EXCLUSIVE:continue
                within+=1;hit.add(w['index'])
                if abs(a['time_seconds']-b['time_seconds'])<=5.0:tolerance+=1
                if len(examples)<12:
                    examples.append(f"w{w['index']} {a['label']}@{a['time_seconds']} vs {b['label']}@{b['time_seconds']}")
    return dict(pairs_in_window=within,pairs_within_tolerance=tolerance,windows_affected=len(hit),examples=examples)

out['outcome_hedging']=dict(
    description='A made/miss or offensive/defensive pair for one action cannot both be true. Under one-to-one same-label matching the correct member scores a true positive and the other costs only a false positive, so hedging raises recall without any recognition.',
    dense_016_direct=hedging(dense['windows'],lambda w:w.get('direct_events')),
    dense_016_transcript=hedging(dense['windows'],lambda w:w.get('transcript_events')),
    sparse_015_direct=hedging(sparse['windows'],lambda w:w.get('direct_events')),
    sparse_015_transcript=hedging(sparse['windows'],lambda w:w.get('transcript_events')),
    sparse_013_direct=hedging([w for w in pilot13['windows'] if w['arm']=='wide6_context'],lambda w:w.get('events')))

out['caveats']=[
 'Two of the four common windows (0 and 3) carry zero references and are not verified negatives, so they can only add false positives. Effective reference support in the paired comparison is small.',
 'Density and span are coupled at the six-image provider limit: the dense arm gains temporal resolution and loses the two-second outer context. A difference cannot be attributed to density alone.',
 'With the dense span equal to the core window there is no context margin, so an event outside the core cannot be reclassified as context. Window4 extraction failed exactly this way, a consequence of the design rather than of the boundary policy.',
 'Window0 dense transcript output emitted all four mutually exclusive pairs at one timestamp, which is enumeration of the label set rather than recognition.',
 'These are label/time matches on provisional external clip timestamps, not visually confirmed detections, over two development games and single-digit per-type support. No gate is passed.',
]
(D16/'analysis.json').write_text(json.dumps(out,indent=2)+'\n')

def brief(m):
    return {k:(round(m[k],5) if isinstance(m[k],float) else m[k]) for k in ('tp','fp','fn','micro_precision','micro_recall','micro_f1','macro_f1')}
print(json.dumps(dict(
 direct_all_eight={k:dict(references=v['references'],**brief(v['metrics'])) for k,v in out['comparisons']['direct_all_eight_windows'].items() if k!='description'},
 paired=dict(indices=common,references=len(dids),
   sparse_015={a:brief(m) for a,m in out['comparisons']['both_arms_paired']['sparse_015'].items()},
   dense_016={a:brief(m) for a,m in out['comparisons']['both_arms_paired']['dense_016'].items()}),
 operational={k:{kk:vv for kk,vv in v.items() if kk!='extraction_failures'} for k,v in out['operational'].items() if k!='note'}),indent=2))
