"""Observability for what phase 2 does to phase 1's proposals, plus the rules gate.

Phase 1 proposes events; phase 2 confirms, relabels, rejects or routes them to
human review. Until now the only visible artefact was the surviving set, so a
proposal that phase 2 killed left no record of *why*. That made two questions
unanswerable: is verification removing false positives or eating true ones, and
which labels does it disagree with most.

Every phase-1 proposal now produces a :class:`Transition` carrying both labels,
both confidences, the verdict, the verifier's stated reason and any rules
violation that fired. :func:`transition_metrics` aggregates them so a run can be
scored on verification behaviour, not only on final accuracy.

The rules gate lives here too because it is the last thing that can change a
verdict, and its effect must appear in the same record.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field

from ..evaluation.basketball_rules import Violation, validate_sequence

#: Phase-2 outcomes, in order of how much they change phase 1's claim.
CONFIRMED_UNCHANGED = 'confirmed_unchanged'
CORRECTED_RELABEL = 'corrected_relabel'
ROUTED_TO_REVIEW = 'routed_to_review'
REJECTED = 'rejected'
RULES_BLOCKED = 'rules_blocked'


@dataclass
class Transition:
    """One phase-1 proposal and what phase 2 did with it."""
    event_id: str | None
    phase1_label: str | None
    phase1_confidence: float | None
    phase2_label: str | None
    phase2_confidence: float | None
    outcome: str
    verification_reason: str
    expert_review_required: bool
    rule_violations: list[dict] = field(default_factory=list)

    def as_dict(self) -> dict:
        return asdict(self)


def classify_outcome(event) -> str:
    """Bucket one resolved classification by what phase 2 did to it."""
    decision = getattr(event, 'decision', None)
    phase1 = getattr(event, 'phase1_moment_type', None)
    label = getattr(event, 'moment_type', None)
    if decision == 'rejected' or label is None:
        return REJECTED
    if decision == 'potential_event':
        return ROUTED_TO_REVIEW
    if phase1 is not None and label != phase1:
        return CORRECTED_RELABEL
    return CONFIRMED_UNCHANGED


def build_transitions(resolved, violations: list[Violation] | None = None) -> list[Transition]:
    """Record what happened to each proposal, attaching any rule violation."""
    by_index: dict[int, list[Violation]] = {}
    for violation in violations or []:
        for index in violation.event_indices:
            by_index.setdefault(index, []).append(violation)

    transitions = []
    for index, event in enumerate(resolved):
        hits = by_index.get(index, [])
        outcome = classify_outcome(event)
        if any(v.severity == 'illegal' for v in hits) and outcome in {CONFIRMED_UNCHANGED, CORRECTED_RELABEL}:
            outcome = RULES_BLOCKED
        transitions.append(Transition(
            event_id=getattr(event, 'event_id', None),
            phase1_label=getattr(event, 'phase1_moment_type', None),
            phase1_confidence=None,
            phase2_label=getattr(event, 'moment_type', None),
            phase2_confidence=getattr(event, 'confidence', None),
            outcome=outcome,
            verification_reason=(getattr(event, 'verification_reason', '') or '')[:600],
            expert_review_required=bool(getattr(event, 'expert_review_required', False)),
            rule_violations=[{'rule': v.rule, 'severity': v.severity, 'detail': v.detail} for v in hits],
        ))
    return transitions


def apply_rules_gate(resolved):
    """Route events in an illegal combination to human review.

    Never deletes an event: when a pair is illegal, either the shot label or the
    follow-up label is wrong and code cannot tell which, so both are surfaced
    with the rule as the reason rather than one being silently dropped. A
    ``review``-severity violation only raises the expert flag.

    Returns ``(events, violations)``.
    """
    violations = validate_sequence(resolved)
    if not violations:
        return resolved, violations

    illegal: dict[int, list[Violation]] = {}
    flagged: set[int] = set()
    for violation in violations:
        for index in violation.event_indices:
            if violation.severity == 'illegal':
                illegal.setdefault(index, []).append(violation)
            else:
                flagged.add(index)

    out = list(resolved)
    for index, hits in illegal.items():
        if index >= len(out):
            continue
        event = out[index]
        if getattr(event, 'decision', None) == 'rejected':
            continue
        reason = 'RULES: ' + '; '.join(v.detail for v in hits)
        existing = getattr(event, 'verification_reason', '') or ''
        out[index] = event.model_copy(update={
            'decision': 'potential_event',
            'confidence': min(getattr(event, 'confidence', 1.0) or 1.0, 0.49),
            'verification_reason': (reason + (' | ' + existing if existing else ''))[:1000],
            'expert_review_required': True,
        })
    for index in flagged:
        if index < len(out) and index not in illegal:
            out[index] = out[index].model_copy(update={'expert_review_required': True})
    return out, violations


def transition_metrics(transitions) -> dict:
    """Aggregate verification behaviour across a run."""
    outcomes = Counter(t.outcome for t in transitions)
    relabels = Counter(
        f'{t.phase1_label}->{t.phase2_label}' for t in transitions
        if t.outcome == CORRECTED_RELABEL)
    killed_by_label = Counter(
        t.phase1_label for t in transitions
        if t.outcome in {REJECTED, ROUTED_TO_REVIEW, RULES_BLOCKED})
    rules_fired = Counter(
        v['rule'] for t in transitions for v in t.rule_violations)
    total = len(transitions)
    survived = outcomes[CONFIRMED_UNCHANGED] + outcomes[CORRECTED_RELABEL]
    return {
        'proposals': total,
        'outcomes': dict(outcomes),
        'survival_rate': (survived / total) if total else None,
        'relabels': dict(relabels),
        'phase1_labels_not_surviving': dict(killed_by_label),
        'rules_fired': dict(rules_fired),
        'expert_flagged': sum(1 for t in transitions if t.expert_review_required),
    }
