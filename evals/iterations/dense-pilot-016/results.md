# Dense pilot016 — temporal density at fixed image count

Single declared change from the 013/015 controls: frame spacing 2.4s across a 12s span
(core ±2s) becomes 1.6s across the 8s core. Same model (`openbmb/MiniCPM-V-4_5`), prompts,
temperature 0, seed 0, 1536 output cap, references, 12 definitions and five-second one-to-one
matcher. Both arms share one boundary policy from the outset. Third dataset untouched.

**Declared confound:** at the six-image provider limit found in 013, density and span cannot be
varied independently. The dense arm gains temporal resolution and loses the 2s outer context.
No difference here can be attributed to density alone.

## Operational

24 of 24 calls returned completed output; no provider error, timeout or retry. 78.78s of call
latency, 79.65s elapsed, 39,878 tokens. Estimated spend $0.54936, ledger $4.88544 of the $8
ceiling. Direct arm valid 8/8, narration valid 8/8, extraction valid **4/8** — three
`Missing or invented observation citation`, one `Unknown label or event outside observed interval`.
That last failure is a design consequence: with the dense span equal to the core window there is
no context margin, so an out-of-core event cannot be reclassified as context. Invalid windows
contribute no predictions and are never counted as correct empty results.

## Direct arm, all eight windows, 14 references

The largest like-for-like comparison. Identical model, prompt template and output cap; only the
frame timestamps differ.

| | TP | FP | FN | Precision | Recall | micro F1 | macro F1 | predictions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| sparse 013 | 3 | 31 | 11 | .08824 | .21429 | .12500 | .04709 | 34 |
| dense 016 | 4 | 45 | 10 | .08163 | .28571 | .12698 | .04347 | 49 |

Recall rises .214 → .286 on one extra matched reference. Precision falls, macro F1 falls, and
micro F1 moves by .002. Density bought 15 more predictions and one more true positive.

## Both arms, windows 1 and 6, 6 references

Sparse figures are re-derived from retained 015 raw output under the **same** boundary policy, so
frame timestamps are the only difference.

| | TP | FP | FN | micro F1 | macro F1 |
|---|---:|---:|---:|---:|---:|
| sparse 015 direct | 1 | 5 | 5 | .16667 | .08333 |
| dense 016 direct | 2 | 8 | 4 | .25000 | .16667 |
| sparse 015 transcript | 3 | 1 | 3 | **.60000** | .44444 |
| dense 016 transcript | 3 | 3 | 3 | .50000 | .44444 |

The transcript arm got **worse** under density: same true positives, two more false positives.
Note also that 015's own primary paired figure was .40 on windows [2,6]; the same retained output
scores .60 on windows [1,6]. Window choice moves the headline more than either treatment does,
which is the clearest available statement of how little these samples support.

## Why the recall gain is not recognition

Mutually exclusive labels emitted for one action — made and miss, or offensive and defensive
rebound. Under one-to-one same-label matching the correct member scores a true positive while the
other costs only a false positive, so hedging raises recall without any recognition.

| | contradictory pairs in-window | within 5s | windows affected |
|---|---:|---:|---:|
| dense 016 direct | 26 | 19 | 5 |
| dense 016 transcript | 7 | 5 | 3 |
| sparse 013 direct | 3 | 3 | 2 |
| sparse 015 direct | 0 | 0 | 0 |
| sparse 015 transcript | 2 | 2 | 2 |

Window 0 — an annotation-empty window — produced all four exclusive pairs at the single timestamp
20.0: made and miss for two-point, three-point and free throw, plus both rebound types. That is
enumeration of the label set, not observation.

Window 1 is the mechanism in miniature. The dense transcript emitted `free_throw_made@223.0`
and `free_throw_miss` at both 229.4 and 231.0. The reference is `free_throw_made@225`, so the
made guess scores the true positive and the two miss guesses cost two false positives.

## Evidence quality

Of 20 screened transcript events, **0 pass** the entailment screen (015: 2 of 8). 48 observations,
11 marked `visibility=clear` while the text itself hedges. Better narration did not produce better
grounded extraction; it produced more honest uncertainty that the extractor then overrode.

## What density did fix

Window 1's narration. 015 described "a player in black holds the ball near the three-point line",
which the 015 contact-sheet audit found was actually a free-throw setup. 016 narrates
"Players in blue and black jerseys are positioned for a free throw" and identifies the blue
shooter. That is a real perception improvement on the exact error 015 recorded. It did not carry
through to grounded event extraction: the transcript still could not establish the outcome, said
so ("The outcome of the shot is uncertain", "the ball's final position is unknown"), and the
extractor asserted one anyway.

## Limits

Two development games, 14 references, single-digit per-type support, two annotation-empty windows
that are not verified negatives and can only add false positives. Provisional external clip
timestamps, not audited action bounds. No gate passed. Nothing here supports full-game or holdout
use.
