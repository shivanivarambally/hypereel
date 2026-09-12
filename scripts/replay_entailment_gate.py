"""Offline replay of the pilot015 transcripts through the entailment gate; zero inference.

Measures what the opt-in strict mode WOULD have done to the frozen extraction output, and
scores the gate itself against the recorded auditor verdicts. Never changes run results.
"""
from pathlib import Path
import json
from hypereel.evaluation.transcript import parse_window_extracted_events, screen_extracted_events
from run_evidence_pilot import now
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'evals/iterations/transcript-pilot-015'

report=json.loads((OUT/'report.json').read_text())
audit=json.loads((OUT/'entailment-audit.json').read_text())
verdicts={(r['window_index'],r['label'],round(r['time_seconds'],1)):r['auditor_verdict']
          for r in audit['events'] if r['arm']=='transcript'}
rows=[]
for w in report['windows']:
    core=w['window'];times=[x['time'] for x in w['manifest']]
    calls=[c for c in report['calls'] if c['index']==w['index'] and c['stage']=='extraction' and c.get('raw_completion')]
    raw=calls[0]['raw_completion']['choices'][0]['message']['content']
    inside,outside=parse_window_extracted_events(raw,w['observations'],min(times),max(times),core['start'],core['end'])
    for event in screen_extracted_events(inside+outside,w['observations']):
        key=(w['index'],event['label'],round(event['time_seconds'],1))
        rows.append(dict(window_index=w['index'],label=event['label'],time_seconds=event['time_seconds'],
            observation_ids=event['observation_ids'],kept_by_gate=not event['entailment']['missing'],
            missing_elements=event['entailment']['missing'],cited_hedging=event['entailment']['cited_hedging'],
            cited_visibility=event['entailment']['cited_visibility'],auditor_verdict=verdicts[key]))

kept=[r for r in rows if r['kept_by_gate']]
dropped=[r for r in rows if not r['kept_by_gate']]
entailed=[r for r in rows if r['auditor_verdict']=='entailed']
true_keep=[r for r in kept if r['auditor_verdict']=='entailed']
result=dict(created_at=now(),kind='post_run_offline_replay',inference_calls=0,primary_report_unchanged=True,
    replays='transcript-pilot-015 extraction output through the opt-in entailment gate',
    method='Re-parse retained raw extraction text under the shared boundary policy, apply screen_extracted_events, compare the gate decision with the auditor verdicts already recorded in entailment-audit.json. No inference, no reference change, no report modified.',
    caveat='The gate is a deliberately over-permissive lexical screen, not a correctness test. Surviving an event proves only that outcome/control language is present somewhere in its cited or prior text. This replay measures the gate, on eight events from three windows, which is far too small to set a threshold or claim generalisation.',
    events=rows,
    summary=dict(events=len(rows),kept=len(kept),dropped=len(dropped),
        auditor_entailed=len(entailed),
        gate_kept_and_entailed=len(true_keep),
        gate_kept_but_unsupported=len(kept)-len(true_keep),
        gate_dropped_but_entailed=len([r for r in entailed if not r['kept_by_gate']]),
        gate_precision=len(true_keep)/len(kept) if kept else None,
        gate_recall=len(true_keep)/len(entailed) if entailed else None))
(OUT/'gate-replay.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result['summary'],indent=2))
for r in rows:
    print(f"  w{r['window_index']} {r['label']}@{r['time_seconds']} kept={r['kept_by_gate']} "
          f"missing={r['missing_elements']} auditor={r['auditor_verdict']}")
