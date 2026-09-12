"""021 post-hoc formatting-only analysis; original strict report untouched."""
import json,re,hashlib
from pathlib import Path
from hypereel.evaluation.basketball_events import parse_events,score_events
from run_gemini_pilot import ROOT,OUT,now,note,write

def unfence(s):
 m=re.fullmatch(r'\s*```(?:json)?\s*\n([\s\S]*?)\n```\s*',s)
 return m.group(1) if m else s

def main():
 p=OUT/'report.json';r=json.loads(p.read_text());assert r['status']!='running'
 result={'created_at':now(),'classification':'post_hoc_formatting_only_not_primary','original_report_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rule':'Remove a single outer Markdown json code fence only, for every arm including historical control. No event edits, filters, repairs or inference.','windows':[],'metrics':{}}
 controls=r['historical_control']; refs=r['scored_references']
 for arm in ['historical_minicpm','images','video']:
  rows=controls if arm=='historical_minicpm' else [c for c in r['calls'] if c['arm']==arm]
  for row in rows:
   core=row['window'];control=next(w for w in controls if w['index']==row['index']);lo=min(m['time'] for m in control['manifest']);hi=max(m['time'] for m in control['manifest'])
   raw=row.get('raw',row.get('raw_text',''));entry={'arm':arm,'index':row['index'],'window':core,'fence_removed':raw!=unfence(raw)}
   try:
    events=[dict(e.model_dump(),game_id=core['game_id']) for e in parse_events(unfence(raw),lo,hi)]
    entry.update(status='completed',events=[e for e in events if core['start']<=e['time_seconds']<=core['end']],context_events=[e for e in events if not core['start']<=e['time_seconds']<=core['end']])
   except ValueError as e:entry.update(status='invalid',error=str(e))
   result['windows'].append(entry)
 common=[i for i in [1,2,6] if all(any(w['index']==i and w['arm']==a and w['status']=='completed' for w in result['windows']) for a in ['historical_minicpm','images','video'])];result['common_completed_indices']=common
 ids={i for w in controls if w['index'] in common for i in w['window']['reference_ids']};refs=[x for x in refs if x['reference_id'] in ids]
 for arm in ['historical_minicpm','images','video']:result['metrics'][arm]=score_events(refs,[e for w in result['windows'] if w['arm']==arm and w['index'] in common for e in w['events']])
 write(OUT/'reparse.json',result);note('Formatting-only secondary analysis '+json.dumps({a:{k:m[k] for k in ['tp','fp','fn','micro_precision','micro_recall','micro_f1']} for a,m in result['metrics'].items()}));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
