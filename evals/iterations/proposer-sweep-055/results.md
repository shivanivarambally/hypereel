# Contiguous development sweep — F1 0.360 — 055

> Publication clarification, 16 September 2026: the counts are reproducible in [offline audit 056](../publication-audit-056.json), using half-open windows. This is one game segment, not an unbiased estimate across games. “Hallucinated,” “invented” and “empty” in the original interpretation below mean predictions unmatched to the source references; independent footage review is required to establish absence of real events. Earlier tests included a negative W3. The historical curated-versus-sweep difference is not a controlled estimate of curation's effect. Raw outputs and original numeric results are preserved.

Completed 16 September 2026. User authorized a $2 ceiling increase to measure
detection on windows that were not hand-picked.

**100 contiguous 10-second windows** covering 600–1600 s of game 1, tiled
uniformly with no reference to the golden set when choosing them. Discovery-only,
8 fps, same window geometry as every prior experiment so results are comparable.
Scored against 98 golden references derived from `source_event_type` +
`source_outcome`.

This is the first measurement in the project on a sample that cannot flatter the
system, and the first with real true-negative coverage.

## Headline

| Sample | Precision | Recall | F1 | Refs | Windows |
|---|---:|---:|---:|---:|---:|
| 7 reviewed windows (curated) | 0.67 | 0.75 | **0.706** | 8 | 7 |
| 4 density-picked windows | 0.44 | 0.18 | 0.258 | 22 | 4 |
| **100 contiguous windows (unbiased)** | **0.315** | **0.418** | **0.360** | **98** | 100 |

**F1 0.360.** Every number reported before 054 — 0.727, 0.636, the whole 043–053
arc — was measured on seven windows chosen *because* they contained human-reviewed
events. The curated sample inflated the result by roughly **0.35 F1**.

41 true positives, 89 false positives, 57 false negatives.

## Finding 1 — the model hallucinates on more than half of empty windows

53 of the 100 windows contain no golden event. This is the first time dead time
has ever been in the evaluation.

| Behaviour on empty windows | Count | Share |
|---|---:|---:|
| Correctly silent | 23 | 43% |
| **Invented at least one event** | **30** | **57%** |

The model produces events on the majority of windows where nothing happens. That
is the dominant source of the 0.315 precision, and it has been invisible for the
entire project because every previously evaluated window was selected for
containing an event.

For a highlight-reel product this is the more damaging failure mode: a reel
padded with invented plays is worse than a reel that misses some.

## Finding 2 — my 054 conclusion was wrong

054 concluded "the model under-proposes; the recall ceiling is at discovery."
That was measured on four windows chosen for maximum density, where it emitted 9
predictions for 22 events.

Across the unbiased sweep it emitted **130 predictions for 98 references** — it
*over*-proposes overall.

Both are true locally and the aggregate is the opposite of what I reported:

- On dense sequences it under-enumerates, missing events in a crowded possession.
- On sparse or empty windows it over-generates, inventing plays that are not there.

The 054 finding was itself an artefact of density-picked sampling, exactly the
error it was written to correct. Corrected here.

## Finding 3 — per-class, with the product-critical failure

| Class | TP/FP/FN | Precision | Recall | F1 |
|---|---|---:|---:|---:|
| `two_point_miss` | 17/21/9 | 0.45 | 0.65 | **0.531** |
| `offensive_rebound` | 5/10/6 | 0.33 | 0.45 | 0.385 |
| `turnover` | 9/16/14 | 0.36 | 0.39 | 0.375 |
| `steal` | 6/20/4 | 0.23 | 0.60 | 0.333 |
| `assist` | 1/1/2 | 0.50 | 0.33 | 0.400 |
| `free_throw_miss` | 1/2/5 | 0.33 | 0.17 | 0.222 |
| **`two_point_made`** | **1/2/9** | 0.33 | **0.10** | **0.154** |
| `defensive_rebound` | 1/11/6 | 0.08 | 0.14 | 0.105 |
| `free_throw_made` | 0/1/1 | 0.00 | 0.00 | 0.000 |
| `block` | 0/0/1 | — | 0.00 | 0.000 |
| `three_point_miss` | 0/5/0 | 0.00 | — | 0.000 |

**`two_point_made` recall is 0.10 — one made basket found out of ten.** HypeReel
exists to build highlight reels, and a made basket is the single most reel-worthy
event in the taxonomy. This is a product-level failure, not a metric nuance, and
it did not appear in any earlier measurement because W2 and W7 each contained
exactly one made basket and the model happened to find them.

Two other patterns:

- **`defensive_rebound` is near-random** (F1 0.105, 11 false positives). Combined
  with `offensive_rebound` at 0.385, rebound *team attribution* is where much of
  the noise lives — consistent with W5's offensive/defensive flip across runs.
- **`steal` has recall 0.60 but precision 0.23** (20 false positives). The model
  sees steals everywhere. Paired with `turnover` at 16 false positives, this is
  the possession-change family generating noise on ordinary play.

## What this does to the session's conclusions

| Conclusion | Status after 055 |
|---|---|
| Two-phase beats single-pass (0.727 vs 0.500) | Both measured on curated windows; the comparison may hold but the magnitudes do not |
| Consensus gives 0.727 deterministically | True on curated windows only |
| Reference set is the binding constraint | Wrong (054), and now definitively: 98 refs were reachable for $2 |
| Model under-proposes | **Wrong** — over-proposes 130:98 overall |
| Recall ceiling is at discovery | Half right: discovery is the problem, but through *precision* on empty windows more than recall on dense ones |
| Verifier fix (044), anchoring bug (051) | Stand — diagnosed from mechanism, not from the curated metric |

The verifier work now looks more valuable than 052 concluded, not less: a second
pass that rejects invented events is exactly what a 57% hallucination rate on
empty windows needs. 052 measured phase 2 as worth 0.000, but that was on curated
windows containing real events, where there was little to reject.

## Budget

- 055 incremental: **$2.005934** (100 calls)
- Ceiling raised $11.192294875 → **$13.192294875** on user authorization, recorded
  in `gemini-funded-budget.json`
- Ledger: **$13.165006**; remaining headroom **$0.027289**
- Session total 043–055: **$3.5711537**

## Next, in priority order

1. **Empty-window precision.** 57% hallucination on dead time is the largest
   single defect. Re-test phase 2 on empty windows specifically — 052's
   "verification is worth 0.000" was measured where there was nothing to reject.
   This is the cheapest high-value experiment left.
2. **`two_point_made` recall 0.10.** Product-critical. The reel cannot be built
   from events the detector does not find.
3. **Rebound attribution.** `defensive_rebound` F1 0.105 with 11 false positives;
   the rules gate (050) can now be tested against real violations, which it never
   saw on curated windows.
4. Re-baseline every earlier comparison on uncurated windows before quoting any
   of it.

## Limitations

One contiguous span of one game, 16.7 minutes of 46.5. Unbiased within that span
but not a random sample of the whole game, and game 2 is untested. Golden rows are
source-annotated with provisional boundaries, so matching is by window membership;
an event correctly detected but attributed to an adjacent window scores as a miss
on both. Single run, so no variance estimate at this scale. Discovery-only —
phase 2 was not run. Holdout untouched; golden labels unmodified; no commit or
push.
