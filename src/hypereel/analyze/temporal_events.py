"""Strict temporal schema and fail-closed verification, independent of reference data."""
from __future__ import annotations

import json

from ..evaluation.basketball_rules import rules_prompt_text
import math

from ..models import Classification
from .two_phase import EXPERT_LABELS, INCOMPLETE_EVIDENCE

MAX_EVENTS = 12


def event_rows(raw):
    data = json.loads(raw)
    rows = data['events']
    if not isinstance(rows, list) or len(rows) > MAX_EVENTS:
        raise ValueError('Invalid or oversized event list')
    return rows


def parse_event(row, recipe, window, clip_start):
    label = row['moment_type']
    if label not in {m.name for m in recipe.moment_types}:
        raise ValueError('Unknown event label')
    timestamp = float(row['time_seconds']) + clip_start
    confidence = float(row['confidence'])
    if not math.isfinite(timestamp) or not window.start <= timestamp <= window.end:
        raise ValueError('Event outside candidate interval')
    if not math.isfinite(confidence) or not 0 <= confidence <= 1:
        raise ValueError('Invalid confidence')
    if not isinstance(row.get('subject_present'), bool):
        raise ValueError('Invalid subject flag')
    if row.get('team') is not None and not isinstance(row['team'], str):
        raise ValueError('Invalid team')
    reason = row['reason']
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError('Missing evidence')
    return Classification(moment_type=label, event_time=timestamp,
                          subject_present=row['subject_present'], confidence=confidence,
                          team=row.get('team'), reason=reason[:1000])


def parse_discovery(raw, recipe, window, clip_start, window_index):
    events = []
    for i, row in enumerate(event_rows(raw)):
        event = parse_event(row, recipe, window, clip_start)
        events.append(event.model_copy(update={
            'event_id': f'w{window_index}e{i}', 'source_window_index': window_index,
            'phase1_moment_type': event.moment_type, 'phase1_event_time': event.event_time,
        }))
    return events


def potential(event, reason):
    text = reason.lower()
    return event.model_copy(update={
        'decision': 'potential_event', 'confidence': min(event.confidence, .49),
        'verification_reason': reason,
        'expert_review_required': event.moment_type in EXPERT_LABELS or any(
            word in text for word in ('foul', 'referee', 'statistical rule')),
    })


def parse_verification(raw, proposals, recipe, window, clip_start):
    rows = event_rows(raw)
    by_id = {}
    for row in rows:
        event_id = row['event_id']
        if event_id in by_id or event_id not in {p.event_id for p in proposals}:
            raise ValueError('Duplicate or unknown verification event ID')
        by_id[event_id] = row
    results = []
    for proposal in proposals:
        row = by_id.get(proposal.event_id)
        result = potential(proposal, 'UNCERTAIN: missing verification result')
        if row is not None:
            reason = str(row.get('reason') or 'UNCERTAIN: missing evidence')
            uncertain = not row.get('reason') or reason.lower().startswith('uncertain:') or any(
                term in reason.lower() for term in INCOMPLETE_EVIDENCE)
            status = row.get('status')
            result = potential(proposal, reason)
            if status == 'rejected' and not uncertain:
                result = result.model_copy(update={'moment_type': None, 'decision': 'rejected'})
            elif status in {'confirmed', 'corrected'} and not uncertain:
                try:
                    checked = parse_event(row, recipe, window, clip_start)
                    if status == 'confirmed' and checked.moment_type != proposal.moment_type:
                        raise ValueError('Relabel requires corrected status')
                    if abs(checked.event_time - proposal.event_time) > 2:
                        raise ValueError('Verifier substituted a different action time')
                    result = checked.model_copy(update={
                        'event_id': proposal.event_id, 'source_window_index': proposal.source_window_index,
                        'phase1_moment_type': proposal.moment_type,
                        'phase1_event_time': proposal.event_time,
                        'decision': 'confirmed', 'verification_reason': reason,
                        'expert_review_required': result.expert_review_required or checked.moment_type in EXPERT_LABELS,
                    })
                except (ValueError, KeyError, TypeError):
                    result = potential(proposal, 'UNCERTAIN: invalid verification event; '+reason)
        results.append(result)
    return results


