# Human annotation revision and cached-prediction rescore 033

Completed offline on September 15, 2026. No inference call, paid spend, holdout access, or historical-report rewrite occurred.

## What changed

A versioned partial development revision now lives at `evals/golden/revisions/development-human-review-v1.json`. It preserves the original external markers and records the user's observed intervals, FIBA-based adjudication, unresolved values and per-window comparability. Historical `evals/golden/` files are unchanged.

Cached direct-video predictions from `gemini-development-summary/full-control.json` were rescored only where the reviewed label, a usable original point anchor, and the model's original input/core remained comparable.

## Results

| Measurement | Windows | Positive references | TP | FP | FN | Precision | Recall | Micro-F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Historical full original | 8 | 14 | 5 | 8 | 9 | 38.46% | 35.71% | 37.04% |
| Human-adjudicated point-comparable slice | 6, including one confirmed negative | 5 | 2 | 5 | 3 | 28.57% | 40.00% | 33.33% |

These rows are **not a before/after model comparison**. Their denominators differ. The model predictions did not change. The second row measures the currently adjudicable slice and exposes annotation/evaluator coverage gaps.

The five comparable positives are: W1 free-throw made, W2 steal, W4 free-throw miss, W5 block and W6's first two-point miss. W3 is a confirmed negative. W0 remains unreviewed.

Per-window accounting:

- W1: predicted free-throw miss rather than the human-supported make: TP0/FP1/FN1.
- W2: cached steal matches; unconfirmed assist/turnover and incomplete made-basket input are excluded: TP1/FP0/FN0.
- W3: confirmed negative and no cached prediction: TP0/FP0/FN0.
- W4: predicted free-throw made rather than the human-supported miss: TP0/FP1/FN1.
- W5: cached output omitted the block: TP0/FP0/FN1. Its predicted `two_point_miss` is not scored as wrong because the review supports a generic missed FGA but not its point value.
- W6: the first `two_point_miss` matches. Rejected steal and turnover and the unmatched duplicate two-point miss are false positives: TP1/FP3/FN0.

## Explicit coverage gaps

- W2's made basket extends beyond both the original core and cached clip. Cached predictions are not predictions on an action-complete revised input.
- W6's defensive rebound extends beyond the original scored core; it is excluded from the cached-input comparison.
- W5 missed FGA and W7 made FGA have unknown point values. The cached 12-label taxonomy cannot express these gold labels without hierarchy/abstention support.
- W6's second miss and corrected offensive rebound lack exact audited times; they are retained but not point-scored.
- W2 assist and turnover remain unresolved because the user did not separately confirm or reject them.
- The typed 12:58/assumed 21:58 correction remains explicitly pending confirmation.

## Interpretation and next step

The offline rescore does not demonstrate a Gemini improvement or regression. It demonstrates that the original benchmark mixes label errors, incomplete temporal inputs and taxonomy gaps with genuine model errors.

Next, implement a versioned hierarchical evaluation taxonomy in which `two_point_made` and `three_point_made` are children of `made_field_goal`, and corresponding miss labels are children of `missed_field_goal`. Keep exact-subtype and parent-label scores separate. Before any paid inference, obtain exact audited timing for W6's second miss/offensive rebound and create action-complete revised inputs for W2 and W6. A future model run on those inputs must be reported as a new-input experiment, never compared as though only labels changed.
