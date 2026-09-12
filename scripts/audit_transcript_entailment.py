"""Offline entailment audit of pilot015; never changes original run results.

Answers a question the label/time scorer cannot: are the extracted events actually
supported by the evidence they cite? Citation validation only proves an observation ID
exists. Reads report.json, writes one new sibling JSON, performs zero inference.
"""
from pathlib import Path
import json
from hypereel.evaluation.basketball_events import score_events
from hypereel.evaluation.transcript import entailment_elements, hedging_tokens, parse_window_extracted_events
from run_evidence_pilot import now
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'evals/iterations/transcript-pilot-015'

# Auditor judgements, keyed (window, arm, label, time). These are agent inspection of the
# frozen transcript and evidence text, not independent human reannotation and not new labels.
# transcript arm: 'entailed' = every required element established by the frozen transcript.
# direct arm: 'asserted' = its own evidence claims the required elements. That is a WEAKER and
# non-equivalent bar; the direct arm cites no frozen text, so entailment cannot be checked.
VERDICTS={
 (1,'transcript','two_point_miss',228.2):('entailed',False,
  "o4 states the ball makes contact with the rim and bounces off, an observed non-scoring outcome, and the same row refers to players reacting to the shot, so the citation supplies both required elements on its own and is complete. Entailed by the transcript is not visually correct: the015 contact-sheet audit found this window is a free-throw setup narrated as a shot near the three-point line, so this is a faithful extraction from a false narration."),
 (1,'transcript','offensive_rebound',233.0):('unsupported',False,
  "o6 says a player in blue is seen with the ball 'possibly after a rebound'. Control is explicitly hedged, and blue is the defending team relative to the black shooter in o1/o2, so even at face value this describes a defensive rebound. No observation establishes the shooting team regaining control."),
 (2,'transcript','two_point_miss',758.8):('unsupported',False,
  "o3 establishes an attempt and the ball in the air, never an outcome. The next observation o4 explicitly states the outcome of the shot is uncertain, so the transcript contradicts rather than supports a miss."),
 (2,'transcript','offensive_rebound',761.2):('unsupported',False,
  "o4 has the ball still in the air and says the outcome is uncertain. No preceding miss, no control gained, no team attribution."),
 (2,'transcript','defensive_rebound',763.6):('unsupported',False,
  "o5 and o6 describe the ball in the air with an uncertain trajectory. Neither observation has any player controlling the ball."),
 (6,'transcript','two_point_miss',1316.4):('unsupported',False,
  "o2 is an attempt in flight. 'Players in yellow are ready to rebound' is anticipation, not an observed outcome."),
 (6,'transcript','offensive_rebound',1323.6):('unsupported',False,
  "o5 has the ball still in the air. No control is gained by anyone and no preceding miss is observed."),
 (6,'transcript','defensive_rebound',1323.6):('unsupported',False,
  "Cites the identical observation o5 at the identical timestamp as the offensive rebound above. The two labels are mutually exclusive and cannot both follow from one observation."),
 (1,'direct','two_point_miss',223.4):('asserted',False,
  "Claims the ball does not go through the hoop. Both required elements are asserted, but this is unverifiable model self-report about an image, with no citation into frozen text."),
 (1,'direct','defensive_rebound',223.4):('unsupported',False,
  "Reuses the same sentence as the two_point_miss above at the same timestamp and appends a control claim. A rebound placed on the shot-release frame is temporally incoherent, and one sentence cannot evidence two distinct actions at one instant."),
 (2,'direct','two_point_made',756.4):('unsupported',True,
  "Infers a basket from the scoreboard, which build_prompt explicitly forbids. No shot attempt and no observed outcome."),
 (2,'direct','defensive_rebound',758.8):('unsupported',False,
  "Asserts possession by a black-uniform player after a missed shot, but black is the team attempting the shot in this sequence, so the claimed defensive attribution contradicts the action it describes. The miss itself is asserted, never observed."),
 (2,'direct','two_point_made',761.2):('unsupported',True,
  "Scoreboard inference, and the score quoted is 7-0, unchanged from the 756.4 event that already claimed a basket. An unchanged score cannot evidence a second basket."),
 (2,'direct','defensive_rebound',763.6):('unsupported',False,
  "Evidence string is byte-identical to the 758.8 defensive rebound. Repeated identical text is not a distinct observed action."),
 (2,'direct','two_point_made',766.0):('unsupported',True,
  "Scoreboard inference with the same unchanged 7-0 score; third claimed basket from one static scoreboard."),
 (6,'direct','two_point_made',1316.4):('unsupported',True,
  "Infers a score change from a scoreboard reading, explicitly forbidden. Ball near the basket is not an outcome."),
 (6,'direct','defensive_rebound',1318.8):('asserted',False,
  "Asserts a prior white shot attempt, yellow gaining control, and the team identity. All required elements are claimed, but unverifiable self-report rather than entailment."),
 (6,'direct','two_point_made',1321.2):('unsupported',True,
  "Self-contradictory: states the scoreboard is unchanged and then suggests another score from the ball being in the air."),
 (6,'direct','defensive_rebound',1323.6):('asserted',False,
  "Asserts yellow gaining possession after a missed shot with team identity. Claimed, not observed; the miss is never independently evidenced."),
}