def discovery_prompt(recipe, window, clip_start):
    rubric = {m.name: m.description for m in recipe.moment_types}
    return (
        'PHASE 1: Enumerate distinct basketball events in temporal order from continuous video. '
        'Optimize candidate recall: include visually plausible uncertain events; do not invent events '
        'merely because they usually follow another. Several labels may describe one possession '
        '(e.g. steal then shot, missed shot then rebound). Repeated attempts are separate events. '
        'Do not force one label per clip. Return an empty events array for no plausible event. '
        'Follow ball possession, release, flight, rim/net interaction, and next control across time. '
        'A rebound is not a steal. Shot outcome and point value are separate; use generic field-goal '
        'labels when available and value cannot be seen. Use null team when attribution is unclear. '
        'Do not infer a score from a delayed scoreboard or invent jersey identities. '
        # Rule constraints are a constant, not a retrieval: the governing rule set is one
        # page and closed, so fetching it per window would add a failure mode for no gain.
        # W1 motivated this — a player collecting a MADE free throw was reported as a
        # defensive rebound in all eight runs, which then back-inferred a missed shot.
        + rules_prompt_text() +
        f'Subject selection: {recipe.subject_selector.model_dump_json()}. Rubric: {json.dumps(rubric)}. '
        f'Only event anchors between {window.start-clip_start} and {window.end-clip_start} '
        'seconds relative to THIS supplied clip (00:00=0), not game clock. For shots anchor outcome; '
        'for possession changes anchor control; for blocks anchor contact; for an ASSIST anchor the moment of the PASS, not the resulting basket. Surrounding footage is context. '
        f'Return at most {MAX_EVENTS} events. JSON only: '
        '{"events":[{"moment_type":"rubric_label","time_seconds":1.2,"team":null,'
        '"subject_present":true,"confidence":0.7,"reason":"visible evidence and any uncertainty"}]}'
    )


def verification_prompt(recipe, window, clip_start, proposals):
    claims = [dict(event_id=p.event_id, moment_type=p.moment_type,
                   time_seconds=p.event_time-clip_start, team=p.team) for p in proposals]
    return (
        'PHASE 2: Independently inspect the continuous video to verify EVERY proposed event ID. '
        + rules_prompt_text() +
        'Proposals are fallible hypotheses, not evidence. Follow ball and team possession in order. '
        'Confirm only when the defining action/outcome is visible. Correct the label if this SAME '
        'action is visibly another rubric event (e.g. free throw rather than field goal). Never '
        'replace a proposal with an unrelated event; keep its ID, adjust time by at most 2 seconds. '
        'Use the same anchors as phase 1: shots at the outcome, possession changes at control, blocks at contact, an ASSIST at the moment of the PASS. '
        'Reject only on visible contradiction. Missing, off-camera, occluded or ambiguous evidence '
        'means potential_event, NOT rejected. Unknown point value may use a generic field-goal label. '
        'An unclear foul/referee/statistical ruling means potential_event for expert review. '
        'Do not add proposals or drop IDs. Explain concrete video evidence, not agreement with proposal. '
        f'Rubric: {json.dumps({m.name:m.description for m in recipe.moment_types})}. '
        f'Subject: {recipe.subject_selector.model_dump_json()}. '
        f'Event times must be clip-relative seconds between {window.start-clip_start} '
        f'and {window.end-clip_start}. Proposals: {json.dumps(claims)}. '
        'JSON only: {"events":[{"event_id":"w0e0","status":"confirmed|corrected|potential_event|rejected",'
        '"moment_type":"rubric_label","time_seconds":1.2,"team":null,"subject_present":true,'
        '"confidence":0.8,"reason":"visible action and outcome evidence"}]}'
    )
