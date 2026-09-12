"""Offline interpretation and boundary sensitivity; never changes original run results."""
from pathlib import Path
import json
from hypereel.evaluation.transcript import parse_extracted_events
from hypereel.evaluation.basketball_events import score_events
from run_evidence_pilot import now
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'evals/iterations/transcript-pilot-015'
d=json.loads((OUT/'report.json').read_text())
audit=dict(created_at=now(),kind='post_run_offline_audit',inference_calls=0,
    primary_report_unchanged=True,
    method='Agent visual inspection of all18 supplied frames as three contact sheets, plus entailment inspection of raw transcript/extraction. Qualitative observations, not independent human audit or new golden labels.',
    findings=[
      'All18 transcript rows use visibility=clear, including text saying possibly or uncertain. Metadata does not reliably represent uncertainty.',
      'Window1 narrative describes black-team shooting near the three-point line; supplied images show a blue-uniform player at the free-throw line. Free-throw setup recognition is wrong. Sparse frames do not independently settle every shot outcome.',
      'Window2 at758.8s shows a black-uniform ball handler near midcourt with blue defenders; narration calls this a shot towards the basket. At763.6s black players remain visible although narration says the black player is no longer in frame. This establishes visual-description errors without altering reference times.',
      'Window6 narration repeats ball-in-air descriptions across most frames instead of distinguishing the changing action. Initial claim of white control is questionable: first image shows ball near a yellow-uniform player. Exact full action sequence is not reannotated from these sparse samples.',
      'All6 accepted transcript-branch events have citations that do not establish their claimed outcome/control: ball-in-air is used for misses and rebounds; one uncertain-outcome row becomes an offensive rebound. All6 events have confidence1.0.',
      'All3 transcript label/time matches occur in window6. None of their cited observations establishes the event. Better reference matching here does not establish better grounded recognition.',
      'Window1 extraction includes233s outside core223–231; original parser rejects whole extraction. Direct parser accepts observed-context times then filters to core. This asymmetric boundary handling is a pilot limitation, not a model recognition failure alone.'
    ])
# Apply the same original direct-branch context/filter policy to retained extraction text.
# Supplemental only: do not replace predeclared primary metrics or modify report.json.
preds=[];valid=[]
for w in d['windows']:
    calls=[c for c in d['calls'] if c['index']==w['index'] and c['stage']=='extraction' and c.get('raw_completion')]
    if not calls or 'observations' not in w:continue
    raw=calls[0]['raw_completion']['choices'][0]['message']['content']
    times=[x['time'] for x in w['manifest']]
    events=parse_extracted_events(raw,w['observations'],min(times),max(times))
    core=w['window'];preds.extend(dict(e,game_id=core['game_id']) for e in events if core['start']<=e['time_seconds']<=core['end']);valid.append(w['index'])
ids={i for w in d['windows'] if w['index'] in valid for i in w['window']['reference_ids']};refs=[r for r in d['scored_references'] if r['reference_id'] in ids]
audit['boundary_sensitivity']=dict(description='Post-hoc same context/filter policy for both arms; no new inference. Primary strict failure remains recorded.',indices=valid,transcript=score_events(refs,preds),direct=score_events(refs,[e for w in d['windows'] if w['index'] in valid for e in w['direct_events']]))
(OUT/'observation-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print(json.dumps({a:{k:m[k] for k in ['tp','fp','fn','micro_precision','micro_recall','micro_f1','macro_f1']} for a,m in audit['boundary_sensitivity'].items() if a in ['direct','transcript']}))