d=json.loads((OUT/'report.json').read_text())
rows=[];observations=[];by_arm={'direct':[],'transcript':[]}
for w in d['windows']:
    core=w['window'];times=[x['time'] for x in w['manifest']]
    for o in w.get('observations',[]):
        hedges=hedging_tokens(o['observation'])
        observations.append(dict(window_index=w['index'],observation_id=o['observation_id'],time_seconds=o['time_seconds'],
            visibility=o['visibility'],hedging_tokens=hedges,
            visibility_conflicts_with_text=bool(hedges) and o['visibility']=='clear',observation=o['observation']))
    calls=[c for c in d['calls'] if c['index']==w['index'] and c['stage']=='extraction' and c.get('raw_completion')]
    if not calls or 'observations' not in w:raise RuntimeError(f'Missing retained extraction for window {w["index"]}')
    raw=calls[0]['raw_completion']['choices'][0]['message']['content']
    inside,outside=parse_window_extracted_events(raw,w['observations'],min(times),max(times),core['start'],core['end'])
    cited={o['observation_id']:o for o in w['observations']}
    events=[('transcript',e,True) for e in inside]+[('transcript',e,False) for e in outside]
    events+=[('direct',e,True) for e in w.get('direct_events',[])]+[('direct',e,False) for e in w.get('direct_context_events',[])]
    for arm,e,in_core in events:
        ids=e.get('observation_ids',[])
        texts=[cited[i]['observation'] for i in ids] if ids else [e['evidence']]
        prior=[o['observation'] for o in w['observations'] if o['time_seconds']<=e['time_seconds']] if ids else [e['evidence']]
        required,found,missing=entailment_elements(e['label'],texts,prior)
        key=(w['index'],arm,e['label'],round(e['time_seconds'],1))
        if key not in VERDICTS:raise RuntimeError(f'No recorded auditor verdict for {key}')
        verdict,prohibited,reason=VERDICTS[key]
        row=dict(window_index=w['index'],game_id=core['game_id'],arm=arm,label=e['label'],time_seconds=e['time_seconds'],
            in_core_window=in_core,observation_ids=ids,cited_text=texts,
            cited_visibility=[cited[i]['visibility'] for i in ids],
            required_elements=required,lexical_found=found,lexical_missing=missing,
            lexical_verdict='supported' if not missing else 'unsupported',
            auditor_verdict=verdict,prohibited_inference=prohibited,citation_complete=not ids or not missing,
            auditor_reason=reason,model_confidence=e['confidence'],matched_reference_id=None)
        rows.append(row);by_arm[arm].append(row)
        if in_core:row['_scored']=True

