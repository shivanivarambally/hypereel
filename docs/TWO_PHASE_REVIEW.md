# Two-phase event detection and human review

HypeReel supports an opt-in two-pass Gemini video workflow:

**Update — 16 September 2026:** the recipe may set `verify_events: true` (verification), `false` (multi-event discovery only), or omit it (global setting). Discovery-only skips the second call, not event enumeration. Its `confirmed` status is a selection-compatibility flag, **not independent confirmation**; the human clip gate still applies. The sequence rules gate can route suspect outputs to review in either temporal mode. [Rules and caveats](BASKETBALL_RULES.md).

The broader run 055 used discovery-only at an experimental 8 fps and reached F1 .360 on 98 externally labeled references. Two-phase superiority remains untested on this broader segment. Older curated claims that verification adds no value do not justify a general recommendation to disable it. Native-video settings still default to 4 fps; experiment runners set `Settings.gemini_video_fps` explicitly. No paid inference was rerun for the publication review.

Current native-video contract (15 September 2026, iteration 040): discovery returns multiple event records with timestamps and optional model-attributed teams. Verification checks the entire list in a second call. The old one-label contract remains available for legacy callers and providers. Timestamps are predictions, not independently verified truth. Historical single-label results remain in [evaluation 039](../evals/iterations/two-phase-e2e-039/results.md).

1. **Discovery:** enumerate plausible rubric events per candidate window, preserving multiple actions in one possession, using clip-relative timestamps converted to source-video seconds.
2. **Verification:** check every event ID against the same continuous footage, allowing a supported label correction for the same action. Missing, malformed or uncertain verification retains proposals for review. Empty discovery makes no verification call.

Verification produces one of three outcomes:

- `confirmed`: the proposed action is supported, possibly with a corrected label, and may proceed to reel selection. Original label/time and verification evidence remain attached.
- `potential_event`: evidence is plausible but incomplete, occluded or disputed. It is excluded from automatic selection and added to the review queue.
- `rejected`: the video visibly contradicts the proposal. It is excluded and not added to the queue.

At the clip-approval screen, each potential event shows its source interval, proposed label, uncertainty reason and an expert-review indicator when applicable. The reviewer can **Confirm**, **Correct label**, **Reject**, or **Review later**. Confirmed/corrected items enter the proposed reel only through this explicit human action.

Blocks, assists and ambiguous turnovers in the potential queue are marked as basketball-expert review candidates. Ordinary visible decisions do not require an expert.

Unclear foul/referee/statistical rules also trigger expert escalation. An outcome hidden off-camera or by occlusion remains a potential event even if a model inconsistently calls it rejected. After a person approves potential clips, the displayed reel duration is recalculated from the edited selection.

Enable the workflow with:

```bash
HYPEREEL_TWO_PHASE_VERIFICATION=true
```

This setting is off by default because verification can approximately double model calls. The existing funded budget guard remains authoritative.

The review queue is stored in graph state as structured `PotentialEvent` records. It preserves the candidate interval, proposed label, confidence, uncertainty reason, review status and expert-review flag. It does not silently change golden annotations or treat unresolved review as rejection.

Event records also retain event ID/time and the model-attributed team. Graph state preserves original proposal windows separately from expanded event-aligned candidates. Review/render clips retain contextual windows; overlapping selected footage may be deduplicated, but detection records are not discarded. Cross-window event deduplication and validated team normalization remain future work. The list is bounded at 12 events per short window; oversized/invalid discovery is recorded as an error, never silently truncated.

## Evaluation requirements

Measure discovery and final output separately:

- Phase 1: candidate recall.
- Phase 2: confirmation precision, rejection accuracy and potential-event rate.
- Final output: precision, recall and F1 after verification.
- Human workflow: queue size, correction rate, expert-escalation rate and review time.
- Temporal quality: strict timestamp error plus the established tolerance-aware result.

Potential events are neither automatic true positives nor automatic false positives. They receive a final metric outcome only after human adjudication. A time tolerance can absorb minor timestamp drift but must not excuse the wrong event, wrong team, wrong possession order or an omitted event.
