# Two-phase production evaluation and UI/render verification — 038–039

Completed 15 September 2026. The user authorized increasing the evaluation ceiling by $2 and repeating end-to-end tests.

## Outcome

The actual Gemini discovery, verification, review queue, local approval, rendering and download paths were exercised. Workflow checks passed. Recognition did not improve sufficiently: automatic output matched only one of six scorable reviewed labels, and another label was retained as a potential event for human review.

The production adapter still returns **one label per candidate window**. Consequently it cannot enumerate both the steal and basket in W2, or both the block and missed shot in W5. The earlier statement that the complete multi-event discovery design had been implemented was too broad. The current feature implements two passes for one proposal per window.

## Budget and execution

- Previous cumulative ceiling: $9.192294875.
- Authorized increase: $2. New ceiling: **$11.192294875**.
- Historical spending before this task: $9.166582125; it was not reset.
- Live video calls: **33**, all completed (20 in 038, 13 in 039).
- Live graph judge/summary calls during UI checks: **11**, all completed.
- Video-call estimated cost: $0.372648; UI text-call estimated cost: $0.0063945.
- Total additional estimated cost: **$0.3790425**.
- Final cumulative ledger: **$9.545624625**.
- Remaining authorized headroom: **$1.64667025**.

This changes the local spending cap; it does not purchase credits or verify the Google account balance. Per-run ledger deltas include UI calls made while the video comparison was running, so sum provider records for isolated video-call costs.

## What was run

038 ran a fresh single-pass control and fresh two-phase classification through the production `GeminiVideoVisionProvider`, `classify_candidates`, review-queue construction and graph selection for W1–W7. The model was `gemini-3.8-flash`, using continuous video at four sampled frames per second. The same reviewed clip files, core intervals and all-event recipe were used across arms. Prompts contained team identity but no golden event labels or expected answers.

039 repeated all seven two-phase windows after uncertainty-routing corrections, reusing the immutable single-pass control from 038. The runner checked media hashes and core intervals for that reuse. No model was trained or fine-tuned. W0 has no in-window human adjudication and was excluded. The final third-game holdout was not used; its test was explicitly deselected.

## Metrics and their limits

Production classifications have no event timestamp and no structured team fields. Accordingly these results measure **label coverage within fixed reviewed windows**, not timestamped event accuracy, team accuracy, or candidate-proposer recall. The previous ±5-second matching rule cannot be applied to a response without an event timestamp. Earlier 034–037 event-level F1 values are not directly comparable with this table.

The primary subset is W1–W5: six reviewed positive labels plus confirmed-negative W3. Unadjudicated extra event families are ignored consistently for both arms. W6 has ambiguous timing and multiple nearby shots, and W7 has an unaudited timestamp and unknown shot value; both are reported qualitatively.

| Stage | TP | FP | FN | Conditional precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| Fresh single-pass control, 038 | 2 | 0 | 4 | 100% | 33.3% | 50.0% |
| Discovery, final two-phase run 039 | 2 | 1 | 4 | 66.7% | 33.3% | 44.4% |
| Automatically confirmed and selected, 039 | 1 | 0 | 5 | 100% | 16.7% | 28.6% |
| Confirmed plus pending potential events, 039 | 2 | 0 | 4 | 100% | 33.3% | 50.0% |

The 100% precision for automatic output is only **one correct scored prediction out of one scored prediction**. Other unadjudicated outputs are excluded; this does not demonstrate reliable overall accuracy. The last row measures retained candidate coverage. It is not final human-reviewed accuracy and does not automatically credit a future correction.

In initial 038, only one primary reference survived confirmation or review retention. In 039, the reviewed W5 missed-shot label survived as a potential event. Its eventual basketball-statistics adjudication is still a human decision.

Current per-class counts, full phase metrics and every window's accounting are reproducible in `metrics.json` using `scripts/score_two_phase_e2e.py`. The scorer consumes actual recorded model classifications rather than prefilled TP/FP/FN lists.

## Concrete findings

| Window | Final two-phase result | Compared with human review |
|---|---|---|
| W1 | Confirmed defensive rebound | Omitted the reviewed made free throw. The generated missed-shot narrative conflicts with that review; the extra rebound has not been separately adjudicated. |
| W2 | Confirmed made two-pointer | Correct basket; separate reviewed steal omitted from the one-label output. |
| W3 | Empty | Correct negative. |
| W4 | Proposed two-point miss; verifier rejected it as a free-throw attempt | Wrong discovery category. Verifier recognized the category problem, but the current confirm/reject contract cannot output the corrected event. |
| W5 | Potential two-point miss; unclear foul/statistical interpretation | Generic missed-FGA coverage retained for review; point value remains unconfirmed. Reviewed block omitted. Expert review requested by final deterministic routing. |
| W6 | Proposed two-point miss; verifier rejected it as a three-point miss | Narrative remains inconsistent with the reviewed Campus miss/rebound sequence. No claim that the earlier specialized W6 success transferred to this production path. |
| W7 | Confirmed two-point make | Review supports a made basket with unknown point value and off-camera shooter; subtype remains unsupported. |

## Bugs found and corrected during testing

1. **Hidden evidence was treated as rejection.** In 038 the verifier began its reason with `REJECTED:` while saying the basket was off-camera. The router now retains explicit uncertainty and occluded/off-camera outcomes as potential events, even when the prefix or matching label is inconsistent. Added regressions for both failure cases; the verifier prompt now distinguishes unseen outcomes from observed contradictions.
2. **Expert escalation missed unclear foul calls on shot candidates.** It previously only checked whether the candidate label was block, assist or turnover. Foul/referee/statistical-rule ambiguity in the verification reason now also marks a potential event for expert review. `review-routing.json` applies this deterministic correction to the captured 039 outputs with zero new inference; W5's flag changes to true. No labels or golden data changed.
3. **Human-confirmed potential clips left a stale duration total.** Gate 1 now recalculates duration from the approved selection. The corrected queue-to-render test verified an 8-second selected clip, 8-second rendered MP4 and matching displayed state.

## End-to-end UI evidence

- Fresh 038 W2 confirmation → actual graph selection/judge → Gate 1 → simulated local render approval → 15-second MP4 → Gate 2 with video player and download button.
- Fresh 038 W6 potential event → disabled render button while pending → simulated confirmation → 9-second MP4. A follow-up test verified duration after the metadata fix.
- Fresh 039 W5 potential event → expert indicator → simulated correction to `missed_field_goal` → preserved `corrected` review status → 8-second MP4 and download button. Evidence: `ui-potential-e2e.json`.

These are automated UI interactions, not completed human annotations. They never update the golden dataset and are not added to accuracy metrics. No share/publish approval was clicked.

The comparison starts from fixed reviewed candidate windows. UI tests resume the graph after the captured live classification. Full-video ingestion, full-game proposer coverage and final holdout performance are outside this bounded test.

## Verification and next engineering step

Final regression run: **431 passed, 4 skipped, 1 holdout test deselected**. JUnit evidence is in `regression-tests-final.xml`. Existing legacy-SDK warning persists. Historical reports and unrelated local work remain preserved; no commit or push was performed.

The next improvement should be to let discovery return multiple timestamped events per window, then verify each one and allow a supported relabel or human correction. More restrictive prompts alone will not remove the one-label coverage ceiling. Stage metrics, uncertain-item counts and independent development examples should be used to test that change before any final holdout run.
