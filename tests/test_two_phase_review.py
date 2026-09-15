from unittest.mock import Mock

from hypereel.analyze.classifier import classify_candidates
from hypereel.analyze.two_phase import build_review_queue, resolve
from hypereel.config import Settings
from hypereel.models import CandidateWindow, Classification, PotentialEvent
from hypereel.review import apply_review_action
from hypereel.select.selector import score_candidates


def test_disagreement_becomes_potential_event_and_not_auto_selected(basketball_recipe):
    discovery = Classification(moment_type="block", subject_present=True, confidence=.8, reason="possible touch")
    verification = Classification(moment_type=None, subject_present=True, confidence=.5, reason="UNCERTAIN: occluded contact")
    result = resolve(discovery, verification)
    window = CandidateWindow(start=10, end=14, signal_scores={"motion": 1})
    queue = build_review_queue([window], [result])
    assert result.decision == "potential_event"
    assert result.expert_review_required is True
    assert queue[0].proposed_label == "block"
    assert score_candidates([window], [result], basketball_recipe) == []


def test_visible_contradiction_is_rejected_not_queued():
    discovery = Classification(moment_type="steal", confidence=.7)
    verification = Classification(moment_type=None, confidence=.9, reason="REJECTED: ordinary rebound")
    result = resolve(discovery, verification)
    assert result.decision == "rejected"
    assert build_review_queue([CandidateWindow(start=0, end=2)], [result]) == []


def test_matching_verification_is_confirmed():
    discovery = Classification(moment_type="steal", subject_present=True, confidence=.8)
    verification = Classification(moment_type="steal", subject_present=True, confidence=.7, reason="interception visible")
    result = resolve(discovery, verification)
    assert result.decision == "confirmed"
    assert result.moment_type == "steal" and result.confidence == .7


def test_classifier_calls_both_video_phases_when_enabled(basketball_recipe):
    provider = Mock()
    provider.classify_video_window.return_value = Classification(moment_type="steal", confidence=.8)
    provider.verify_video_window.return_value = Classification(moment_type="steal", confidence=.7)
    settings = Settings(two_phase_verification=True)
    result = classify_candidates([CandidateWindow(start=1, end=3)], basketball_recipe, provider, settings, "/video.mp4")
    assert result[0].decision == "confirmed"
    provider.verify_video_window.assert_called_once()


def test_simple_review_actions():
    item = PotentialEvent(candidate_index=0, start=1, end=3, proposed_label="block",
                          confidence=.4, uncertainty_reason="occluded", expert_review_required=True)
    assert apply_review_action(item, "confirm").review_status == "confirmed"
    corrected = apply_review_action(item, "correct", corrected_label="missed_field_goal")
    assert corrected.review_status == "corrected" and corrected.proposed_label == "missed_field_goal"
    assert apply_review_action(item, "reject").review_status == "rejected"


def test_off_camera_outcome_is_queued_even_if_verifier_says_rejected():
    discovery = Classification(moment_type='free_throw_made', confidence=.8)
    verification = Classification(moment_type=None, confidence=.8,
        reason='REJECTED: The basket is off-camera, making the outcome unviewable directly.')
    result = resolve(discovery, verification)
    assert result.decision == 'potential_event'
    queue = build_review_queue([CandidateWindow(start=92, end=104)], [result])
    assert len(queue) == 1
    assert queue[0].proposed_label == 'free_throw_made'


def test_matching_label_with_uncertain_evidence_is_not_auto_confirmed():
    discovery = Classification(moment_type='block', confidence=.8)
    verification = Classification(moment_type='block', confidence=.8,
        reason='UNCERTAIN: defender contact is occluded')
    result = resolve(discovery, verification)
    assert result.decision == 'potential_event'


def test_unclear_foul_on_shot_escalates_to_expert():
    discovery = Classification(moment_type='two_point_miss', confidence=.8)
    verification = Classification(reason='UNCERTAIN: a foul may have negated the attempt')
    result = resolve(discovery, verification)
    assert result.decision == 'potential_event'
    assert result.expert_review_required
