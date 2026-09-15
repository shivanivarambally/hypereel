# W6 defensive-rebound evidence audit

This is a bounded offline audit of the existing Gemini 034 prediction. It made no new provider call and did not access the holdout.

## Observed versus predicted

| Order | Human-reviewed sequence | Gemini's evidence narrative |
|---:|---|---|
| 1 | Campus/yellow misses a two-pointer around 22:00 | Unlimited/white misses a layup at 21:59.75 |
| 2 | Campus/yellow gets the offensive rebound around 22:02 | Campus/yellow gets a **defensive** rebound at 22:01.5 |
| 3 | Campus/yellow misses a second shot; exact time unresolved | Campus/yellow misses at 22:02.5 |
| 4 | Unlimited gets the defensive rebound at 22:03–22:05 | Campus/yellow gets an offensive rebound at 22:03 |

Gemini also emitted a turnover at 21:57.5, which the human review rejects for this sequence.

## Verdict

The predicted `defensive_rebound` is **not supported** by the reviewed video sequence. Although its 22:01.5 timestamp falls within the broad ±5-second matching tolerance, Gemini explicitly assigns it to yellow/Campus. The reviewed defensive rebound belongs to Unlimited after Campus retains possession, shoots again, and misses.

For the defensive-rebound fact alone:

| Scoring policy | TP | FP | FN |
|---|---:|---:|---:|
| Label + ±5-second time only | 1 | 0 | 0 |
| Label + time + reviewed team/sequence evidence | 0 | 1 | 1 |

The first row is a false sense of correctness. The evidence-aware result is the defensible one.

## Evaluator correction

`scripts/audit_w6_rebound_sequence.py` now performs this focused team-and-sequence check using only team/color aliases explicitly present in the human-review record. It preserves the unresolved exact timing of the second miss and offensive rebound instead of manufacturing point labels. This audit is deliberately case-specific; generalizing it requires structured `team`, `possession_id`, and event-order fields in model output and golden references.
