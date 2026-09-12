"""Versioned primitive contract: explicit releases, outcomes and interceptions.

Model states remain predictions, not verified facts. No automatic claim of grounding.
Old ball_state.py and executed017 snapshots remain unchanged.
"""
import json
from math import isfinite
from .ball_state import SHOT_LABELS
STATES=('held','shot_release','pass_release','in_flight','rim_contact','through_net','missed','interception','defensive_touch','loose','not_visible')
FIELDS={'time_seconds','ball_state','team','player','release_zone'}

def prompt(times,views):
 return ('Report visual basketball primitives for each timestamp, not event labels. '+
  f'Timestamps: {json.dumps(times)}. Image manifest: {json.dumps(views)}. '+
  'A wide and rim crop at the same time are the SAME instant. A missing crop is not evidence of no shot. '+
  'Return JSON {"frames":[...]} with exactly one chronological row per timestamp. Each row has exactly '+
  'time_seconds,ball_state,team,player,release_zone. Team is jersey color or unknown; player is readable jersey number or unknown. '+
  'ball_state must be one of: held (visible control); shot_release (visible ball release towards basket); '+
  'pass_release (visible pass release towards teammate); in_flight (airborne, purpose unclear); '+
  'rim_contact (visible contact); through_net (ball visibly going down through basket); '+
  'missed (ball visibly passes outside/beyond basket without scoring, including airball; being in the air or touching rim alone is insufficient); '+
  'interception (defender visibly takes control of opponent pass/dribble); defensive_touch (visible defender contact without control); '+
  'loose (visible uncontrolled ball); not_visible (cannot locate ball or state uncertain). '+
  'For shot_release ONLY, release_zone is shooter location at release: free_throw_line (visible free-throw setup), inside_arc, beyond_arc, or unknown. '+
  'All other rows must use release_zone=unknown. Never use airborne ball location as release zone. '+
  'Team means current controlling/touching/releasing team; use unknown for unattended airborne ball if unclear. '+
  'Do not infer from scoreboard, posture alone, unseen action between images, or previous score. Unknown is allowed. '+
  'These are sampled frames; do not invent transitions. No explanatory text or extra fields.')

def parse(raw,times):
 obj=json.loads(raw)
 if not isinstance(obj,dict):raise ValueError('Expected state object')
 if set(obj)=={'frames'}:rows=obj['frames']
 elif obj and all(isinstance(v,dict) for v in obj.values()):
  keys=sorted(obj,key=float)
  if len(keys)!=len(times) or any(abs(float(k)-t)>.05 for k,t in zip(keys,times)):raise ValueError('Wrong timestamp keys')
  rows=[obj[k] for k in keys]
 else:raise ValueError('Expected frames list or timestamp-keyed rows')
 if not isinstance(rows,list) or len(rows)!=len(times):raise ValueError('Exactly one row per timestamp required')
 for r,t in zip(rows,times):
  if not isinstance(r,dict) or set(r)!=FIELDS:raise ValueError('Wrong state fields')
  x=r['time_seconds']
  if isinstance(x,bool) or not isinstance(x,(int,float)) or not isfinite(x) or abs(x-t)>.05:raise ValueError('Wrong timestamp')
  if r['ball_state'] not in STATES or r['release_zone'] not in (*SHOT_LABELS,'unknown'):raise ValueError('Unknown state or zone')
  if r['ball_state']!='shot_release' and r['release_zone']!='unknown':raise ValueError('Zone only belongs to release')
  for k in ['team','player']:
   if not isinstance(r[k],str) or not 1<=len(r[k].strip())<=40:raise ValueError('Invalid identity')
   r[k]=r[k].strip().lower()
 return rows

def derive(rows,start,end):
 events=[];notes=[];shot=None;rebound=None;holder=None;passed=None
 def known(x):return bool(x) and x!='unknown'
 def emit(label,t,evidence):
  if start<=t<=end:events.append(dict(label=label,time_seconds=t,confidence=1.,evidence=evidence))
  else:notes.append(f'{label}@{t} outside core, retained as context only')
 def finish(made,t):
  nonlocal shot,rebound,passed
  if shot is None:notes.append(f'Outcome@{t} lacks an explicit shot release');return
  z=shot['release_zone']
  if z in SHOT_LABELS:emit(SHOT_LABELS[z][0 if made else 1],t,f'Predicted explicit release@{shot["time_seconds"]} from {z}, outcome@{t}')
  else:notes.append(f'Outcome@{t} with unknown shooter zone; no typed shot')
  if made and passed and known(passed['team']) and passed['team']==shot['team'] and known(passed['player']) and known(shot['player']) and passed['player']!=shot['player'] and 0<=shot['time_seconds']-passed['time_seconds']<=8:
   emit('assist',t,'Predicted pass by distinct teammate followed by release and made outcome; bounded heuristic, not official assist adjudication')
  rebound=None if made else shot['team'];shot=None;passed=None
 for r in rows:
  s=r['ball_state'];t=r['time_seconds'];team=r['team']
  if s=='not_visible':
   if shot:notes.append(f'Outcome unobserved across gap@{t}; reset shot')
   shot=None;holder=None;passed=None;rebound=None
  elif s=='shot_release':
   if shot:notes.append(f'Prior release unresolved before new release@{t}')
   shot=r;rebound=None
  elif s=='pass_release':shot=None;rebound=None;passed=r;holder=team if known(team) else None
  elif s=='through_net':finish(True,t)
  elif s=='missed':finish(False,t)
  elif s=='held':
   if rebound and known(rebound) and known(team):emit('offensive_rebound' if team==rebound else 'defensive_rebound',t,'Predicted explicit miss followed by observed control');rebound=None
   elif rebound:notes.append(f'Rebound team unknown@{t}');rebound=None
   if shot:notes.append(f'Control@{t} without explicit outcome; shot unresolved');shot=None
   if holder and known(team) and holder!=team and not passed:notes.append(f'Possession changed@{t} without observed cause; no steal/turnover')
   if passed and known(team) and team!=passed['team']:notes.append(f'Opposing control@{t} without interception evidence');passed=None
   holder=team if known(team) else None
  elif s=='interception':
   prior=passed['team'] if passed else holder
   if shot or rebound:notes.append(f'Interception-like state@{t} during shot/rebound; ambiguous, not steal')
   elif known(team) and known(prior) and team!=prior:
    emit('steal',t,'Predicted defensive interception following opponent control/pass');emit('turnover',t,'Opponent loses control in predicted interception')
   else:notes.append(f'Interception@{t} without known opposing prior possession')
   holder=team if known(team) else None;passed=None
  elif s=='defensive_touch':
   if shot and known(team) and known(shot['team']) and team!=shot['team']:
    emit('block',t,'Predicted defender contact during explicit opponent shot');shot=None;passed=None;rebound=None
   else:notes.append(f'Defensive touch@{t} does not establish a block or steal')
  # in_flight/rim_contact/loose never imply outcome; retain explicit release until contrary evidence.
 if shot:notes.append('Sequence ends with unresolved shot')
 return events,notes
