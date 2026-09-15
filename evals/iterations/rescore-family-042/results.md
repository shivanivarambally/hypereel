# Offline family re-score and fps instrumentation — 042

Completed 15 September 2026. **No inference. No spend.** Ledger unchanged at
$9.693852375; authorized ceiling $11.192294875; remaining headroom $1.498442.

This iteration re-scored existing recorded outputs from 038–041 under a new
label matcher and instrumented the sampled frame rate. No model was called, no
golden label was edited, and the final holdout was not touched.

## What was changed

1. `scripts/score_two_phase_e2e.py` — replaced the `index == 5` special case
   with a general label-family matcher. Two relationships are now credited, in
   either direction: **subsumption** (`missed_field_goal` covers
   `two_point_miss` / `three_point_miss`; `made_field_goal` covers
   `two_point_made` / `three_point_made`) and **alias**
   (`steal` ≡ `turnover`, one event described from opposite sides).
   Assignment is greedy and one-to-one, exact matches first so a specific
   prediction is not consumed by a generic reference another prediction needed.
   Each window now reports `matched`, `inexact`, `false_positives` and
   `false_negatives`, so family credit is auditable rather than implicit.
2. `scripts/score_two_phase_e2e.py` — added `--out` and `--force` so a report
   can be re-scored without deleting the historical `metrics.json`.
3. `src/hypereel/config.py` — added `gemini_video_fps` (default 4, unchanged).
4. `src/hypereel/providers/gemini_video.py` — the sampled frame rate was
   hardcoded as `4` in six places. It now reads `self._fps` from settings and
   is recorded in every call's metadata, so a run's temporal resolution is
   auditable after the fact.

Regression suite after the change: **443 passed, 4 skipped**.

## Result 1 — the family matcher changed nothing (negative result)

Every stage of every iteration scored identically under exact matching and
family matching.

| Iteration | Stage | TP/FP/FN | F1 (exact) | F1 (family) |
|---|---|---:|---:|---:|
| 038 | single_pass | 2/0/4 | 0.500 | 0.500 |
| 038 | discovery | 2/1/4 | 0.444 | 0.444 |
| 039 | confirmed_plus_potential | 2/0/4 | 0.500 | 0.500 |
| 040 | discovery | 3/2/3 | 0.545 | 0.545 |
| 040 | selected | 1/2/5 | 0.222 | 0.222 |
| 041 | discovery | 3/2/3 | 0.545 | 0.545 |
| 041 | confirmed | 2/2/4 | 0.400 | 0.400 |
| 041 | selected | 2/2/4 | 0.400 | 0.400 |

The hypothesis was that taxonomy overlap was suppressing measured accuracy. It
was not. The `index == 5` hack already granted the only subsumption credit that
mattered, and `turnover` in W2 was being dropped as unadjudicated rather than
counted as a false positive. **Predicted gain: some. Actual gain: zero.**

The change is retained because it is general, auditable and removes a
window-specific special case, not because it improved a number.

## Result 2 — 041's multi-label-per-clip fix is worth +0.18 on selection

Scoring 040 `selected` (which had no recorded metric) against 041:

| Iteration | selected TP/FP/FN | F1 |
|---|---:|---:|
| 040 | 1/2/5 | 0.222 |
| 041 | 2/2/4 | 0.400 |

In 040 the selector collapsed every window to one clip and lost discovered
events. In 041 `selected` equals `confirmed`, so selection no longer discards
anything the verifier kept. That regression is closed.

## Result 3 — `confirmed` is the wrong headline metric

The only difference between 041 `discovery` (3/2/3) and 041 `confirmed`
(2/2/4) is W5. W5 was detected at 0.49 confidence, correctly identified as
heavily occluded, and routed to the human review queue as a potential event.
The `confirmed` stage counts only `decision == 'confirmed'`, so **a correctly
flagged uncertain event scores as a miss.**

`confirmed_plus_potential` (3/2/3, F1 0.545) is the honest measure of what the
system produced. `confirmed` measures only what it was willing to auto-accept
without review. Reporting the latter as "automatic accuracy" penalises the
uncertainty router for working. Both limitations are now stated in
`metrics.json`.

## Result 4 — every remaining error is a made-versus-missed error

Per-window discovery errors in 041 under family matching:

| Window | Predicted | Reference | Character of the error |
|---|---|---|---|
| W1 | `two_point_miss` (+ `defensive_rebound`, unadjudicated) | `free_throw_made` | Wrong shot type *and* wrong outcome |
| W2 | `steal`, `turnover`, `two_point_made` | `steal`, `two_point_made` | Both correct |
| W4 | `free_throw_made` @0.95 | `free_throw_miss` | Right shot type, **outcome inverted** |
| W5 | `two_point_miss` @0.49 | `missed_field_goal`, `block` | Shot matched by family; `block` never detected |

W4 is the cleanest signal available. The model identifies the free throw
correctly and reports the opposite outcome at 0.95 confidence, while the frozen
single-pass control got it right. This is not a taxonomy problem, a selection
problem or a prompt-verbosity problem. It is a question of whether the ball went
through the net.

W1 warrants re-adjudication before anything else. Three independent runs
(038 single-pass `defensive_rebound`; 040 and 041 `two_point_miss` +
`defensive_rebound`) all describe a missed field goal followed by a rebound,
against a reference of `free_throw_made`. Three runs disagreeing with one label
in the same direction is more consistent with a label error than with three
correlated model errors. One bad label is 17% of a six-label reference set.

`block` (W5) is the only non-shot miss and is a separate failure: a defensive
event in an occluded frame, never proposed by any arm.

## Hypothesis for the next run

Shot outcome is decided by the ball passing through the net, which lasts roughly
200 milliseconds. Every call in 038–041 sampled at **4 fps**, a 250 ms frame
interval, so the decisive frames can fall between samples. That is consistent
with the observed failure shape: shot *type* is recovered reliably (free throw,
two-point) while shot *outcome* inverts.

The test is a discovery-only re-run of W1, W4 and W5 at a higher frame rate with
everything else held fixed — same clips, same media hashes, same prompt, same
model, same recipe. `gemini_video_fps` now makes this a settings change rather
than a code edit.

Estimated cost, from the 040 per-call average of roughly $0.011 at 4 fps and
token count scaling with sampled frames: **about $0.08–0.12** for three windows
at 10 fps, discovery only. Remaining headroom is $1.498442. This spend is not
yet authorized and has not been made.

If outcome accuracy does not move at a higher frame rate, the next candidate is
the structured-field schema (`{action, shot_type, outcome}`) rather than the
flat 14-way enum, which removes the model's need to commit type and outcome in a
single token.

## Standing limitations

Six positive labels across two development games. Every metric moves ±17% per
event, so none of these differences is statistically meaningful; they are
directional only. Fixed reviewed windows throughout, so proposer recall remains
unmeasured and no full-game claim is supported. Final holdout untouched.
