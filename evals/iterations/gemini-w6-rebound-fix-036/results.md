# W6 possession-sequence model fix — iterations 035–036

Completed September 15, 2026 on the reviewed W6 development clip. No holdout data was accessed.

## Implemented change

The native Gemini video prompt now requires an ordered possession ledger: shooting team, visible outcome and next controlling team. Rebound type is determined by comparing the rebound controller with the immediately preceding missed-shot team. An offensive rebound keeps the possession open so a putback and later rebound are treated as separate events. Possession changing after a missed shot is not automatically a turnover.

Structured evaluation output now carries `team` and `shooting_team`. A deterministic validator rejects a defensive rebound whose controlling team equals its claimed shooting team, and rejects an offensive rebound when those teams differ. Clip-relative timestamps are normalized to source time. Exact and generic miss labels emitted for the same shot are deduplicated.

## Before and after

| Run | Defensive-rebound prediction | Evidence-aware result | Unsupported turnover |
|---|---|---|---|
| 034 baseline | Campus/yellow defensive rebound at 1321.5 | TP0 / FP1 / FN1 | Yes |
| 035 fixed | Unlimited defensive rebound after Campus miss at 1324.167 | TP1 / FP0 / FN0 | No |
| 036 independent repeat | Unlimited defensive rebound after Campus miss at 1324.33 | TP1 / FP0 / FN0 | No |

The fix reproduced the correct defensive-rebound team, preceding shooting team and reviewed 1323–1325 interval in **two of two fresh calls**. Total incremental estimated spend for 035–036 was **$0.033615**, moving the cumulative local ledger from $9.067744875 to $9.101359875.

Iteration 035 returned clip-relative timestamps despite the requested source-time format. Its model call completed, but the first parser stopped. The response was preserved in the provider log and successfully reparsed after adding explicit, tested time-basis normalization; no duplicate paid call was used for recovery.

## Remaining error

This is a successful targeted defensive-rebound fix, not full sequence recall. Both corrected calls recovered the later Campus miss and Unlimited defensive rebound, but neither recovered the earlier Campus offensive rebound. The precise point time for the second miss remains unresolved in the human review and was not manufactured. Iteration 036 also returned both `two_point_miss` and its generic parent `missed_field_goal` for the same shot; deterministic hierarchy deduplication reduces that to one event.

The result demonstrates a real model-output improvement because the fresh predictions changed and passed team/time/evidence validation. It does not claim generalized rebound accuracy from one reviewed play. Broader validation requires additional independently reviewed rebound sequences with team and shot–rebound order annotations.

## Verification

The full repository suite passes: 420 tests passed and 4 were skipped. Targeted possession, Gemini-provider and W6 evidence tests are included in that run. Historical reports were preserved; no commit or push was performed.
