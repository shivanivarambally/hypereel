# Per-recipe verification flag, discovery-only validation, full statistics — 053

Completed 15 September 2026. Implements the cheaper fix recommended in 052,
validates it live, and reports the full statistical picture from every run on the
current reference set.

## What was implemented

`Recipe.verify_events: bool | None` — a per-recipe override for the second
verification pass. `None` defers to the global setting, so existing behaviour is
unchanged.

Two things had to be separated to make this correct. Turning off
`two_phase_verification` previously also disabled **multi-event discovery**,
because `classify_moments` fell back to the single-label path. That would have
thrown away the capability the gain actually comes from (051: the entire
two-phase advantage is multi-event discovery, a phase-1 property). The temporal
path now stays active whenever available, and `verify_events=False` skips only
the second provider call.

- `verification_enabled(recipe, settings)` in `classifier.py` — one greppable
  place where the decision is made, shared by the legacy and temporal paths.
- Discovery-only branch in `GeminiVideoVisionProvider.classify_video_events` —
  proposals return marked `confirmed` with an empty review queue.
- `scripts/run_two_phase_e2e.py --discovery-only`.

Suite: **459 passed, 4 skipped.**

## Cost saving confirmed live

| Mode | Calls | Spend |
|---|---:|---:|
| Two-phase, W1–W5 (050) | 9 | $0.1908487 |
| **Discovery-only, W1–W5 (053)** | **5** | **$0.1048875** |

**45% cheaper per run**, as predicted. Discovery-only scored 3/2/3, F1 0.545 —
inside the established band, and identical to 050's two-phase result on the same
windows.

## Full statistics, discovery stage, n=6

| Run | TP/FP/FN | Precision | Recall | F1 | Mode |
|---|---|---:|---:|---:|---|
| 045 | 4/1/2 | 0.80 | 0.67 | 0.727 | two-phase |
| 046 | 4/1/2 | 0.80 | 0.67 | 0.727 | two-phase |
| 047 | 4/1/2 | 0.80 | 0.67 | 0.727 | two-phase |
| 048 | 3/2/3 | 0.60 | 0.50 | 0.545 | two-phase |
| 050 | 3/2/3 | 0.60 | 0.50 | 0.545 | two-phase |
| 053 | 3/2/3 | 0.60 | 0.50 | 0.545 | **discovery-only** |

| Metric | Mean | sd | 95% CI | Width |
|---|---:|---:|---|---:|
| **F1** | 0.636 | 0.100 | [0.532, 0.741] | 0.209 |
| **Precision** | 0.700 | 0.110 | [0.585, 0.815] | 0.230 |
| **Recall** | 0.583 | 0.091 | [0.488, 0.679] | 0.192 |

Single-pass control: F1 0.500. Consensus over 045–048: 0.727, deterministic.

The distribution is bimodal, not continuous — every run scores either 4/1/2 or
3/2/3. There is no middle. The difference is entirely whether W4 returns
`free_throw_miss` (correct) or `free_throw_made` (wrong) on that sampling.

## Per-class, n=6

| Class | TP/FP/FN | Precision | Recall | F1 | Detection |
|---|---|---:|---:|---:|---|
| `steal` | 6/0/0 | 1.00 | 1.00 | 1.000 | 6/6 runs |
| `two_point_made` | 6/0/0 | 1.00 | 1.00 | 1.000 | 6/6 runs |
| `missed_field_goal` | 6/0/0 | 1.00 | 1.00 | 1.000 | 6/6 runs |
| `free_throw_miss` | 3/0/3 | 1.00 | 0.50 | 0.667 | **3/6 runs** |
| `free_throw_made` | 0/3/6 | 0.00 | 0.00 | 0.000 | **0/6 runs** |
| `block` | 0/0/6 | — | 0.00 | 0.000 | **0/6 runs** |
| `two_point_miss` | 0/3/0 | 0.00 | — | — | FPs only (W1) |
| `three_point_miss` | 0/3/0 | 0.00 | — | — | FPs only (W1) |

Three classes are solved perfectly and stably. One is a coin flip. Two are never
detected. Every false positive belongs to W1.

## The honest answer on confidence

The request was to run enough tests to be confident about F1 and recall. **That
is not achievable on this reference set, and more runs will not fix it.**

At the observed sd of 0.100, the sample size needed for a given 95% CI width:

| Target CI width | Runs needed | Approx cost at $0.105/run |
|---|---:|---:|
| ±0.05 (width 0.10) | 16 | $1.68 |
| ±0.025 (width 0.05) | 62 | $6.51 |
| ±0.01 (width 0.02) | 385 | $40.42 |

Current headroom is **$0.104291**, below one further run, so 053 is the last paid
measurement.

But cost is the smaller problem. **Six positive labels is the real limit.** One
event is 16.7% of recall, so the metric can only take a handful of values and the
sd is a property of the reference set, not of the model. Sixteen more runs would
give a tight interval around a number that still rests on five windows and one
disputed coin-flip label. The per-class table above is more informative than any
aggregate, and it says the interesting facts plainly: three classes work, one is
unstable, two have never worked.

## What to state externally

Defensible: *"On a six-label development set, discovery-stage F1 is 0.64 ± 0.10
(n=6), against a single-pass baseline of 0.50. Three of six event classes detect
perfectly and stably; one is unstable; two are never detected. Full-game accuracy
is unproven and the holdout is untouched."*

Not defensible: any single run's 0.727, or any claim of generalisation.

## Budget

- Incremental: **$0.1048875** (5 calls)
- Ledger: **$11.088004125**; remaining headroom **$0.104291**
- Session total 043–053: **$1.4941519**

## Next

1. **Grow the reference set.** Annotation time, not spend. Target 40–60 labels
   across 15–20 windows, balanced made/missed, ≥4 instances per class. Every
   open question has now reduced to this one.
2. `block`: 0/6, never detected by any arm at any frame rate. Needs more than one
   reference instance before any experiment on it is readable.
3. Verify the 051 assist anchor fix when budget allows.
4. Default `verify_events=False` on throughput recipes; keep it on where a human
   reviews output, for the `potential_event` routing rather than for accuracy.

## Limitations

Six positive labels, five windows, two development games, one of them a coin
flip. Fixed reviewed windows, so proposer recall is still unmeasured and no
full-game claim is supported. The CI assumes runs are independent and identically
distributed, which is reasonable for repeated sampling of the same prompt but
untested. Holdout untouched; golden labels unmodified; no commit or push.