# Label/time matching under the Part1 parity policy, so entailment can be crossed with matches.
indices=[w['index'] for w in d['windows']]
ids={i for w in d['windows'] for i in w['window']['reference_ids']}
refs=[r for r in d['scored_references'] if r['reference_id'] in ids]
parity={};gated={}
for arm in ('direct','transcript'):
    scored=[r for r in by_arm[arm] if r.get('_scored')]
    preds=[dict(label=r['label'],time_seconds=r['time_seconds'],confidence=r['model_confidence'],
                evidence='',game_id=r['game_id']) for r in scored]
    parity[arm]=score_events(refs,preds)
    for m in parity[arm]['matches']:
        scored[m['prediction_index']]['matched_reference_id']=refs[m['reference_index']]['reference_id']
    keep='entailed' if arm=='transcript' else 'asserted'
    survivors=[(r,p) for r,p in zip(scored,preds) if r['auditor_verdict']==keep and not r['prohibited_inference']]
    gated[arm]=dict(kept=len(survivors),of=len(scored),bar=keep,metrics=score_events(refs,[p for _,p in survivors]))
for r in rows:r.pop('_scored',None)

matched=[r for r in rows if r['matched_reference_id']]
audit=dict(created_at=now(),kind='post_run_offline_audit',inference_calls=0,primary_report_unchanged=True,
    audits='transcript-pilot-015',boundary_policy='Part1 parity: parse over the observed context span, then split on the core window. Recovers window1, which the original asymmetric parser discarded whole.',
    method='Agent inspection of the frozen transcript, cited observation text and event evidence in report.json, plus a deliberately over-permissive lexical screen. Not independent human reannotation, not new golden labels, no reference label or timestamp altered.',
    layer_asymmetry='A MISSING lexical element is strong evidence a citation does not entail its event. A FOUND element is NOT evidence that it does. The auditor verdict is authoritative; the screen only bounds it. Disagreement in both directions is expected and counted.',
    arm_asymmetry="Transcript events cite a frozen transcript, so entailment is checkable. Direct events carry only a self-reported evidence sentence about images, so the best available verdict is 'asserted': its own text claims the required elements. That is a weaker, non-equivalent bar and the two arms' gated results are NOT a clean paired comparison.",
    events=rows,observations=observations,
    aggregates=dict(
        events_audited=len(rows),
        by_arm={a:dict(total=len(v),
            **{k:sum(1 for r in v if r['auditor_verdict']==k) for k in ('entailed','asserted','unsupported')},
            prohibited_inference=sum(1 for r in v if r['prohibited_inference']),
            lexical_supported=sum(1 for r in v if r['lexical_verdict']=='supported'),
            lexical_disagrees_with_auditor=sum(1 for r in v if (r['lexical_verdict']=='supported')!=(r['auditor_verdict'] in ('entailed','asserted'))))
            for a,v in by_arm.items()},
        confidence_by_verdict={a:sorted({r['model_confidence'] for r in v if r['auditor_verdict']=='unsupported'}) for a,v in by_arm.items()},
        observations_total=len(observations),
        observations_flagged_clear_but_hedged=sum(1 for o in observations if o['visibility_conflicts_with_text']),
        matches_total=len(matched),
        matches_entailed=sum(1 for r in matched if r['auditor_verdict']=='entailed'),
        matches_asserted=sum(1 for r in matched if r['auditor_verdict']=='asserted'),
        matches_unsupported=sum(1 for r in matched if r['auditor_verdict']=='unsupported')),
    matched_events=[{k:r[k] for k in ('window_index','arm','label','time_seconds','matched_reference_id','auditor_verdict','model_confidence')} for r in matched],
    boundary_parity_metrics=dict(description='Label/time scoring under the Part1 parity policy over all three windows. Reproduces the post-hoc numbers already recorded in observation-audit.json; recorded here only so the entailment cross-tab has a matching denominator.',indices=indices,**parity),
    entailment_gated_diagnostic=dict(
        caveat='SECONDARY DIAGNOSTIC. Never a replacement for report.json paired_metrics or available_metrics, which are unchanged. It quantifies how much of each reported score rests on evidence that survives inspection, and it is expected to lower scores, not raise them. The two arms are gated at different, non-equivalent bars (see arm_asymmetry) and must not be read as a clean paired result.',
        indices=indices,**gated))
(OUT/'entailment-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print(json.dumps(dict(aggregates=audit['aggregates'],
    parity={a:{k:m[k] for k in ('tp','fp','fn','micro_f1')} for a,m in parity.items()},
    gated={a:dict(kept=g['kept'],of=g['of'],bar=g['bar'],**{k:g['metrics'][k] for k in ('tp','fp','fn','micro_f1')}) for a,g in gated.items()}),indent=2))
