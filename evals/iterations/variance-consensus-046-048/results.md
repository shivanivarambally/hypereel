# Variance estimate and majority-vote consensus — 046, 047, 048

Completed 15 September 2026. Three unchanged repeats of 045 restricted to the
scored windows W1–W5, at 8 fps, single-pass control reused frozen from 038. No
code, prompt, model, recipe or media changed between runs. The repeats serve two
purposes at once: they estimate run-to-run variance, and they supply the samples
for an offline consensus ensemble that costs nothing extra.

## Why this was run first

045 measured F1 0.727 against a 0.500 baseline but could not attribute the gain,
because discovery output moved between runs despite discovery being unmodified.
With six positive labels, one event is 16.7% of recall, so noise and signal were
plausibly the same size. No further comparison on this set was interpretable
until the spread was known.

## Result 1 — variance quantified

Confirmed stage, six reviewed positive labels in W1–W5:

| Run | TP/FP/FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| 045 | 4/1/2 | 0.80 | 0.67 | 0.727 |
| 046 | 4/1/2 | 0.80 | 0.67 | 0.727 |
| 047 | 4/1/2 | 0.80 | 0.67 | 0.727 |
| 048 | 3/2/3 | 0.60 | 0.50 | 0.545 |

**Mean 0.682, sd 0.091, spread 0.182.** Frozen single-pass control: 0.500.

The variance is real and large relative to the gain. It is also **not large
enough to explain the gain away**: the worst of four runs (0.545) still beats the
single-pass baseline (0.500), and the previous two-phase confirmed score was
0.400. The verifier fix survives the variance check.

## Result 2 — per-window instability

| Window | Distinct outcomes in 4 runs | Detail |
|---|---|---|
| W1 | 2 | 3× `two_point_miss` + `defensive_rebound`; 1× `three_point_miss` + `defensive_rebound` |
| W2 | 2 | 2× with `assist`, 2× without; `steal`/`turnover`/`two_point_made` in all four |
| W3 | 1 | empty in all four (stable correct negative) |
| W4 | 2 | **3× `free_throw_miss` (correct)**, 1× `free_throw_made` |
| W5 | 3 | `two_point_miss` in all four; second event was `defensive_rebound` ×2, `offensive_rebound` ×1, rejected ×1 |
| W6, W7 | 1 | stable (outside scored subset) |

Two patterns. Shot *type* wobbles within the correct outcome family (W1:
two-point versus three-point, both misses). Secondary events appear and
disappear, and rebound *team attribution* flips (W5: offensive versus
defensive). The core event of each window is stable; the periphery is not.

W4 is the important one. It is correct in three runs of four. Every single-run
report before 045 sampled the wrong side of that coin.

## Result 3 — consensus removes the variance

`scripts/score_consensus.py` (new, no inference) keeps a label only when it
appears in at least a threshold fraction of runs.

| Ensemble | TP/FP/FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| Single run, mean of 4 | — | — | — | 0.682 ± 0.091 |
| Consensus, threshold 0.50 (≥2 of 4) | 4/1/2 | 0.80 | 0.67 | **0.727** |
| Consensus, threshold 0.75 (≥3 of 4) | 4/1/2 | 0.80 | 0.67 | **0.727** |

Consensus scores what the *best* single run scores, deterministically, rather
than the mean. Both thresholds agree, which is a useful stability signal in
itself. The 048 outlier's `free_throw_made` on W4 is voted out; W4 resolves to
`free_throw_miss`, which human adjudication confirmed is correct.

Threshold 0.50 additionally admits `assist` on W2 (2 of 4 runs); it is
unadjudicated and therefore ignored by the scorer, so it does not affect the
score. Threshold 0.75 drops it. Prefer 0.75 in production: same score, fewer
unverified extras reaching a reviewer.

Consensus costs 4× inference for one answer. That is the trade: roughly $0.76
per window-set instead of $0.19, in exchange for a reproducible number.

## Result 4 — only two errors remain, and one is on a disputed label

Consensus output versus reference:

| Window | Consensus | Reference | Status |
|---|---|---|---|
| W1 | `two_point_miss`, `defensive_rebound` | `free_throw_made` | FP + FN, **reference disputed** |
| W2 | `steal`, `turnover`, `two_point_made` | `steal`, `two_point_made` | correct |
| W3 | — | — | correct negative |
| W4 | `free_throw_miss` | `free_throw_miss` | correct |
| W5 | `two_point_miss` | `missed_field_goal`, `block` | shot matched by family; `block` missed |

W1 has now been contradicted by **eight independent runs** (038 single-pass,
040, 041, 043, 045, 046, 047, 048), all reporting a missed field goal followed by
a defensive rebound against a `free_throw_made` reference. Sensitivity analysis:

| Assumption | TP/FP/FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| W1 reference correct as written | 4/1/2 | 0.80 | 0.67 | 0.727 |
| **W1 reference is a missed FG + defensive rebound** | **5/0/1** | **1.00** | **0.83** | **0.909** |

One free human decision moves the headline from 0.727 to 0.909 or confirms a
genuine and very stubborn model failure. Either way it is now the highest-value
action available, and it costs nothing.

If W1 resolves in the model's favour, the only remaining error on this set is
`block` in W5, never detected by any arm in any run at any frame rate.

## Budget

| Run | Calls | Incremental |
|---|---:|---:|
| 046 | 9 | $0.1900208 |
| 047 | 9 | $0.1910700 |
| 048 | 9 | $0.1899195 |

- Ledger after: **$10.748652375**
- Ceiling $11.192294875; remaining headroom **$0.443642**
- Session total across 043–048: **$1.0548003**

Stopping here deliberately with headroom intact. Further repeats will not move
consensus, which is already stable across both thresholds, and the binding
constraint is no longer variance or the model.

## Arc of the whole session

| Iteration | Confirmed F1 | What changed |
|---|---:|---|
| 041 (baseline state at session start) | 0.400 | — |
| 042 | 0.400 | Offline re-score, family matcher: no change (negative result) |
| 043 | — | 8 fps ablation: no change to scored labels (hypothesis disconfirmed) |
| 044 | 0.800 on W2+W4 subset | Verifier de-anchored, shot-family criteria re-keyed |
| 045 | 0.727 | Fix applied to full set; attribution unclear |
| 046–048 + consensus | **0.727 deterministic** | Variance quantified; consensus removes it |

Single-pass control held at 0.500 throughout.

## Limitations

Six positive labels across two development games, one of them disputed. Four
runs is a small variance sample; sd 0.091 has wide error bars of its own. Fixed
reviewed windows throughout, so proposer recall remains unmeasured and no
full-game claim is supported. Consensus reduces sampling variance but adds no
evidence, so a label wrong in every run survives the vote. W6 and W7 ran but sit
outside the scored subset. 443 passed, 4 skipped. Holdout untouched; golden
labels unmodified. No commit or push.

## Next, in order

1. **Re-adjudicate W1.** Free, blocking, decides between 0.727 and 0.909.
   Clip at `evals/adjudication/disputed-w1-w4/w1_disputed_5.5-10.0.mp4`; that
   file begins at source 5.5 s, so the disputed events at 7.375 s and 8.25 s sit
   near 1.9 s and 2.75 s into it.
2. **Grow the reference set** past six labels. This is now the constraint on
   every remaining question. Target 40–60 labels, 15–20 windows, with made and
   missed shots deliberately balanced and at least four instances per action
   type.
3. **Measure proposer recall** offline against reference timestamps. Still zero
   on a full game, and likely the dominant term there.
4. Structured-field schema (`{action, shot_type, outcome}`) only after the
   reference set is trusted and larger.
