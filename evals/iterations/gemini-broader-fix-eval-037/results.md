# Broader current-model development evaluation 037

Completed September 15, 2026 with `gemini-3.8-flash`. The current possession-sequence prompt was run freshly on reviewed W1–W5 and W7; the independently repeated fixed W6 result from iteration 036 completes the current-model view. W0 was excluded because it has no adjudicated event inside its window. No holdout data was accessed.

## Overall comparable result

The comparison uses the same eight human-adjudicated facts and the same evidence-aware policy for baseline 034 and the current model. W3 is a confirmed negative. W7 is qualitative because its reviewed timestamp is approximate. Unresolved W2 assist/turnover and W6 offensive-rebound/second-miss point times are not silently converted into negatives.

| Run | TP | FP | FN | Precision | Recall | Micro-F1 |
|---|---:|---:|---:|---:|---:|---:|
| Baseline 034 | 5 | 3 | 3 | 62.50% | 62.50% | 62.50% |
| Current 037 + fixed W6 036 | 4 | 2 | 4 | 66.67% | 50.00% | 57.14% |

The current prompt improved precision by 4.17 percentage points but reduced recall by 12.50 points; micro-F1 declined 5.36 points. The W6 rebound improvement is real, but the broader system did **not** improve overall on this small reviewed set.

## Current per-class result

| Event | Refs | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Steal | 1 | 1 | 0 | 0 | 100% | 100% | 100% |
| Two-point made | 1 | 1 | 0 | 0 | 100% | 100% | 100% |
| Generic missed field goal | 1 | 1 | 0 | 0 | 100% | 100% | 100% |
| Defensive rebound | 1 | 1 | 0 | 0 | 100% | 100% | 100% |
| Free-throw made | 1 | 0 | 1 | 1 | 0% | 0% | 0% |
| Free-throw miss | 1 | 0 | 1 | 1 | 0% | 0% | 0% |
| Block | 1 | 0 | 0 | 1 | — | 0% | 0% |
| First W6 two-point miss | 1 | 0 | 0 | 1 | — | 0% | 0% |

Each class has only one reviewed reference, so the 0% and 100% values are observations, not stable class estimates.

## Window-level findings

- **W1:** still reversed the reviewed made free throw as a miss. Its subsequent defensive rebound is not scored because the review did not adjudicate that event.
- **W2:** correctly recovered the reviewed steal and made two-pointer from the action-complete clip. It also emitted a turnover; that label remains unresolved rather than assumed correct or false. It omitted the unresolved assist.
- **W3:** remained a correct empty result on the human-confirmed negative.
- **W4:** regressed from the correct 034 miss classification to `free_throw_made` in 037.
- **W5:** received hierarchy credit for the supported missed field goal, but still failed to detect the reviewed block. Its offensive rebound was not adjudicated by the review and is ignored.
- **W6:** retained the targeted improvement: correct Campus missed-shot team followed by Unlimited defensive rebound, with no turnover. It missed the earlier confirmed first miss and the approximate Campus offensive rebound. Its detected later miss cannot be reassigned to the earlier reference merely because it is nearby.
- **W7:** detected a made field goal, but over-specified it as a two-pointer and attributed the shooter/team even though the human review says the shooter was off-camera. The predicted time is six seconds from the approximate review time, so it is qualitative only.

## Lighting check

As a descriptive screen, decoded mean luma ranged from 114.46 to 129.43 across the seven clips. The darkest clip, W2, produced the strongest fully reviewed result; W4 had ordinary mean luma (124.45) yet changed from correct to incorrect. This tiny sample does not support lighting as the cause of the observed errors. Camera angle, occlusion, event boundary coverage and stochastic outcome interpretation remain plausible alternatives, but none is established by this run.

## Cost, limits and conclusion

Iteration 037 added an estimated **$0.06522225**, moving the cumulative local ledger to **$9.166582125**. The funded evaluation ceiling remains $9.192294875, leaving about $0.0257 of evaluator headroom. No additional paid iteration should be started casually.

The current model is relatively reliable on the reviewed steal, made layup, generic miss and corrected defensive rebound examples, and it rejects the negative window. It is not yet reliable on free-throw outcome, block detection or complete multi-event recall. The most defensible next step is to add more independently reviewed examples for those weak classes—especially free throws and blocks—before another prompt change. Repeatedly tuning these same eight facts risks development-set overfitting.
