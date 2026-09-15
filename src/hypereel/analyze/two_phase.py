"""Resolve discovery/verification outputs and build a human-review queue."""
from __future__ import annotations

from ..models import CandidateWindow, Classification, PotentialEvent


EXPERT_LABELS = {"assist", "block", "turnover"}

# A verifier's REJECTED prefix is not sufficient when its explanation says
# the decisive evidence could not be seen. Keep such claims for human review.
INCOMPLETE_EVIDENCE = (
    'off-camera', 'off camera', 'unviewable', 'occluded', 'obscured',
    'cannot verify', 'cannot determine', 'not visible', 'incomplete evidence',
)


def resolve(discovery: Classification, verification: Classification) -> Classification:
    label = discovery.moment_type
    if label is None:
        return discovery.model_copy(update={"decision": "rejected"})
    reason = verification.reason or "verification did not confirm the proposed event"
    normalized = reason.strip().lower()
    expert = label in EXPERT_LABELS or any(
        phrase in normalized for phrase in ('foul', 'referee', 'statistical rule')
    )
    uncertain = normalized.startswith('uncertain:') or any(
        phrase in normalized for phrase in INCOMPLETE_EVIDENCE
    )
    if verification.moment_type == label and not uncertain:
        return Classification(
            moment_type=label,
            subject_present=discovery.subject_present and verification.subject_present,
            confidence=min(discovery.confidence, verification.confidence),
            reason=verification.reason or discovery.reason,
            decision="confirmed",
            phase1_moment_type=label,
            verification_reason=verification.reason,
            expert_review_required=expert,
        )
    hard_reject = normalized.startswith("rejected:") and not uncertain
    return Classification(
        moment_type=None if hard_reject else label,
        subject_present=discovery.subject_present,
        confidence=min(discovery.confidence, verification.confidence, 0.49),
        reason=discovery.reason,
        decision="rejected" if hard_reject else "potential_event",
        phase1_moment_type=label,
        verification_reason=reason,
        expert_review_required=expert,
    )


def build_review_queue(candidates: list[CandidateWindow], classifications: list[Classification]) -> list[PotentialEvent]:
    queue = []
    for index, (window, result) in enumerate(zip(candidates, classifications)):
        if result.decision != "potential_event" or not result.phase1_moment_type:
            continue
        queue.append(PotentialEvent(
            candidate_index=index,
            start=window.start,
            end=window.end,
            proposed_label=result.phase1_moment_type,
            confidence=result.confidence,
            uncertainty_reason=result.verification_reason or result.reason,
            expert_review_required=result.expert_review_required,
            event_time=result.event_time,
            event_id=result.event_id,
            team=result.team,
        ))
    return queue
