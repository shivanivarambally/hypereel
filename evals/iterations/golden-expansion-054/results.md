# The reference set was never six labels — golden expansion and a much lower honest number — 054

Completed 15 September 2026. Triggered by the project owner pointing out that both
development games are fully labelled. They are. This corrects a claim I repeated
throughout the session and produces a substantially worse, substantially more
honest headline.

## What I had wrong

`evals/golden/golden_events.jsonl` holds **462 source-annotated events** covering
both development games end to end:

| Type | Count | | Type | Count |
|---|---:|---|---|---:|
| 2PT | 127 | | 3PT | 40 |
| TOV | 95 | | FT | 39 |
| DR | 47 | | AST | 21 |
| STL | 45 | | BLK | **5** |
| OR | 43 | | | |

I spent the session asserting that six positive labels were the binding
constraint and that `block` was unmeasurable with one instance. **`block` has
five references. The constraint was never the labels.**

### Why the golden set was being bypassed

The scorer used a six-label hand-adjudicated subset because
`expected_moment_type` is populated for only 100 of 462 rows. That is by design:
the golden set was built for **highlight selection**, where a miss, turnover or
rebound is an explicit *negative* — you do not want them in a reel — so those
rows carry a null expected label.

For **all-event detection**, the information is fully present in
`source_event_type` + `source_outcome`, which map onto the fourteen-label
taxonomy exactly. `scripts/score_against_golden.py` (new, offline) does that
mapping. Nothing was missing; the wrong field was being read.

Boundaries are `provisional` (event_time −5s/+4s), so matching is by window
membership rather than timestamp proximity.

## Correction 1 — references inside existing windows: 6, not 14

Re-scoring the already-recorded runs against golden raises the reference count
inside the seven recorded windows from 6 to **14**, and brings W6 and W7 into
scope for the first time.

Three session conclusions do not survive:

- **W2's `turnover` was never a false positive.** It is a genuine golden event
  (`TOV` at 758). I counted it as a taxonomy artefact or unadjudicated extra for
  the entire session. The same applies to W6's turnover.
- **W2's `assist` is a real golden event** (`AST` at 761). The anchoring bug
  diagnosed in 051 therefore cost a true positive, not a harmless extra.
- **W6, excluded everywhere as "qualitative", holds five golden events** and the
  model recovers two of them.

W7 also becomes scorable: golden says `three_point_made`, the model said
`two_point_made` — the make is right, the point value wrong. A different error
class from W1 and W4.

## Correction 2 — the honest number is far lower

Four new windows were run, chosen purely by golden-event density and never seen
by any prior experiment. Discovery-only, 8 fps, game 1, from the local source
video.

| Sample | TP/FP/FN | Precision | Recall | F1 | Refs |
|---|---|---:|---:|---:|---:|
| 7 reviewed windows (curated) | 6/3/2 | 0.67 | 0.75 | **0.706** | 8 |
| **4 new dense windows (unseen)** | **4/5/18** | **0.44** | **0.18** | **0.258** | 22 |
| **Combined, 11 windows** | **10/8/20** | **0.56** | **0.33** | **0.417** | **30** |

Recall falls from 0.75 to **0.18** on windows that were not hand-picked.

Every number reported before this — 0.727, 0.636, the whole 043–053 arc — was
measured on seven windows **selected because they contained human-reviewed
events**. That is a curated, favourable sample, and it flattered the system by
roughly 0.45 F1.

### Why: the model under-proposes

Across the four new windows the model emitted **9 predictions for 22 events**.

| Window | Golden events | Predicted |
|---|---:|---:|
| [808,818] | 6 | 2 |
| [658,668] | 6 | 5 |
| [2736,2746] | 5 | 2 |
| [1888,1898] | 5 | **0** |

W103 contains a missed two, an offensive rebound, a block, a steal and a
turnover, and returned nothing at all.

**The recall ceiling is at discovery, not classification.** The verifier work
(044), the rules gate (050), the anchoring fix (051) and the routing analysis
(052) all operate downstream of a stage that is not proposing most of what
happens. That reorders every remaining priority.

## What this does to earlier conclusions

| Conclusion | Status |
|---|---|
| Two-phase beats single-pass (0.727 vs 0.500) | Measured on curated windows only; untested on unseen ones |
| Reference set is the binding constraint | **Wrong** — 462 labels existed; the constraint is proposer recall |
| `block` unmeasurable with one instance | **Wrong** — 5 references exist; W103 contains one and it was missed |
| W2 `turnover` a false positive | **Wrong** — genuine golden event |
| Variance sd 0.100 is a property of the reference set | Partly right, but measured on the curated sample |
| Consensus gives 0.727 deterministically | True, on curated windows |

The verifier fix (044) and the assist anchoring bug (051) stand — both were
diagnosed from mechanism, not from the curated metric.

## Budget

- 054 incremental: **$0.0710678** (4 calls, one per window, discovery-only)
- Ledger: **$11.159071900**; remaining headroom **$0.033223**
- Session total 043–054: **$1.5652197**

Budget is now effectively exhausted. Expanding further is cheap in principle —
the full source video for game 1 is local at
`downloads/KBETdDRM70Q.studio-720p.mp4`, and discovery-only costs about $0.018
per window — so roughly $2 would cover ~100 windows and several hundred
references.

## Next, reordered

1. **Fix proposer recall.** The model returns 9 of 22 events on dense sequences
   and zero on one window. Nothing downstream matters until discovery proposes
   what is there. Candidates: longer windows, explicit "enumerate every
   possession event" framing, or a sweep over the full game rather than
   pre-cut clips.
2. **Re-baseline on uncurated windows.** Every comparison in this repo should be
   restated against golden-derived references on windows chosen by density or at
   random, not by prior human review.
3. `block` is now measurable (5 references) and was missed in the one new window
   containing it.
4. Verify the 051 assist anchor, which now matters more since the assist is a
   scorable reference.

## Limitations

The four new windows are game 1 only, deliberately chosen as the *densest*
available, so 0.258 is a hard-case estimate rather than a uniform sample; a
random sample would likely fall between 0.258 and 0.706. Golden rows are
source-annotated and unverified for this project, with provisional boundaries,
so matching is by window membership. 30 references is still small. The holdout
is untouched and golden labels are unmodified. No commit or push.
