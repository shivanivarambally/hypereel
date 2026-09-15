# Frame-rate ablation on shot-outcome windows — 043

Completed 15 September 2026. User authorized the experiment proposed in 042.

Discovery + verification re-run of **W1, W4 and W5 only**, at **8 fps** instead of
the historical 4, with everything else held fixed: same clips, same media
hashes, same core intervals, same prompt, same model (`gemini-3.8-flash`), same
recipe. The frozen single-pass control was reused from 038, so no baseline calls
were made. The final holdout was not touched and no golden label was edited.

## Budget

- Ledger before: $9.693852375
- Live video calls: **6**, all completed, zero provider errors
- Incremental estimated spend: **$0.1202475**
- Ledger after: **$9.814099875**
- Ceiling $11.192294875; remaining headroom **$1.378195**

Local accounting only; this does not verify a Google account balance.

## Hypothesis

Shot outcome is decided by the ball passing through the net, roughly 200 ms.
At 4 fps the frame interval is 250 ms, so the decisive frames can fall between
samples. Predicted effect: doubling to 8 fps (125 ms interval) recovers outcome
discrimination, in particular W4's inverted free throw.

## Primary result — disconfirmed

Scored on the four reviewed positive labels inside these three windows
(`free_throw_made`, `free_throw_miss`, `block`, `missed_field_goal`):

| Run | Stage | TP/FP/FN | Precision | Recall | F1 |
|---|---|---:|---:|---:|---:|
| 041 @ 4 fps | discovery | 1/2/3 | 33.3% | 25.0% | 0.286 |
| 043 @ 8 fps | discovery | 1/2/3 | 33.3% | 25.0% | 0.286 |
| 041 @ 4 fps | confirmed_plus_potential | 1/2/3 | 33.3% | 25.0% | 0.286 |
| 043 @ 8 fps | confirmed_plus_potential | 1/2/3 | 33.3% | 25.0% | 0.286 |

Identical at every stage. **Doubling temporal resolution did not change a single
scored label.** The frame-interval explanation for outcome inversion is wrong, or
at least is not the binding constraint at this range.

## Secondary result — fps does raise confidence and event coverage

The scores are identical but the outputs are not. W5 changed materially:

| | 4 fps (041) | 8 fps (043) |
|---|---|---|
| Events discovered | 1 | 2 |
| `two_point_miss` confidence | 0.49 | 0.85 |
| Routing | `potential_event`, sent to human review | `confirmed`, auto-accepted |
| Additional event | none | `offensive_rebound` @6.6s, conf 0.85 |

At 4 fps the model called W5 heavily occluded and declined to commit. At 8 fps it
resolved the same shot confidently and additionally recovered the offensive
rebound that follows it. Event timestamps across all three windows also became
finer, landing on 1/8-second boundaries (7.375, 8.25, 6.0, 6.625).

So higher fps buys **coverage and confidence**, which is worth having for review
throughput and for reducing the human-review queue, but it does not buy outcome
correctness. These are separate problems.

## The error that survived, and why it is now falsifiable

W4 is unchanged and remains the sharpest disagreement in the dataset:

| Source | W4 verdict | Confidence |
|---|---|---|
| Reference label | `free_throw_miss` | — |
| 038 single-pass control | `free_throw_miss` | — |
| 040 two-phase @4 fps | `free_throw_made` | 0.95 |
| 041 two-phase @4 fps | `free_throw_made` | 0.95 |
| **043 two-phase @8 fps** | `free_throw_made` | 0.90 |

At 8 fps the model reports: *"Player #11 in white shoots a free throw at
00:06.8–00:07.5, and the ball goes through the basket at around 00:08.7."*

That is a specific, timestamped, checkable claim, produced independently at two
frame rates. It is either a repeatable model failure or the reference label is
wrong. **Watching 8.7 s of that clip settles it and costs nothing.**

W1 is in the same position with more evidence behind it. Four independent runs
(038 single-pass `defensive_rebound`; 040, 041 and 043 `two_point_miss` +
`defensive_rebound`) describe a missed field goal followed by a rebound, against
a reference of `free_throw_made`. Four runs disagreeing with one label in the
same direction, across two pipeline designs and two frame rates, is not what
correlated model error usually looks like.

`block` in W5 remains undetected at any frame rate by any arm. That is the one
unambiguous recall failure left, and it is a defensive event rather than a shot
outcome.

## What this changes about the plan

Stop spending on model configuration until W1 and W4 are re-adjudicated. Two of
the four reference labels in this subset are contradicted by every run that has
ever been made against them. If both are wrong, discovery on this subset is
3/0/1 rather than 1/2/3, and the pipeline has been penalised for being right.
Six labels, two of them disputed, cannot support any further tuning decision.

The structured-field schema (`{action, shot_type, outcome}`) remains the next
model-side candidate after adjudication, since it removes the need to commit
shot type and outcome in one token. It should not be run before the reference
set is trusted and larger.

## Standing limitations

Three windows, four positive labels. Fixed reviewed windows, so proposer recall
is still unmeasured and no full-game claim is supported. Single-pass control
reused rather than re-run at 8 fps, so this ablation isolates the two-phase arm
only. 443 passed, 4 skipped. Holdout untouched; golden labels unmodified.
