"""Offline re-derivation of pilot017 from retained raw text; zero inference.

POST-HOC and labelled as such. Four of eight 017 windows failed strict parsing because the model
returned a timestamp-keyed object instead of {"frames": [...]}. The per-frame content was valid.
parse_states was extended to accept that serialisation; every semantic check — vocabulary, court
zone, one entry per image, timestamp agreement — is unchanged, and the unsound assist rule was
removed. This re-derives from the preserved completions rather than paying for an identical
re-run at temperature 0 and seed 0.

report.json keeps the original strict outcome. Nothing here replaces it.
"""
from pathlib import Path
import json
from hypereel.evaluation.ball_state import contradictory_pairs, derive_events, parse_states
from hypereel.evaluation.basketball_events import score_events
from run_evidence_pilot import now
ROOT=Path(__file__).resolve().parents[1]
D17=ROOT/'evals/iterations/state-pilot-017'
D16=ROOT/'evals/iterations/dense-pilot-016'
D13=ROOT/'evals/iterations/evidence-pilot-013'

state=json.loads((D17/'report.json').read_text())
dense=json.loads((D16/'report.json').read_text())
pilot13=json.loads((D13/'report.json').read_text())
refs={r['reference_id']:r for r in state['scored_references']}

windows=[];notes=[];states_seen=[]
for w in state['windows']:
    core=w['window'];times=[x['time'] for x in w['manifest']]
    call=[c for c in state['calls'] if c['index']==w['index'] and c.get('raw_completion')][0]
    raw=call['raw_completion']['choices'][0]['message']['content']
    rows=parse_states(raw,times)
    events,why=derive_events(rows,core['start'],core['end'])
    if contradictory_pairs(events):raise AssertionError('Derivation produced contradictory labels')
    windows.append(dict(index=w['index'],game_id=core['game_id'],reference_ids=core['reference_ids'],
        states=rows,events=[dict(e,game_id=core['game_id']) for e in events],derivation_notes=why,
        originally=w['status']))
    notes+=why;states_seen+=rows

ids={i for w in windows for i in w['reference_ids']}
preds=[e for w in windows for e in w['events']]
derived=score_events([refs[i] for i in sorted(ids)],preds)

# Controls on the SAME eight windows.
d16_direct=[e for w in dense['windows'] if w['direct_status']=='completed' for e in w['direct_events']]
d16_ids={i for w in dense['windows'] if w['direct_status']=='completed' for i in w['window']['reference_ids']}
d13_direct=[dict(e,game_id=w['window']['game_id']) for w in pilot13['windows']
            if w['arm']=='wide6_context' and w['status']=='completed' for e in w['events']]
d13_ids={i for w in pilot13['windows'] if w['arm']=='wide6_context' and w['status']=='completed'
         for i in w['window']['reference_ids']}

from collections import Counter
out=dict(created_at=now(),kind='post_run_offline_reparse',inference_calls=0,primary_report_unchanged=True,
    reparses='state-pilot-017',
    change='parse_states now also accepts the timestamp-keyed object the model actually returned. Serialisation shape only; vocabulary, court-zone, per-image and timestamp validation are unchanged. The assist rule was removed as unsound: consecutive held frames by one team are continued possession, not an observed pass.',
    honesty='Post-hoc after observing outputs. The original strict result (4 of 8 windows invalid, 0 events, recall 0) stands in report.json and is not replaced. No semantic validation was relaxed to admit any event.',
    windows_reparsed=len(windows),windows_originally_valid=sum(1 for w in windows if w['originally']=='completed'),
    state_distribution=dict(Counter(r['ball_state'] for r in states_seen)),
    zone_distribution=dict(Counter(r['court_zone'] for r in states_seen)),
    team_known=sum(1 for r in states_seen if r['team'] not in ('unknown','')),
    frames=len(states_seen),
    derivation=dict(events=len(preds),notes=len(notes),contradictory_pairs=0,
        note='Notes record every point where no event was emitted because the evidence did not support one.'),
    metrics=dict(references=len(ids),derived_017=derived,
        dense_016_direct=score_events([refs[i] for i in sorted(d16_ids)],d16_direct),
        sparse_013_direct=score_events([refs[i] for i in sorted(d13_ids)],d13_direct)),
    windows=windows,
    finding='The model reported through_net or rim_contact in almost no frame. Constrained to report only what it can see, it does not report shot outcomes at all, which is why the derivation emits almost nothing. The outcomes the earlier pilots scored were asserted, not observed.')
(D17/'reparse.json').write_text(json.dumps(out,indent=2)+'\n')

def brief(m):
    return {k:(round(m[k],5) if isinstance(m[k],float) else m[k]) for k in ('tp','fp','fn','micro_precision','micro_recall','micro_f1','macro_f1')}
print(json.dumps(dict(frames=out['frames'],states=out['state_distribution'],zones=out['zone_distribution'],
    team_known=out['team_known'],derived_events=len(preds),derivation_notes=len(notes),
    references=len(ids),metrics={k:brief(v) for k,v in out['metrics'].items() if k!='references'}),indent=2))
for w in windows:
    print(f"  w{w['index']}: {[(e['label'],e['time_seconds']) for e in w['events']]}  "
          f"refs={[(refs[i]['label'],refs[i]['time_seconds']) for i in w['reference_ids']]}")
