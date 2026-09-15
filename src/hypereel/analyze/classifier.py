"""Turn candidate windows into vision-model verdicts.

Bridges the cheap, local proposer signals (audio/motion) to the vision model:
samples a handful of frames per candidate window, then asks the active
:class:`VisionProvider` to judge each window against the recipe's rubric.
Degrades gracefully at every step — no video, no OpenCV, or a provider
hiccup should shrink confidence, never take down the pipeline.
"""

from __future__ import annotations

import os

from ..config import Settings
from ..observability import checkpoint_classification
from ..models import CandidateWindow, Classification, Recipe
from ..providers.base import VisionProvider
from .two_phase import resolve


def extract_frames(video_path: str | None, window: CandidateWindow, n: int, out_dir: str) -> list[str]:
    """Sample ``n`` frames evenly across ``window`` and write them as JPEGs to ``out_dir``.

    Returns the written paths, in order. Returns ``[]`` (never raises) if there
    is no source video, OpenCV isn't installed, or the read fails for any
    reason. Most vision providers — including the mock used in tests — judge
    a window without needing real frame content, so an empty list is a safe,
    fully-functional degradation.
    """
    if not video_path or n <= 0:
        return []

    try:
        import cv2  # lazy import: opencv is an optional dependency
    except ImportError:
        return []

    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return []

        fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
        if fps <= 0:
            cap.release()
            return []

        os.makedirs(out_dir, exist_ok=True)
        duration = max(window.end - window.start, 0.0)
        paths: list[str] = []
        for i in range(n):
            # Evenly spaced timestamps in [start, end]; a lone frame lands at the midpoint.
            frac = 0.5 if n == 1 else i / (n - 1)
            timestamp = window.start + frac * duration
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(timestamp * fps))
            ok, frame = cap.read()
            if not ok:
                continue
            out_path = os.path.join(out_dir, f"w{int(window.start * 1000)}_{i}.jpg")
            if cv2.imwrite(out_path, frame):
                paths.append(out_path)
        cap.release()
        return paths
    except Exception:
        return []


def verification_enabled(recipe, settings) -> bool:
    """Whether the second verification pass runs for this recipe.

    ``recipe.verify_events`` wins when set; otherwise the global setting decides.
    Kept as one function so both the legacy per-window path and the temporal
    path agree, and so the decision is greppable rather than duplicated.
    """
    override = getattr(recipe, 'verify_events', None)
    return bool(settings.two_phase_verification if override is None else override)


def classify_candidates(
    candidates: list[CandidateWindow],
    recipe: Recipe,
    provider: VisionProvider,
    settings: Settings,
    video_path: str | None = None,
) -> list[Classification]:
    """Classify every candidate window, 1:1, never raising.

    ``VisionProvider.classify_window`` is contractually non-raising, but frame
    extraction (or a misbehaving custom provider) could still blow up — one
    bad window should never drop the rest of the reel, so any exception here
    becomes a low-confidence, explained :class:`Classification` instead.
    """
    frames_dir = os.path.join(settings.download_dir, "frames")
    results: list[Classification] = []
    for i, window in enumerate(candidates):
        try:
            video_classifier = getattr(provider, "classify_video_window", None)
            if callable(video_classifier) and video_path:
                classification = video_classifier(video_path, window, recipe, window_index=i)
                if verification_enabled(recipe, settings) and classification.moment_type is not None:
                    verifier = getattr(provider, "verify_video_window", None)
                    if callable(verifier):
                        verification = verifier(
                            video_path, window, recipe, classification, window_index=i
                        )
                        classification = resolve(classification, verification)
                checkpoint_classification(i, window, classification)
                results.append(classification)
                continue
            context = max(0.0, settings.classification_context_seconds)
            if context > 0 and settings.frames_per_candidate >= 5:
                frame_paths = []
                if window.start > 0:
                    before = CandidateWindow(
                        start=max(0.0, window.start - context), end=window.start,
                        signal_scores=window.signal_scores,
                    )
                    frame_paths += extract_frames(video_path, before, 1, frames_dir)
                core_paths = extract_frames(
                    video_path, window, settings.frames_per_candidate - 2, frames_dir
                )
                frame_paths += core_paths
                after = CandidateWindow(
                    start=window.end, end=window.end + context,
                    signal_scores=window.signal_scores,
                )
                frame_paths += extract_frames(video_path, after, 1, frames_dir)
            else:
                frame_paths = extract_frames(
                    video_path, window, settings.frames_per_candidate, frames_dir
                )
                core_paths = frame_paths
            classification = provider.classify_window(frame_paths, recipe, window_index=i)
            if settings.verify_with_core_frames:
                verify = getattr(provider, "verify_window", None)
                verification = (
                    verify(core_paths, recipe, classification, window_index=i)
                    if callable(verify) and classification.moment_type is not None
                    else provider.classify_window(core_paths, recipe, window_index=i)
                )
                if verification.moment_type != classification.moment_type:
                    classification = Classification(
                        moment_type=None,
                        subject_present=(classification.subject_present
                                         and verification.subject_present),
                        confidence=min(classification.confidence, verification.confidence, 0.25),
                        reason=("context/core disagreement: context="
                                f"{classification.moment_type}, core={verification.moment_type}"),
                    )
                else:
                    classification = Classification(
                        moment_type=classification.moment_type,
                        subject_present=(classification.subject_present
                                         and verification.subject_present),
                        confidence=min(classification.confidence, verification.confidence),
                        reason=classification.reason,
                    )
        except Exception:
            classification = Classification(confidence=0.0, reason="classification error")
        checkpoint_classification(i, window, classification)
        results.append(classification)
    return results


from .phase_transitions import apply_rules_gate, build_transitions  # noqa: E402

#: Phase-1 -> phase-2 transitions from the most recent classify_moments call.
#: Module-level so a runner can read verification behaviour without threading
#: another return value through the graph. Cleared at the start of each call.
last_run_transitions: list = []


def classify_moments(candidates, recipe, provider, settings, video_path=None):
    """Expand temporal outputs while keeping the legacy classifier's 1:1 contract.

    Event records remain separate even when selection deduplicates overlapping
    footage. Each event retains its full proposal window for contextual review.
    """
    last_run_transitions.clear()
    temporal = getattr(provider, 'classify_video_events', None)
    # The temporal path stays active whenever it is available: multi-event discovery
    # is independent of verification, and `verify_events=False` skips only the second
    # call inside the provider. Falling back to the single-label path here would
    # discard the capability that the gain actually comes from.
    temporal_available = video_path and callable(temporal)
    if not (temporal_available and (verification_enabled(recipe, settings)
                                    or getattr(recipe, 'verify_events', None) is False)):
        return candidates, classify_candidates(candidates, recipe, provider, settings, video_path)
    windows, results = [], []
    for index, window in enumerate(candidates):
        try:
            events = temporal(video_path, window, recipe, window_index=index)
        except Exception as error:
            events = [Classification(confidence=0, source_window_index=index,
                       reason=f'temporal discovery error: {type(error).__name__}')]
        # Rules gate, applied per window because legality is a property of a
        # sequence: a rebound is judged against the shot that preceded it in the
        # same possession, not against events in an unrelated window. Illegal
        # combinations are routed to human review rather than deleted, since
        # code cannot tell which of the two labels is the wrong one.
        events, violations = apply_rules_gate(events)
        last_run_transitions.extend(build_transitions(events, violations))
        for event in events:
            windows.append(window)
            results.append(event)
            checkpoint_classification(len(results)-1, window, event)
    return windows, results
