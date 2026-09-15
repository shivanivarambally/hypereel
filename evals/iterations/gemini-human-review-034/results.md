# Fresh Gemini human-review evaluation 034

Completed September 15, 2026 using `gemini-3.8-flash`. Seven development windows were processed; W0 was excluded because it remains unreviewed. The sealed holdout was not accessed. Incremental estimated spend was **$0.0755235**, moving the local cumulative ledger from $8.992221375 to $9.067744875.

## Comparable result

The only defensible before/after comparison uses unchanged media and the same human-adjudicated scoring policy: W1, W3, W4 and W5. Parent-label credit is allowed where an exact two/three-point subtype is unknown; unadjudicated event families are ignored.

| Run | Windows | Positive refs | TP | FP | FN | Precision | Recall | Micro-F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Cached control | 4 | 4 | 1 | 2 | 3 | 33.33% | 25.00% | 28.57% |
| Fresh Gemini | 4 | 4 | 2 | 1 | 2 | 66.67% | 50.00% | 57.14% |

Micro-F1 increased by 28.57 percentage points on this small common slice. The change comes from W4: the fresh run classified the reviewed free throw as a miss, whereas the cached run called it made. W1 remained wrong. W3 remained a correct negative. W5 retained parent-level credit for the missed field goal but still omitted the block.

This is a **stochastic same-model rerun on four windows**, not evidence of an architecture improvement. The sample is too small to claim generalized improvement.

An exact-subtype-only check, which excludes W5's generic missed-FGA hierarchy credit, moved from TP0/FP2/FN3 (F1 0.00) to TP1/FP1/FN2 (F1 0.40). It has only three positive references and carries the same small-sample warning.

## Revised action-complete inputs

W2 and W6 were deliberately re-extracted with enough surrounding video to include the reviewed actions. They are reported separately because they are different inputs from the cached control.

- W2 recovered both confirmed facts: the steal and made two-pointer. The predicted turnover and assist remain unadjudicated, so they are neither credited nor penalized.
- W6 recovered the first confirmed missed two-pointer. It also invented/repeated a turnover rejected by the user's review and described the rebound with the wrong team/sequence. Its second missed shot and offensive rebound are label-supported, but their exact audited point times remain unresolved.

W6 exposes an evaluator weakness: a naive label-plus-±5-second matcher can call the defensive rebound correct even though the model's evidence assigns it to the wrong team and play sequence. Future scoring must include actor/team and evidence consistency when those fields are known.

## Taxonomy observation

W7 used the new generic `made_field_goal` label instead of guessing a two- or three-pointer. That is the intended taxonomy behavior. It is not point-scored because the human timestamp is approximate, and the model's explanation still claimed two points based on the scoreboard despite an explicit instruction not to do so.

## Conclusion

The fresh run is complete and produced a better outcome on the tiny unchanged-input slice, but it did not resolve the core reliability problem: W1 still reversed a free-throw outcome, W5 missed the block, and W6 showed semantically inconsistent possession/rebound reasoning. Action-complete windows help—especially W2—but prompt-only reruns are not yet a durable solution. The next defensible improvement is an evidence-aware temporal evaluator plus explicit team/actor fields, followed by a repeated-seed development test before any holdout run.
