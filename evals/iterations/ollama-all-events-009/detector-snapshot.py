"""Versioned all-event detection and scoring, independent of reel selection.

Point matching is provisional until external clip times receive action audits.
No reference labels or timestamps are included in the detector prompt.
"""
from __future__ import annotations
import json
from math import isfinite
from pydantic import BaseModel, ConfigDict, Field
from ..providers.ollama import OllamaVisionProvider

DEFINITIONS = {
 'two_point_made': 'A two-point field-goal attempt visibly scores.',
 'two_point_miss': 'A two-point field-goal attempt visibly misses.',
 'three_point_made': 'A shot from beyond the three-point arc visibly scores.',
 'three_point_miss': 'A shot from beyond the three-point arc visibly misses.',
 'free_throw_made': 'A free-throw attempt visibly scores.',
 'free_throw_miss': 'A free-throw attempt visibly misses.',
 'offensive_rebound': 'The shooting team gains control after its missed shot.',
 'defensive_rebound': 'The defending team gains control after an opponent missed shot.',
 'steal': 'A defender intercepts or disrupts opponent possession and gains team control.',
 'turnover': 'A team loses possession through an error, violation, or opponent steal; not a normal shot/rebound.',
 'block': 'A defender visibly deflects an opponent shot attempt.',
 'assist': 'A pass directly leads to a teammate made field goal; both pass and made shot must be supported.',
}
LABELS = tuple(sorted(DEFINITIONS))

class Event(BaseModel):
    model_config = ConfigDict(extra='forbid')
    label: str
    time_seconds: float = Field(allow_inf_nan=False)
    confidence: float = Field(ge=0, le=1, allow_inf_nan=False)
    evidence: str = Field(min_length=1, max_length=600)


def parse_events(text: str, start: float, end: float) -> list[Event]:
    obj = json.loads(text)
    if not isinstance(obj, dict) or set(obj) != {'events'} or not isinstance(obj['events'], list):
        raise ValueError('Expected exactly an events array')
    if len(obj['events']) > 12:
        raise ValueError('Too many events for one bounded window')
    result = [Event.model_validate(e) for e in obj['events']]
    for e in result:
        if e.label not in LABELS or not start <= e.time_seconds <= end:
            raise ValueError('Unknown label or event outside observed interval')
    return result


def build_prompt(times: list[float], variant: str = 'direct') -> str:
    if variant not in {'direct', 'evidence_first'}:
        raise ValueError('Unknown prompt variant')
    definitions = '\n'.join(f'{k}: {v}' for k,v in DEFINITIONS.items())
    evidence = ('First follow the ball through each image: which team controls it, whether a shot is attempted, '
                'whether the ball scores/misses, and which team controls it afterward. Use this progression '
                'to identify events. A change after a missed shot is a rebound, not automatically a steal.\n'
                if variant == 'evidence_first' else '')
    return (f'Analyze ALL basketball events in these chronological images, not just highlights. '
            f'Image source times in seconds: {times}.\n{evidence}{definitions}\n'
            'Return every supported event, including multiple different events in the same sequence. '
            'A steal and opponent turnover may coexist; a missed shot and a rebound may coexist. '
            'Do not infer a basket from a scoreboard. Do not invent an event hidden between images. '
            'Do not treat an uncertain event as a confirmed one. Use the nearest supported action time. '
            'Return only JSON: {"events":[{"label":"one exact label above","time_seconds":0.0,'
            '"confidence":0.8,"evidence":"brief visible evidence"}]}. '
            'If no event is supported, return {"events":[]}.')


class OllamaEventDetector(OllamaVisionProvider):
    def detect(self, paths: list[str], times: list[float], variant: str = 'direct', on_response=None):
        if len(paths) != len(times) or not paths or times != sorted(times):
            raise ValueError('Each ordered image needs its own timestamp')
        prompt = build_prompt(times, variant)
        raw = self._client.chat([{'role':'user','content':prompt,'images':self._images(paths)}],
                                operation='basketball_event_detection_v2', json_mode=True)
        if on_response is not None:
            on_response(raw)
        return raw, parse_events(raw, times[0], times[-1])


def score_events(references: list[dict], predictions: list[dict], tolerance: float = 5.0) -> dict:
    """Maximum-cardinality one-to-one same-type point matching.

    Duplicate predictions remain unmatched false positives. Do not allow one
    prediction to explain multiple reference events, including paired labels.
    """
    if not isfinite(tolerance) or tolerance < 0:
        raise ValueError('Invalid time tolerance')
    for rows in (references, predictions):
        for row in rows:
            if row['label'] not in LABELS or not isfinite(row['time_seconds']):
                raise ValueError('Invalid scoring event')
    by_type = {}; matches=[]
    for label in LABELS:
        rs=[i for i,r in enumerate(references) if r['label']==label]
        ps=[i for i,p in enumerate(predictions) if p['label']==label]
        edges={p:sorted([r for r in rs if predictions[p]['game_id']==references[r]['game_id'] and abs(predictions[p]['time_seconds']-references[r]['time_seconds'])<=tolerance],key=lambda r:abs(predictions[p]['time_seconds']-references[r]['time_seconds'])) for p in ps}
        assigned={}
        def augment(p,seen):
            for r in edges[p]:
                if r in seen:continue
                seen.add(r)
                if r not in assigned or augment(assigned[r],seen):
                    assigned[r]=p;return True
            return False
        for p in ps:augment(p,set())
        tp=len(assigned);fp=len(ps)-tp;fn=len(rs)-tp
        by_type[label]={'tp':tp,'fp':fp,'fn':fn,'support':len(rs),'predictions':len(ps),
                        'precision':tp/(tp+fp) if tp+fp else None,
                        'recall':tp/(tp+fn) if tp+fn else None,
                        'f1':2*tp/(2*tp+fp+fn) if rs or ps else None}
        matches.extend({'reference_index':r,'prediction_index':p} for r,p in assigned.items())
    tp=sum(v['tp'] for v in by_type.values());fp=sum(v['fp'] for v in by_type.values());fn=sum(v['fn'] for v in by_type.values())
    supported=[v for v in by_type.values() if v['support']]
    return {'metric_version':'basketball-events-point-v2-provisional','tolerance_seconds':tolerance,
            'per_type':by_type,'matches':matches,'tp':tp,'fp':fp,'fn':fn,
            'micro_precision':tp/(tp+fp) if tp+fp else None,
            'micro_recall':tp/(tp+fn) if tp+fn else None,
            'micro_f1':2*tp/(2*tp+fp+fn) if tp+fp+fn else None,
            'macro_f1':sum(v['f1'] for v in supported)/len(supported) if supported else None,
            'worst_type_recall':min(v['recall'] for v in supported) if supported else None,
            'measured_types':len(supported),'total_required_types':len(LABELS),
            'release_gate_pass':False,'release_gate_reason':'Diagnostic point timestamps are unaudited; representative held-out development coverage required'}
