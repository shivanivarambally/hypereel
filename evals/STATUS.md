## Current publication audit — 2026-09-16T00:39:02+05:30

Latest live evidence is **055**, discovery-only at 8 fps on 100 contiguous windows spanning 600–1600s of game 1. Offline replay **056** reproduces TP41/FP89/FN57: precision .3154, recall .4184, F1 .3596, against 98 source-annotated events. The replay fixes scorer game selection for non-legacy window IDs and uses half-open boundaries; historical raw outputs and gold remain unchanged. [Replay](iterations/publication-audit-056.json) · [review and remaining issues](../docs/REVIEW_2026-09-16.md).

Interpretation corrections to earlier wording below: this is **one non-density-selected development segment**, not a population-wide “real number” or unbiased estimate across all games. Thirty of 53 windows with no source reference contain a prediction; these are **unmatched outputs requiring adjudication**, not automatically proven hallucinations. Differences from curated scores cannot isolate a causal curation effect because reference policies and samples differ. Older tests already included a reviewed negative W3. The complete golden set has 462 source-labeled rows; earlier six-event limits described an adjudicated subset, not a lack of data. Two-phase versus discovery-only remains untested on the broader sweep.

Ledger $13.165006125; authorized cumulative ceiling $13.192294875; remaining **$0.02728875**. No new paid calls or ceiling changes during this audit. Full games and final holdout remain unrun. Priorities: adjudicate unmatched/empty-reference-window predictions, improve made-basket recall and rebound attribution, and evaluate verification on the same broader sample when budget is authorized. README, evaluation guides and handoff are updated; historical reports/submission snapshots are retained.

---

## Historical interpretation — contiguous sweep F1 0.360 — 055 — 2026-09-16

User authorized a $2 ceiling increase ($11.192294875 -> $13.192294875) to measure detection on windows that
were **not hand-picked**. 100 contiguous 10s windows tiling 600-1600s of game 1, chosen with no reference to the
golden set, discovery-only at 8 fps, same geometry as every prior experiment. Scored against **98 golden
references**. 100 calls, **$2.005934**; ledger **$13.165006**; headroom $0.027289. Session total 043-055: $3.5712.

| Sample | Prec | Recall | F1 | Refs |
|---|---:|---:|---:|---:|
| 7 reviewed windows (curated) | 0.67 | 0.75 | 0.706 | 8 |
| 4 density-picked windows | 0.44 | 0.18 | 0.258 | 22 |
| **100 contiguous windows (unbiased)** | **0.315** | **0.418** | **0.360** | **98** |

**The real number is F1 0.360.** Curation inflated everything reported before 054 by roughly **0.35 F1**.

**Finding 1 - the model hallucinates on 57% of empty windows.** 53 of 100 windows contain no golden event; the
model correctly stayed silent on 23 and **invented events on 30**. First true-negative coverage in the project,
and the dominant source of the 0.315 precision. For a highlight product this is the worse failure mode: a reel
padded with invented plays beats no reel less than a sparse honest one does.

**Finding 2 - my 054 conclusion was wrong.** 054 said "the model under-proposes". Across the unbiased sweep it
emitted **130 predictions for 98 references** - it over-proposes. It under-enumerates on dense sequences and
over-generates on sparse ones; 054 was itself an artefact of density-picked sampling, the exact error it was
written to correct.

**Finding 3 - `two_point_made` recall is 0.10.** One made basket found in ten. HypeReel exists to build highlight
reels and a made basket is the most reel-worthy event in the taxonomy; this is product-level, not a metric
nuance. It stayed hidden because W2 and W7 each held exactly one made basket and the model happened to find
them. Also: `defensive_rebound` F1 0.105 with 11 false positives (rebound team attribution is a major noise
source), and `steal` recall 0.60 at precision 0.23 (20 false positives).

**This reopens 052.** Phase 2 was measured as worth 0.000, but on curated windows full of real events where
there was little to reject. A 57% hallucination rate is exactly what a rejecting second pass is for, and the
rules gate (050) can finally be tested against real violations rather than firing zero times.

Next in priority order: empty-window precision; `two_point_made` recall; rebound attribution; then re-baseline
every earlier comparison before quoting it. See evals/iterations/proposer-sweep-055/results.md.

---

## Historical — golden set was always there; honest number is far lower — 054 — 2026-09-15

**Correction to a claim I repeated all session.** The owner pointed out both development games are fully
labelled. They are: `evals/golden/golden_events.jsonl` holds **462 source-annotated events** across both games
(2PT 127, TOV 95, DR 47, STL 45, OR 43, 3PT 40, FT 39, AST 21, **BLK 5**). I asserted throughout that six
positive labels were the binding constraint and that `block` was unmeasurable with one instance. **Both wrong.**

**Why it was bypassed:** `expected_moment_type` is populated for only 100/462 rows, because the set was built
for highlight *selection*, where a miss or turnover is an explicit negative. For all-event *detection* the
signal is in `source_event_type` + `source_outcome`, which map onto the 14-label taxonomy exactly. New offline
`scripts/score_against_golden.py` does that mapping. Nothing was missing; the wrong field was being read.

**Correction 1 - references inside existing windows go 6 -> 14**, bringing W6 (5 events) and W7 into scope.
Three conclusions overturned: W2's `turnover` was never a false positive but a genuine golden TOV; W2's
`assist` is a real golden event, so the 051 anchoring bug cost a true positive; W6, excluded everywhere as
"qualitative", holds five golden events and the model recovers two.

**Correction 2 - the honest number is far lower.** Four new windows, chosen purely by golden density and unseen
by any prior experiment, run discovery-only from the local source video:

| Sample | TP/FP/FN | Prec | Recall | F1 | Refs |
|---|---|---:|---:|---:|---:|
| 7 reviewed windows (curated) | 6/3/2 | 0.67 | 0.75 | 0.706 | 8 |
| **4 new dense windows (unseen)** | **4/5/18** | **0.44** | **0.18** | **0.258** | 22 |
| **Combined, 11 windows** | **10/8/20** | **0.56** | **0.33** | **0.417** | 30 |

Recall falls from 0.75 to **0.18** on windows that were not hand-picked. Every number before this - 0.727,
0.636, the whole 043-053 arc - was measured on seven windows selected *because* they contained human-reviewed
events. That curated sample flattered the system by roughly 0.45 F1.

**Root cause: the model under-proposes.** 9 predictions for 22 events across the new windows; one window
containing a missed two, an offensive rebound, a block, a steal and a turnover returned **nothing at all**.
**The recall ceiling is at discovery, not classification** - which means the verifier fix (044), rules gate
(050), anchoring fix (051) and routing analysis (052) all operate downstream of a stage that is not proposing
most of what happens. That reorders every remaining priority. The 044 and 051 findings still stand; both were
diagnosed from mechanism rather than from the curated metric.

054 spend **$0.0710678**; ledger **$11.1590719**; **headroom $0.033223**, effectively exhausted. Session total
043-054: $1.5652197. Expanding is cheap in principle - game 1's full video is local and discovery-only is
~$0.018/window, so ~$2 covers ~100 windows. Holdout untouched; golden labels unmodified. See
evals/iterations/golden-expansion-054/results.md.

---

## Historical — verify_events flag, discovery-only validated, full statistics — 053 — 2026-09-15

Implemented the 052 recommendation: `Recipe.verify_events: bool|None`, a per-recipe override for the second
pass, with `verification_enabled(recipe, settings)` as the single decision point. **Correctness note:** turning
verification off previously also disabled multi-event discovery by falling back to the single-label path, which
would have discarded the capability the gain comes from (051). The temporal path now stays active and only the
second provider call is skipped. **459 passed, 4 skipped.**

**Cost saving confirmed live:** discovery-only ran W1-W5 in **5 calls / $0.1048875** against two-phase's 9 calls
/ $0.1908487 - **45% cheaper** - and scored 3/2/3, F1 0.545, identical to 050's two-phase result on the same
windows.

**Full statistics, discovery stage, n=6** (045/046/047/048/050/053): F1 mean **0.636**, sd 0.100, 95% CI
**[0.532, 0.741]**. Precision mean 0.700, CI [0.585, 0.815]. Recall mean 0.583, CI [0.488, 0.679]. Single-pass
control 0.500; consensus over 045-048 gives 0.727 deterministically. The distribution is **bimodal, not
continuous** - every run is either 4/1/2 or 3/2/3, and the difference is entirely whether W4 returns
`free_throw_miss` or `free_throw_made` on that sampling.

**Per-class, n=6:** `steal`, `two_point_made` and `missed_field_goal` all 6/6, F1 1.000 and stable.
`free_throw_miss` 3/6, a coin flip. `free_throw_made` 0/6 (W1's systematic misread) and `block` 0/6 (never
detected by any arm at any frame rate). Every false positive in the set belongs to W1.

**On the request for confidence: it is not achievable here, and more runs will not fix it.** At sd 0.100, a CI
width of 0.10 needs 16 runs ($1.68), 0.05 needs 62 ($6.51), 0.02 needs 385 ($40). Headroom is **$0.104291**,
below one further run, so 053 is the last paid measurement. But cost is the smaller problem: with six positive
labels one event is 16.7% of recall, so the sd is a property of the reference set rather than the model. The
per-class table is more informative than any aggregate. **Defensible external claim:** "discovery-stage F1
0.64 +/- 0.10 (n=6) on a six-label development set against a 0.50 single-pass baseline; three of six classes
stable and perfect, one unstable, two never detected; full-game accuracy unproven, holdout untouched." Not
defensible: any single run's 0.727.

Session total 043-053: **$1.4941519**. Holdout untouched; golden labels unmodified. See
evals/iterations/discovery-only-053/results.md.

---

## Historical — confidence-routing design analysis — 052 — 2026-09-15

No inference, no spend. Ledger unchanged at $10.983116625; headroom $0.209178. Evaluates a proposal to skip
phase 2 when phase 1 is confident and run it only on low confidence or multiple/overlapping events.

**Q1: phase-1 confidence is not calibrated in the gating range.** Adjudicated families only: >=0.90 is 71%
correct (15/21), 0.70-0.89 is 75% correct (3/4). The high bucket is slightly *worse* than the middle, so there
is no usable signal between 0.70 and 1.00 - exactly where a threshold would sit. All four confident errors are
the windows this session has been chasing: W1 `three_point_miss` @0.95, W1 `two_point_miss` @0.95 and @0.90,
W4 `free_throw_made` @0.95. **A confidence gate would skip verification on precisely the cases that need it.**
Caveat: only 4 items in the middle bucket, so the ordering is weak evidence; the confident-error list is not.

**Q2: phase 2 changes the scored metric by exactly zero.** discovery F1 == confirmed F1 in all five post-fix
runs (045/046/047/048/050, delta +0.000 each). The 050 transition log agrees: 6 confirmed_unchanged,
2 routed_to_review, 0 relabels. Combined with 051 - which showed the entire two-phase gain comes from
multi-event *discovery*, a phase-1 capability - verification is currently not earning its 2x inference cost on
this set.

**Recommendation: the instinct is right, the mechanism is not, and there is a cheaper decision available.**
Do not gate on confidence. Do not build the router yet: routing phase 2 to multi-event windows sends it where
phase 1 already did the work, and the data already shows discovery-only scores identically at half the cost, so
a router is more machinery than a config flag for a decision already made. Prefer a per-recipe phase-2 flag,
default off for throughput and on for human-reviewed work. **Keep phase 2 for its safety behaviours, not its
accuracy**: potential_event routing (W5 @0.49 correctly queued), catching W4's confident false positive (044),
and relabelling three_point_miss -> free_throw_miss (049). Those do not show in F1 on six labels.

**Blocking constraint unchanged:** with sd 0.100 and six positive labels, a real phase-2 effect of +/-0.05 would
be invisible. Reference-set size gates this decision as it gates every other open question. See
evals/iterations/routing-analysis-052/summary.json.

---

## Historical — W2 assist failure diagnosed, per-event-type comparison — 051 — 2026-09-15

No inference, no spend. Ledger unchanged at $10.983116625; headroom $0.209178. **459 passed, 4 skipped.**

**W2 assist: a spec gap, not a model failure.** Both phases agreed it was an assist by the same two players and
disagreed on which instant an assist is anchored to. Phase 1 anchored the resulting basket (t=12.1) while its own
reason described the pass at 08.7; phase 2 anchored the pass (t=8.7). The 3.4s gap exceeded the 2s guard in
`parse_verification`, which rejects a larger shift as "Verifier substituted a different action time", so a
well-formed `confirmed` response was discarded on a timestamp convention. Root cause: the discovery prompt names
anchors for shots, possession changes and blocks but **not assists** - the one event in the taxonomy spanning two
separated moments. Both prompts now specify "for an ASSIST anchor the moment of the PASS, not the resulting
basket", with phase 2 told to use phase 1's anchors, plus a regression test. **Not verified live** - headroom is
under one full-set run. The loss cost no F1 in 050 because `assist` is outside W2's reference set, but it
generalises to any two-moment event and was only visible because of the 050 transition log.

**Per-event-type comparison, answering whether two-phase helps for different event types.** Summed over the five
post-fix runs; the single-pass control is frozen 038 reused, so it has zero variance by construction.

| Event type | Single-pass | Two-phase | Verdict |
|---|---|---|---|
| `steal` | 0/5 | **5/5** | two-phase wins |
| `missed_field_goal` | 0/5 | **5/5** | two-phase wins |
| `two_point_made` | 5/5 | 5/5 | tie |
| `free_throw_miss` | **5/5** | 3/5 | **two-phase loses** |
| `block` | 0/5 | 0/5 | neither ever detects it |
| `free_throw_made` (W1) | 0/5 | 0/5 +2FP | neither |

**Two-phase wins exactly where a window holds more than one scorable event** - W2 has a steal and a basket, W5 a
block and a missed shot. Single-pass emits one label per window, so those were structurally unreachable rather
than missed; both classes move 0% to 100%. **It loses on single-event precision**: `free_throw_miss` falls 5/5 to
3/5 on W4's instability. Neither solves `block` (never detected by any arm at any fps, the only pure recall
failure left) or W1's `free_throw_made`. Every false positive in the table is one of W1's wrong shot labels.

**So the aggregate 0.500 -> 0.655 decomposes as +2 classes recovered, -1 degraded, 3 unchanged** - a multi-event
capability win offset by a single-event stability loss, not a general improvement. Prefer two-phase for windows
expected to hold multiple events; consensus over repeats (0.727 deterministic) is the remedy for the stability
loss at 4x inference. See evals/iterations/assist-anchor-051/results.md.

---

## Historical — rules gate, phase-transition observability, W1 occlusion refuted — 050 — 2026-09-15

**W1 occlusion hypothesis REFUTED.** Owner screenshot at ~2s shows the rim and net clearly visible and
unoccluded, ball at the net. The model has a clean view of a visible outcome and reports the opposite. That is a
perception failure, not a data limitation, and no prompt, rule or frame-rate change addresses it. W4's verifier
occlusion report remains true for W4 only and should not be generalised.

**Built:** (1) `apply_rules_gate`, a per-window deterministic legality gate wired into `classify_moments` —
`illegal` violations force `potential_event` at confidence <=0.49 with the rule as the reason and the expert flag
raised, `review` violations raise the flag only, and it never deletes an event since code cannot tell which of
the two labels is wrong. (2) Phase-1 -> phase-2 observability: every proposal now yields a `Transition` with both
labels, the verdict, the verifier's reason and any rule violation, bucketed as confirmed_unchanged /
corrected_relabel / routed_to_review / rejected / rules_blocked, with `transition_metrics()` aggregating survival
rate, relabels and rules fired into `report.json`. This answers what was previously unanswerable: when phase 1
proposes N events and phase 2 keeps fewer, why.

**Taxonomy bug found and fixed:** `validate_sequence` knew only the 14-label set, so legacy `made_basket` /
`three_pointer` recipes were unrecognised as shots and R5 fired spuriously. Same class as the 044
verification-prompt bug. Both taxonomies now covered with a regression test. **458 passed, 4 skipped.**

**Result:** confirmed 3/2/3, P 0.60, R 0.50, **F1 0.545** — the low end of the measured band, not a regression.
Five post-fix runs now read 0.727 / 0.727 / 0.727 / 0.545 / 0.545, mean **0.655**, sd **0.100**. Control 0.500;
consensus over 045-048 gives 0.727 deterministically. **The rules gate fired zero times** — no illegal
combination occurred, so it was a no-op safety net: not shown to help, shown not to harm.

**Observability's first find:** W2's `assist` was routed to review as an *invalid verification event* while the
verifier's own prose describes a textbook assist (full-court pass directly to a made layup). That prefix comes
from `parse_verification`'s exception path, so it is a schema/parse failure, not a judgement — the verifier
agreed and its answer was discarded on a technicality. A silent recall loss, invisible before this log.

Incremental spend **$0.1908487**; ledger **$10.983116625**; **headroom $0.209178**, now under one full-set run.
Session total 043-050: $1.3892644. Holdout untouched; golden labels unmodified. See
evals/iterations/rules-gate-050/results.md.

---

## Historical — basketball rules encoded, verified against NBA sources, tested on W1 — 049 — 2026-09-15

Following W1 adjudication (free throw **made**, ball collected by Black #24), the governing rules were verified
against official NBA sources, written to `docs/BASKETBALL_RULES.md` with per-rule citations and Verified /
Inferred / Convention status, encoded in `src/hypereel/evaluation/basketball_rules.py`, and added to both the
discovery and verification prompts. **457 passed, 4 skipped** (14 new rules tests).

Verified from NBA.com Stat Glossary and NBA Rules 4, 6 and 9: a rebound requires a *missed* shot; a made free
throw is followed by an opponent throw-in so collecting the ball is an inbound, not a rebound; a non-final free
throw leaves the ball dead. That a missed *final* free throw leaves the ball live is marked Inferred, following
from Rule 6's converse rather than stated verbatim. **One correction to the earlier draft:** it said an
uncontrolled recovery gives "a jump ball or alternating-possession throw-in", conflating codes. The NBA uses a
jump ball and has no possession arrow; alternating possession is NFHS/FIBA, and the owner's original statement
was correct. **League caveat recorded:** the footage is amateur/club and likely NFHS or FIBA, so R3 is marked
NBA-specific; R1/R2/R4/R5 are consistent across codes.

**RAG was considered and rejected.** The rule set is one page and closed, so there is no corpus to search;
retrieval would add a failure mode (missing the free-throw rule on a free-throw window) plus per-window cost for
no gain over a constant string. The model was not ignorant of the rules, it confabulated from visual ambiguity.

**W1 result: half the error is fixed.** Shot type moved from field goal (8 runs) to **`free_throw_miss`**, with
the verifier correcting phase 1 and citing the foul line and players lined along the key. The outcome is still
wrong: it asserts rim contact and a miss at 0.95 confidence where the free throw was made. The model has moved
from an incoherent story to a self-consistent but wrong one, and validation correctly fires on the truth-shaped
error (`free_throw_made` + rebound = illegal) but not on the current output. **That is the limit of rules:
they reject impossible combinations, not plausible sequences built on a misread outcome.** The original
back-inference theory is weakened, since naming the free throw did not remove the miss; the model asserts
positive rim contact, pointing at direct misperception, consistent with W4's verifier reporting the hoop is
occluded from this camera.

Incremental spend **$0.0436155**; ledger **$10.792267875**; headroom **$0.400027**. Session total 043-049:
$1.1984157. `validate_sequence` is tested but not yet called by the pipeline. Holdout untouched; golden labels
unmodified. See evals/iterations/rules-encoding-049/results.md.

---

## Historical — W1 adjudicated: reference correct, model systematically wrong — 2026-09-15

Human review of W1 confirms **the free throw was made**, roughly the middle of the 4.5-second excerpt. The
reference `free_throw_made` is **correct** and the model is wrong. The 0.909 sensitivity case from the 046-048
writeup is **ruled out**; consensus stands at **F1 0.727** (4/1/2, precision 0.80, recall 0.67) against the
0.500 single-pass control.

This reclassifies W1 from a disputed label to a **confirmed systematic model error**. All eight runs (038, 040,
041, 043, 045, 046, 047, 048) reported a missed field goal plus defensive rebound. The model places its event at
1.875s file-relative against a human observation near 2.0-2.3s, so it is examining the correct moment and
misreading **both** attributes: shot type (field goal vs free throw) and outcome (missed vs made). Eight for
eight in the same direction is systematic, not sampling variance.

Working hypothesis, untested: the rim is plausibly occluded from this camera, as W4's verifier explicitly
reported for the adjacent window. If the model cannot see the ball drop and then observes a player collecting
the ball from under the net, it may read that as a defensive rebound and back-infer a miss, making W1 one error
with two symptoms rather than two. A prompt remedy exists if so: a rebound requires a *visible* missed shot,
never an inferred one. Three observations requested from the reviewer (free-throw setup visible? rim visible at
ball-through? player collecting the ball from under the basket after the make?).

Both disputed labels are now resolved and **both references were correct**. Remaining errors on this set: W1
(systematic, above) and W5 `block` (never detected by any arm, run or frame rate). Ledger unchanged at
$10.748652375; headroom $0.443642. See evals/adjudication/adjudications.json.

---

## Historical — variance estimate and majority-vote consensus — 046/047/048 — 2026-09-15

Three unchanged repeats of 045 on W1-W5 at 8 fps, control reused from 038. 27 calls, zero errors, incremental
**$0.5710103**; ledger **$10.748652375**; remaining headroom **$0.443642**. Session total 043-048: $1.0548003.

**Variance quantified:** confirmed F1 0.727 / 0.727 / 0.727 / 0.545, mean **0.682**, sd **0.091**, spread 0.182.
Large relative to the gain but not large enough to explain it away: the worst of four runs still beats the
0.500 single-pass control and the prior two-phase 0.400. The verifier fix survives the check. The core event of
each window is stable; the periphery is not (shot type wobbles within the correct outcome family, secondary
events appear and disappear, rebound team attribution flips). W4 is correct in 3 of 4 runs, so every report
before 045 sampled the wrong side.

**Consensus removes the variance.** New `scripts/score_consensus.py` (offline, no spend) votes labels across
repeats: **4/1/2, precision 0.80, recall 0.67, F1 0.727, identical at thresholds 0.50 and 0.75 and
deterministic.** That is the best single run's score rather than the mean, at 4x inference per answer. Prefer
threshold 0.75 in production: same score, fewer unverified extras reaching a reviewer.

**Only two errors remain under consensus.** W5 `block`, never detected by any arm in any run at any frame rate;
and W1, whose reference is now contradicted by **eight independent runs** all reporting a missed field goal plus
defensive rebound against `free_throw_made`. Sensitivity: if that reference is wrong, consensus becomes 5/0/1,
precision 1.00, recall 0.83, **F1 0.909**.

Stopped deliberately with headroom intact; further repeats will not move a consensus already stable across both
thresholds. **Next and blocking: re-adjudicate W1** (free, decides 0.727 vs 0.909), then grow the reference set
past six labels, which is now the constraint on every remaining question. 443 passed, 4 skipped. Holdout
untouched; golden labels unmodified. See evals/iterations/variance-consensus-046-048/results.md.

---

## Historical — fixed verifier on the full development set — 045 — 2026-09-15

Applied the 044 verifier fix to all seven windows at 8 fps, single-pass control reused frozen from 038.
Thirteen video calls, zero errors, incremental spend **$0.2735783**; ledger **$10.177642175**; remaining
headroom **$1.014653**. Session total across 043/044/045: $0.4837898.

**Two-phase now beats the one-phase baseline**, reversing the conclusion standing since 041. On the six
reviewed positive labels in W1-W5: discovery, confirmed, confirmed_plus_potential and selected all report
**4/1/2, precision 0.80, recall 0.67, F1 0.727**, against the frozen single-pass control at 2/0/4, F1 0.500.
Previous two-phase confirmed was 2/2/4, F1 0.400. All four stages agreeing means no events are lost downstream
of discovery. W4 returned the correct `free_throw_miss`.

**Confound, recorded deliberately: the gain cannot be cleanly attributed to the verifier fix.** Discovery
output changed between runs although discovery was not modified. W4 read `free_throw_made` in 040, 041, 043
and 044 and `free_throw_miss` in 045; W1's shot type moved from `two_point_miss` to `three_point_miss`; W5's
second event moved from `offensive_rebound` to `defensive_rebound`. Run-to-run variance is at least one event
on three of five scored windows, and with six labels one event is 16.7% of recall, so the noise is comparable
in size to the measured gain. The only direct evidence the fixed verifier can reject a false proposal remains
044, where it routed W4 to human review with independent reasoning. In 045 it echoed all 11 classifications
because discovery left nothing to catch.

**Next and binding: repeat 045 unchanged to estimate variance** (~$0.27 per repeat, or ~$0.35 restricted to
W1/W4/W5) before any further comparison on this set. Then re-adjudicate W1, now contradicted by five runs, and
grow the reference set past six labels. 443 passed, 4 skipped. Holdout untouched; golden labels unmodified.
See evals/iterations/two-phase-e2e-045/results.md.

---

## Historical — verifier de-anchoring and shot-family criteria — 044 — 2026-09-15

**W4 adjudicated by human review: the reference `free_throw_miss` is correct and the model's repeated
`free_throw_made` was wrong.** That ruled out label error and made the verifier the suspect.

Two compounding bugs found. (1) The verifier was rubber-stamping: `verification_reason` was byte-identical to
the discovery reason in **32 of 33 classifications** across 040/041/043, the sole exception being W5 at 0.49
confidence. (2) The contrastive reject-criteria in `build_verification_prompt` were keyed to a retired
four-label taxonomy (`made_basket`, `three_pointer`, `steal`); against the fourteen-label recipe **only `steal`
ever matched**, so every shot label used the generic fallback. The criterion W4 needed already existed under
`made_basket` ("accept only with visible ball-through-rim/net evidence") and never fired.

Fixed both: re-keyed shot-family criteria to the taxonomy in use with explicit make/miss outcome tests and
hidden-outcome-is-UNCERTAIN, and de-anchored the prompt so the verifier writes an independent `observed`
description before judging the proposal.

Re-ran W2 (control) and W4 at 8 fps. On three reviewed labels, **confirmed precision rose 0.67 -> 1.00 and
confirmed F1 0.667 -> 0.800**; discovery unchanged as expected. W4 moved from `free_throw_made` @0.95
*confirmed* to @0.49 *potential_event* with an independent verification reason: the hoop and net outcome are
completely occluded from that camera angle. W2's three correct events are unaffected.

Four video calls, incremental spend **$0.0899640**; ledger **$9.904063875**; remaining headroom **$1.288231**.
443 passed, 4 skipped. Holdout untouched; golden labels unmodified. Validates the mechanism on two windows, not
the magnitude. See evals/iterations/two-phase-e2e-044/results.md.

---

## Historical — frame-rate ablation on shot-outcome windows — 043 — 2026-09-15

User-authorized experiment from 042. Re-ran discovery + verification on **W1/W4/W5 only at 8 fps** (historical
value 4), everything else fixed: same clips, media hashes, prompt, model and recipe; single-pass control reused
from 038. Six video calls, zero errors, incremental spend **$0.1202475**; ledger **$9.814099875**; remaining
headroom **$1.378195**.

**Hypothesis disconfirmed.** On the four reviewed positive labels in these windows, discovery scored 1/2/3
(F1 0.286) at both 4 fps and 8 fps, identical at every stage. Doubling temporal resolution changed zero scored
labels, so the frame-interval explanation for outcome inversion is not the binding constraint.

Secondary effect is real: fps buys confidence and coverage, not correctness. W5's `two_point_miss` rose from
0.49 to 0.85 and moved from the human-review queue to auto-confirmed, and a second event (`offensive_rebound`)
was recovered that 4 fps missed. Event timestamps sharpened to 1/8-second boundaries.

W4 persists: `free_throw_made` at 0.90 with the specific claim "ball goes through the basket at around 00:08.7",
produced independently at two frame rates, against a `free_throw_miss` reference that the 038 single-pass control
agrees with. W1 is now contradicted by four independent runs across two pipeline designs and two frame rates.

**Next action is free and blocking: human re-adjudication of W1 and W4.** Two of four labels in this subset are
contradicted by every run ever made against them; if both are wrong, discovery here is 3/0/1 rather than 1/2/3.
No further model tuning is decidable until the reference set is trusted. 443 passed, 4 skipped. Holdout untouched;
golden labels unmodified. See evals/iterations/two-phase-e2e-043/results.md.

---

## Historical — offline family re-score and fps instrumentation — 042 — 2026-09-15

No inference, no spend; ledger unchanged at $9.693852375, headroom $1.498442. Re-scored 038-041 under a
general label-family matcher (subsumption + steal/turnover alias) replacing the window-5 special case:
**every stage scored identically to exact matching, so taxonomy overlap was not suppressing accuracy.**
Negative result retained for generality and auditability, not for a number. Newly scored: 040 `selected`
F1 0.222 vs 041 0.400, confirming 041's multi-label-per-clip change closed the selection regression;
`selected` now equals `confirmed`. Identified that `confirmed` is the wrong headline metric because W5 is
the only discovery/confirmed delta and it was correctly routed to human review at 0.49 confidence;
`confirmed_plus_potential` (F1 0.545) is the honest system output. All remaining errors except `block` are
made-versus-missed, with W4 inverting a free-throw outcome at 0.95 confidence where single-pass was
correct. W1 flagged for re-adjudication: three independent runs describe missed FG + rebound against a
`free_throw_made` reference. Added `gemini_video_fps` (default 4, unchanged) replacing six hardcoded
literals, enabling the next experiment. 443 passed, 4 skipped. Golden labels unmodified; holdout untouched.
See evals/iterations/rescore-family-042/results.md.

---

## Historical evaluation — 2026-09-15T19:54:00+05:30

Implemented and tested multi-event timestamped discovery, supported verifier relabeling, and retention of multiple event annotations in overlapping selected footage. Live run 040 plus zero-vision-call selection replay 041: discovery finds 3/6 reviewed events (recall 50%, F1 54.5%); verification confirms 2/6 (recall 33.3%, F1 40%), retaining the third for review. Original one-phase control F1 is 50%; previous two-phase 039 F1 was 28.6%. **Two-phase automatic accuracy is not better than the original one-phase baseline.** Partial, tiny development sample; conditional precision; no holdout use.

442 passed, 4 skipped, 1 holdout test deselected. Real graph/UI rendered 15-second automatic and 8-second simulated-review clips. Additional estimated spend $0.14822775; cumulative $9.693852375; remaining $1.4984425 under unchanged ceiling. Full-game run remains unperformed because recognition quality is not established. Next: independently check W1/W4 media/reference disagreements and W6 team attribution before further verification experiments. [Detailed results and iteration history](iterations/two-phase-e2e-041/results.md). No commit/push.

---

## Historical evaluation — 2026-09-15T19:32:14+05:30

User increased the local cumulative ceiling by $2 to **$11.192294875**. Completed live production two-phase evaluations 038–039 and real graph/UI approval, rendering and download checks. Additional estimated spend **$0.3790425**; cumulative ledger **$9.545624625**; remaining **$1.64667025**. This is local accounting, not account credit purchase.

Workflow passes; recognition improvement is not established. Current production emits one label per window. On six scorable reviewed labels in W1–W5, the fresh single-pass control found 2 (recall 33.3%, F1 50.0%); final two-phase auto-output found 1 (recall 16.7%, F1 28.6%), with one additional reference retained as a potential event. These are window-label metrics conditional on adjudicated families, not directly comparable with earlier timestamped event scores. W6/W7 are qualitative. No holdout use.

Fixed hidden-evidence rejection, foul-related expert escalation and stale duration after human review. **431 passed, 4 skipped, 1 holdout test deselected.** Actual UI tests rendered 15-, 9- and 8-second videos. Review actions were simulated and did not change golden data. Two-phase mode remains opt-in. Next required improvement: multi-event timestamped discovery plus verification that can correct a label. See [full results](iterations/two-phase-e2e-039/results.md) and [machine-readable summary](iterations/two-phase-e2e-039/summary.json). No commit/push.

---

## Current documentation checkpoint — 2026-09-13T12:33:30+05:30

Latest submission: [single-file HTML under 10 MB](../HypeReel-Breakout-Submission-under-10MB.html); the [README](../README.md) links both initial and evaluation/testing recordings. Run 032 remains the latest documented six-clip live-demo result: 87 seconds from a ten-minute both-teams excerpt, 469.46 seconds to complete. Development micro-F1: Gemini 0.370, MiniCPM 0.125, Gemini + transcript 0.348 (eight windows, fourteen references). Full-game accuracy remains unproven; final holdout unused. Last recorded full-suite checkpoint: 411 passed, 4 skipped, 1 holdout test deselected; not rerun for this documentation audit.

Ledger read at this timestamp: $8.992221; remaining local funded cap $0.200073. This is local accounting, not a verified Google balance. Older dated statuses below are historical; do not use their remaining budgets or launch-state claims as current observations.

---

## Commit/push checkpoint — 2026-09-13T00:56:24.665196+05:30

User authorized committing and pushing all pending project changes. Full pre-push suite:411 passed,4 skipped,1 final-holdout test deselected; one legacy Gemini SDK warning. Demo integration029, live UI030, failed three-clip031, successful six-clip032 and subsequent user render/approval feedback fixes included. User's own later render output verified89.5seconds; no claim its Chrome gate2 was visually inspected. Provider spend ledger $8.982478125; funded use $1.790183 of$2, remaining $0.209817. This is insufficient for another similar ~$0.53 full inference run within the current cap. No paid calls made for commit validation; do not reset ledger.

Code, recipes, tests, raw response/usage records and timestamped notes are included. Credentials, local source/render media, preview cache, runtime lock and working scratch remain excluded. Live server remains running; pushing does not redeploy/restart it. Existing historical “uncommitted” entries describe their original checkpoint and are superseded by this commit preparation.

---

## Historical — : six-clip live demo 032 — 2026-09-13T00:24:02.826138+05:30

Fresh both-teams Gemini run on a continuous ten-minute development excerpt selected six non-overlapping clips and rendered an87-second reel in469.46s (~$0.534). Full app/agent diagram and both HITL video review gates restored at ?demo=full-flow; root and old live-demo URL route there. No saved classifications in live mode. 411 tests pass, actual six-player UI/MP4 checks pass. 031 only produced three clips; preserved. Read multiclip-live-032/results.md for evidence, scope, budget and launch state. Full-game accuracy remains unproven; holdout untouched.

---

## Historical — : Live HITL demo 030 verified — 2026-09-12T23:59:15.148085+05:30

Fresh live Gemini analysis through actual UI selected a clip, paused for human video review, then rendered and displayed/downloaded the reel after approval. New /?demo=live-demo and root use fixed real 40-second source and dedicated recipe; advanced form at ?demo=live. Not a replay; not full-game accuracy validation. 31.99 seconds, $0.023884 incremental, funded use $0.320506/$2. See live-hitl-030/results.md and latest IMPLEMENTATION_NOTES. No holdout or sharing.

---

## Demo recovery — 2026-09-12T23:53:02.562026+05:30

Use ?demo=verified (also ?demo=recording) for explicitly labelled replay of the real 029 Gemini result with preview, approval and saved reel download; no inference. Generic live run again produced zero clips with different settings. Live recognition reliability is not resolved. See latest IMPLEMENTATION_NOTES.

---

## Approval UI update — 2026-09-12T23:45:39.646237+05:30

Gate 1 now includes per-clip source video previews and Keep controls; Gate 2 includes the final reel player and download. Empty selections and missing source/output block the corresponding approval. 38 focused UI tests pass; no additional inference or holdout access. See latest IMPLEMENTATION_NOTES and demo-integration-029/results.md. Running app reload required for the updated UI.

---

## Historical — checkpoint — Demo 029 ready — 2026-09-12T23:43:06.544495+05:30

Live app now uses opt-in Gemini native video with a prefilled real 40-second East Bay excerpt. Production graph generated and verified a real 11.5-second MP4, score 0.66. Dedicated recipe retains minimum score 0.50. This known-action demo is not a new benchmark result; no holdout, YOLO or transcript used. 405 tests passed, 4 skipped, 1 holdout deselected; additional UI smoke passed and live form verified. Ledger $7.428182; funded usage $0.235887/$2. See evals/iterations/demo-integration-029/results.md and latest IMPLEMENTATION_NOTES for evidence and runtime requirements. App running at http://127.0.0.1:8501/?demo=ready; no automated evaluation scheduled.

---

## Historical — checkpoint — Funded Gemini tests complete 2026-09-12T23:08:05.527570+05:30

Read evals/iterations/gemini-funded-summary/results.md,confirmation.json,and latest IMPLEMENTATION_NOTES. All8developmentwindows14references12types complete via successful024/027/028video calls. DirectGeminiTP5/FP8/FN9,F1.37037 vs MiniCPMTP3/FP31/FN11,F1.125.025transcript8/8valid,TP4/FP5/FN10,F1.34783;moreprecision,lessrecall.026missingimage2/6valid;staged3windowconfirmationcomplete. NoYOLOadded,noholdoutused. Newfundedspend$0.208809of$2cap,remaining$1.791191;reserve$3ofuserreported$5creditfordemo. Historicalledger$7.401104;neverreset.400tests pass,4skip,1holdouttestdeselected. No inference running/scheduled. Keep directGeminibaseline;defertranscript/genericYOLO. Nextrecommended experiment audits longercontext/shotoutcomevisibility with frozen scoring. Olderquota/partialstatuses below superseded.

---

## Funded continuation — 2026-09-12T23:02:35.564073+05:30

User reports$5Google funding; cap newevaluationat$2,reserve$3for demo. Policy:evals/iterations/gemini-funded-budget.json; fixed baseline$7.192294875,cumulativeceiling$9.192294875,noreset. Budget enforced before everyrequest/retry. Twelve focused checks pass.028video6/7and026images2/6next;025transcriptprepared. Older dailyquota/$8notes below are historical; paidgeneration availability still toverify by nextauthorizedcall.

---

## Historical — checkpoint — Gemini quota blocked 2026-09-12T22:51:12.553566+05:30

Read evals/iterations/gemini-development-summary/results.md and report.json, then latest IMPLEMENTATION_NOTES.023confirmationpartial;024/027combined strict-valid video0–5cover8references8types:GeminiTP3/FP4/FN5,P42.86%,R37.5%,F1.40;matched historicalMiniCPMTP1/FP25/FN7,F1.05882. Video6/7missing,so all12categoryevaluationNOTcomplete. Image2/6confirmationmissing. GoogleHTTP429dailyquota20/model/project exhausted; do not retryshortRetryInfo or change keys toreset. Need paidquotaor dailyreset(midnightPacific;Sep13 12:30PMIST). No inference running/scheduled. Ledger$7.192295/$8includesunknownusage reservations.025transcriptscript/planprepared,unrun;026missing-imageplanprepared,unrun. New retryhandler stopsdailyquota. GenericYOLOdeferred based020fragmentedballtracks. Third dataset remains sealed. Earlier statuses below are historical.

---

## Historical — checkpoint — Gemini021/022 2026-09-12T22:36:14.743400+05:30

Read evals/iterations/gemini-pilot-021/results.md and latest IMPLEMENTATION_NOTES.md.021sixcalls complete but strict JSON rejects Markdown fences; separate formatting-only reparse shows videoTP4/FP3/FN6,F1.47059 vs cached same-subset MiniCPMTP3/FP13/FN7,F1.23077. ImagesTP2/FP0/FN8,F1.33333.022JSON output mode first call valid,secondHTTP503high demand; stopped with no paired confirmation score. No inference running or scheduled. Ledger$6.753083/$8 includes unknown-usage reservation. Third dataset sealed. Next: separately logged capacity recovery/JSON confirmation, then broader eight-window/all12type test if improvement holds. No production architecture shift. Earlier statuses below are historical.

---

## Historical — checkpoint — YOLO/ByteTrack transcript pilot020

Updated 2026-09-12T21:51:35.991675+05:30:020tested YOLO11n+ByteTrack+track-augmented transcript+MiniCPM against shared visual transcript+MiniCPM, on3fully paired development windows(10references,9supported types). TP3→3,FP6→4,FN7→7;precision33.33%→42.86%,recall30%unchanged,microF1 31.58%→35.29%. Modest numerical gain,not reliable event recognition. Native tracking1023frames:only8observed ball-track frames,longest0.133s;no ball tracks in free-throw orCampus clips. All3TPs inCampus;none of7experimental predictions cited a track observation. Evidence errors remain. Local126.33s,peak0.4454GiB;9cloud calls20.83s,$0.28511increment,ledger$6.6463of$8.388tests passed,4skipped,1holdout-test deselected. No inference running,third dataset untouched. Read evals/iterations/track-transcript-020/results.md and plans/raw tracks/report, then latest IMPLEMENTATION_NOTES. Sustained ball tracking is the next unresolved prerequisite; no further experiment scheduled.

Earlier next-action statements below are historical.

---

## Historical — continuation —018/019

Current checkpoint 2026-09-12T21:37:57.009084+05:30:018/019 complete with invalid windows. Corrected v2 rules,4fps source sequences and native rim crops tested.018:31calls,no paired valid windows.019:50calls,one paired window,both armsTP0/FP0/FN4. No demonstrated recognition gain. Mixed-view row duplication and continuing visual errors remain. Total incremental estimated$1.29907;ledger$6.36119of$8.388tests passed,4skipped,1holdout-test deselected. No inference running; third dataset untouched. Read evals/iterations/evidence-state-019/results.md first, then018/019plans/reports and latest IMPLEMENTATION_NOTES. Next decision is a separately frozen perception-component comparison, not another silent MiniCPM prompt retry. Original017code/results remain unchanged; new contract is src/hypereel/evaluation/ball_state_v2.py. No production integration or full court geometry.

Older next-action statements below are historical and superseded by this checkpoint and the latest user authorization.

---

## Current checkpoint — state pilot017, grounded derivation, and the localised conclusion

Recorded 2026-09-12T21:12:53.512927+05:30. Ledger $5.06212 of the $8 ceiling, not reset. Third dataset untouched.

Owner asked for a recommended architectural change, implemented and tested. The016 diagnosis was that the model asserts outcomes it has not seen and the scorer cannot distinguish an assertion from an observation. 017 removes the opportunity instead of instructing against it: the model reports per-frame ball state from a closed vocabulary and events are derived deterministically in src/hypereel/evaluation/ball_state.py. Identical frames to016, same model and decoding, same references and matcher; only the output contract changed.

**The score fell to zero, and that is the finding.** Derived TP0/FP1/FN14, microF1 0, against dense016 direct .12698 and sparse013 direct .125. Across48 frames the model reported held24, loose20, in_flight3, through_net ONCE and rim_contact ZERO times. Eight windows containing five shot-outcome references produced not one observed rim contact. Constrained to report only what is visible, this model does not report shot outcomes at all. Every made and missed shot scored in009 through016 was asserted, not observed — previously an audit inference, now a direct measurement.

The one derived event is instructive: window1 reference free_throw_made@225, model reported through_net at229.4 with court_zone beyond_arc, so the derivation typed it three_point_made and scored a false positive. Outcome seen correctly, shot type wrong. With the right zone it would have matched. One case in fourteen.

What the architecture delivered and keeps: zero contradictory label pairs by construction against26 in016; zero scoreboard-derived events, since the scoreboard is not in the vocabulary;13 unit tests over a stage that is verifiable without a model; and lost recall made visible as derivation notes rather than silent gaps.

CONCLUSION. Grounding removes fabrication and removes the score with it, because the perception layer cannot supply the primitive every scored event depends on. Best measured results anywhere in the track are microF1 .25 direct and .50 to .60 on a two-window transcript subset, both shown ungrounded; the honest grounded score is 0, against gates of .70 on precision, recall and F1. Four distinct changes have now hit the same wall: transcripts015, detector crops013/014, denser frames016, grounded derivation017. No prompt, representation or scoring change over six768px frames of720p broadcast footage will reach the gates. What is needed is a change to the evidence — rim-region frames at much higher effective resolution, sampling dense enough around a release to contain the outcome, and a court-zone signal from geometry rather than the same model. Those are data and instrumentation changes; none is started or authorized.

Validation:378 passed,4 skipped,1 final_holdout deselected; git diff --check clean. transcript-pilot-015 artifacts byte-identical throughout. No holdout access, no label change, no report overwritten, nothing committed.

---

Earlier checkpoints below are historical.

## Current checkpoint — dense pilot016 and overall conclusion

Recorded 2026-09-12T20:58:30.835777+05:30. Owner raised the cumulative ceiling from $5 to $8 and asked for the necessary changes and a conclusion. Ledger $4.88544 of $8, not reset. Third dataset untouched throughout.

Pilot016 tested the one hypothesis the015 audit actually pointed at: that sparse evidence, not the output representation, was the binding constraint. Single declared change, frame spacing 2.4s across12s becomes 1.6s across the8s core, same model, prompts, temperature, seed, output cap, references, definitions and matcher, both arms sharing one boundary policy from the outset. Declared confound: at the six-image provider limit density and span cannot be varied independently.

Execution:24 of24 calls completed, no provider error or retry,79.65s,39,878 tokens, $0.54936. Direct valid8/8, narration valid8/8, extraction valid4/8.

**The hypothesis is not supported.** Direct arm across all8 windows and14 references: sparse013 microF1 .125 to dense016 .12698, with precision and macroF1 falling and predictions rising 34 to49. Both arms on windows1 and6: direct .16667 to .25, transcript .60 DOWN to .50. The transcript arm got worse.

The recall gain is measured to be hedging, not recognition. Dense016 direct emitted26 mutually exclusive label pairs across5 windows against sparse013's3 across2. One-to-one same-label matching credits whichever member of a made/miss pair is right and charges the other only a false positive. Window0, which has no annotations, emitted all four exclusive pairs at one timestamp.

Evidence quality moved backwards:0 of20 dense transcript events pass the entailment screen, against2 of8 in015.

Density did fix one real thing: the window1 narration error the015 audit caught. 015 called it a player in black near the three-point line; it is a free-throw setup, and016 narrates it correctly. Perception improves with denser frames. Grounded event extraction does not.

Sample-size warning that applies retrospectively: 015's primary paired figure was .40 on windows[2,6]; the identical retained output scores .60 on windows[1,6]. Window choice moves the headline more than any treatment tested.

CONCLUSION. Iterations009 to016 do not produce reliable event recognition and the failure is now localised. The model asserts outcomes and possession its own evidence does not contain, and the scorer cannot tell an assertion from an observation. Best measured result is microF1 .25 direct and .50 to .60 on a two-window transcript subset against gates of .70 on precision, recall and F1; the grounded score is 0. Three representation changes have now failed (transcripts, detector crops, denser frames), which is consistent with assertion-under-uncertainty being primary rather than evidence sparsity. Closing the gap needs a detector that must ground an outcome in a visible event, a scorer that penalises mutually exclusive predictions for one action, and audited action timings. Those are architectural, not prompt-level, and none is started.

Tests364 passed,4 skipped,1 final_holdout deselected; git diff --check clean. transcript-pilot-015 artifacts verified byte-identical throughout. No holdout access, no label change, no rendering, upload, deployment or architecture change, nothing committed.

---

Earlier checkpoints below are historical.

## Current checkpoint — boundary parity and entailment audit of015

Recorded 2026-09-12T20:33:43.418354+05:30. Offline work only: zero provider calls, ledger unchanged at $4.33608 of $5, third dataset untouched. report.json and observation-audit.json verified byte-identical before and after. No new iteration number was claimed; this audits015.

Both prerequisites named in the previous checkpoint are now discharged. First, identical core/context boundary handling is enforced in shared library code rather than at each call site. The015 defect was in the callers, not the parser: the direct arm validated over the supplied image span and filtered to core, while the extraction arm validated over core and raised, so window1 left paired coverage because it emitted an event at233.0s, itself a supplied frame timestamp the direct arm would have accepted and filtered. The mirror case confirms asymmetry rather than a model difference: window2 direct emitted two_point_made at766.0, equally out of core, and it was retained as context. Added check_window_span, partition_by_core and parse_window_events to basketball_events.py and the symmetric parse_window_extracted_events to transcript.py. Nothing was loosened; the strict all-or-nothing parsers keep their signatures and are now pinned by their own test. scripts/run_transcript_pilot.py is deliberately unmodified and its015 snapshot stays byte-identical.

Second, entailment is now measured as its own axis. Re-parsing retained raw extraction text under the parity policy recovers window1, so the audit covers19 events across all three windows (11 direct,8 transcript), not the6 the original parser accepted. Transcript:1 entailed,7 unsupported. Direct:0 entailed,3 asserted,8 unsupported, of which5 infer a basket from the scoreboard against explicit prompt instruction, twice quoting an unchanged 7-0 score as evidence for further baskets. The transcript arm also extracted two mutually exclusive rebound labels from one identical observation at one timestamp.

Headline: under parity the arms produce5 label/time matches (direct2, transcript3). None is entailed;4 are unsupported and1 merely asserted. Every one of the transcript arm's3 matches rests on evidence that does not establish the event it claims.

Entailment-gated secondary diagnostic, never a replacement for the primary metrics: transcript keeps1 of7 scored events and falls to TP0/FP1/FN10, microF1 0; direct keeps3 of10 at a weaker asserted bar for TP1/FP2/FN9, microF1 0.15385. The gate lowers both arms and was not used to select or remove anything from the primary result. The arms are gated at non-equivalent bars because direct events cite no frozen text, so this is not a clean paired comparison.

Label/time scoring under parity reproduces observation-audit.json exactly (direct TP2/FP8/FN8 microF1 0.20; transcript TP3/FP4/FN7 microF1 0.35294), independently confirming the parity implementation. Primary paired_metrics in report.json are untouched and unrestated.

The one entailed transcript event, window1 two_point_miss at228.2s, is also the clearest evidence that the axes are independent: the015 contact sheet shows that window is a free-throw setup narrated as a shot near the three-point line, so it is a faithful extraction from a false narration. Entailed by the transcript does not mean visually correct. Of18 observation rows,6 are marked visibility=clear while the text hedges. Every unsupported transcript event carries confidence1.0 and every unsupported direct event0.8; reported confidence tracks neither entailment nor correctness.

Validation:363 passed,4 skipped,1 final_holdout test deselected, up from355 by8 new tests; git diff --check clean. The parity guard was verified red on reverting the transcript-side bounds, not merely assumed.

Decision unchanged and better evidenced: do not adopt this MiniCPM narration/extraction combination as a detector. The015 numerical lift remains real as a label/time measurement and remains recorded, but no part of it is evidentially grounded. Any larger frozen comparison should apply the parity policy and record entailment from the outset rather than as a post-hoc audit, and should treat observation accuracy, entailment and label/time matching as three separate measured axes. No inference was started, no architecture changed, no rendering or upload performed.

---

Earlier checkpoints below are historical.

## Current checkpoint — transcript pilot015

Transcript pilot015 completed at 2026-09-12T19:47:12.041385+05:30; final audit recorded 2026-09-12T19:50:21.866669+05:30.

User identifies HoopIQ as the specialist source of the supplied golden labels. No replacement specialist or new user annotation was required. Tested fresh direct detection against observation-only visual narration followed by text-only event extraction, using the same Nebius MiniCPM-V-4_5 for all stages. Three frozen development windows [1,2,6],10 references across9 supported types, all12 event definitions available. Identical6frame JPEG sequences per visual arm,768pixel wide,2.4second gaps across12seconds including2seconds context either side. This isolates representation change on sparse evidence; it is not continuous-video transcription or speech recognition. No references entered model prompts. Third dataset untouched.

Nine of nine provider calls returned completed output in 20.26s; no provider crash, timeout or retry. All3 narrations parsed, all3 direct results parsed,2of3 extraction outputs passed the original strict core-time validation. Window1 emitted an event at233s outside223–231, so that whole transcript result was excluded from primary paired metrics. All raw outputs, input hashes, prompts, observation IDs, per-call timestamps, latencies, usage and memory/pressure checkpoints are preserved. Per-call raw text and parsed window outputs were appended to IMPLEMENTATION_NOTES during execution.

Primary matched coverage: windows2and6,9 references across8 supported types. Direct TP2/FP6/FN7,precision25%,recall22.22%,microF1 23.53%,macroF1 10%. Transcript TP3/FP3/FN6,precision50%,recall33.33%,microF1 40%,macroF1 25%. Unmeasured categories must not be described as passing. Available-only full direct metrics use3windows and cannot be directly compared with2window transcript metrics.

Audit identified asymmetric boundary handling: direct accepted observed context then filtered; extraction required core bounds. Retained original report unchanged. A separately labeled post-hoc offline sensitivity applies direct's context/filter policy to retained extraction outputs acrossall3windows: direct TP2/FP8/FN8,P20%,R20%,F1 20%;transcript TP3/FP4/FN7,P42.86%,R30%,F1 35.29%. No fresh inference or reference changes. Future paired runner must apply identical boundary policy from the outset.

The numerical lift is not established semantic improvement. All6 accepted transcript events cite observations that do not establish their claimed miss or possession outcome. All3 matches are in campus window6. All6 accepted events haveconfidence1.0. All18 narrator rows say visibility=clear despite several descriptions explicitly stating uncertainty. Contact-sheet inspection found clear visual errors: free-throw setup mislabeled as a shot near the three-point line; midcourt ball handling narrated as a shot towards the basket. Full qualitative audit is in observation-audit.json. This audit is agent inspection, not independent human reannotation; original HoopIQ labels/times remain unchanged.

Implementation: added evaluation/transcript.py for timestamp-anchored observations, text-only extraction and valid observation-ID checks; scripts/run_transcript_pilot.py for bounded paired inference and live notes; scripts/audit_transcript_pilot.py for reproducible offline sensitivity. Citation validation establishes ID existence, not factual entailment. No semantic filter was retroactively used to boost scores. Production application architecture unchanged.

Tests:355 passed,4 skipped,1 final_holdout test deselected; no holdout evaluation. Three new tests cover time anchoring/order, paired events, invented citations and empty-transcript evidence. Spend estimateincrement$0.18957,ledger cumulative$4.33608 against$5 ceiling; historical conservative estimates,not invoice prices. No inference remains running.

Decision: retain the transcript and evidence-link format as a diagnostic tool; do not adopt this MiniCPM narration/extraction combination as a reliable detector. Both visual narration and text-to-event reasoning failed. Next refinement should first enforce common boundary handling and evaluate extraction entailment on these frozen transcripts, then test visual narration with genuinely richer temporal evidence or a better visual model under a separately frozen comparison. Treat observation accuracy and event matching separately; do not equate a valid citation or high model confidence with correctness. No new architecture switch or paid run was started after this audit.

---

Earlier checkpoints below are historical.

## Current checkpoint — bounded pilot013/014 completed (2026-09-12)

Bounded pilot 013/014 finished with arm failures; no production architecture adoption.

User authorization to run this pilot superseded the earlier analysis-only pause. Used Nebius MiniCPM-V-4_5 consistently across input arms and local YOLO11n COCO for optional ball crops. The two development games, original eight core windows, 14 reference events, 12 category definitions and five-second one-to-one matcher remained frozen. Third dataset untouched.

013: six wide frames plus context completed 8/8 windows: TP3/FP31/FN11, precision8.82%, recall21.43%, microF1 12.50%, macroF1 4.71%. Twelve-image and crop requests each failed on first request with BadRequestError; exact error body was not retained, so the exact provider limit is unknown. These arms have no valid semantic result.

014: predeclared compatibility change packed the same12 timestamps into six two-row sheets, equal canvas in dense/crop arms. Dense arm returned20events against the maximum12 and stopped at0/8 valid. Crop arm completed3/8 windows then returned20events and stopped: partial TP1/FP21/FN4, precision4.55%, recall20%, microF1 7.41%. Both schema failures had finish_reason=stop, not output truncation. Raw responses preserved; no relaxed validation or automatic retries. No planned identical-input reuse actually occurred. No common completed dense/crop window exists, so there is NO valid paired estimate of YOLO benefit. Differences from013 also confound packing and coverage.

YOLO produced ball candidates in6/96 sampled frames (only two windows; none for campus). This is candidate frequency, not audited ball recall. Detector preparation22.33s, sampled peak process RSS0.410GiB. No observed machine crash. Cloud client RSS is not hosted model memory. Repeated frame-level shot/rebound stories and scoreboard-based explanations remain a grounding/event-identity failure despite explicit instructions; greater visible detail alone did not establish reliable event recognition.

Actual15 cloud attempts across both iterations. Conservative ledger increment$1.20313 includes$0.60 reserved for two rejected requests with unknown usage; cumulative$4.14651 of$5. These are estimates, not invoice charges. No further inference is running or scheduled. New isolated detector environment, preparation/runner scripts, frame manifests/hashes, boxes, memory checkpoints, raw responses, usage and failure audits retained. Production application unchanged.

Validation:352 tests passed,4 skipped,1 final_holdout test deselected. Do not treat failed/unattempted windows as zero-event successes. Existing labels and provisional timing are best-effort evidence, not an audited benchmark; annotation-empty controls are not verified negatives.

Decision: do not adopt the generic YOLO crop pipeline based on this pilot. The next bounded refinement should first validate provider-compatible structured output and require distinct action evidence across timestamps, using retained development clips/raw outputs to address repeated invented events. Keep event definitions and scoring frozen, then predeclare any fresh comparison. Do not increase event limits, discard unmatched predictions, or integrate tracking merely to improve the reported score. No user annotation work is required to interpret this pilot.

---

Historical content below is preserved; earlier analysis-only/cloud prohibition/next-action statements are superseded by the current checkpoint and subsequent user authorization.

Latest user direction: **analysis/proposal only; no detector implementation or new inference.** Deep analysis delivered in user outputs/hypereel-architecture-analysis.md. Read latest notes for evidence, architecture options and predeclared decision checks. Earlier next-action suggestions below do not authorize immediate execution.

Latest status (2026-09-12,after Nebius012): **Matched comparison:MiniCPM detects more but remains unreliable.**

Matched Nebius MiniCPM comparison completed both broad configurations with byte-identical JPEGs and prompt text against frozen local snapshots. Fourframes:TP4/FP32/FN10,P=.1111,R=.2857,microF1=.16,macroF1=.05979. Sixframes:TP5/FP49/FN9,P=.09259,R=.35714,microF1=.14706,macroF1=.09615. Qwen bothTP0/FP0/FN14,F1=0. These are provisional label/time matches,not independently visually confirmed detections; same14labels/12types,not fullgames. MiniCPM is more willing to emit events but has severe overprediction and weak evidence. Raw examples infer repeated scores from unchanged scoreboard and label being positioned for a rebound as completed control. Both violate prompt intent. Sixframes adds one turnover match but21moreFP than fourframes and lower microF1. No steals,assists,blocks,offensive rebounds,free throws,or three-point events matched. Do not call MiniCPM reliable or promote sixframes/YOLO based on this.

Explanation comparison against011 stopped on its first response:HTTP/completion finished successfully,141outputtokens (not truncation),but only1observation for6images. Strict parser correctly rejected it;0of2explanationwindows valid,second unattempted. Do not report zero-error18/18 or score rejected event. Total17paid requests,16schema-valid event outputs,1schema failure,no provider failure,no retries,56.57s batch elapsed. Conservative historical10/30 USD per million ledger estimateincrement$0.41311,total$2.94338 below$5;not confirmed invoice pricing. User explicitly authorized this hosted comparison; no ongoing general cloud fallback introduced. Third dataset untouched. Recordvalidation-audit.json preserves exactcause separate from genericValueError history. No model/label/prompt changes after seeing results. Nextpriority remains visual timing audit and bounding event outcomes to observable evidence; apples-to-apples evidence now available before an architectural choice.

Older statuses below are historical.

Latest status (2026-09-12,after011): **All-event recognition still fails.** 009–011 completed:18/18 provider calls successful,no crash/timeout/schema failure,23.85min total measured batch runtime,peak sampled llama RSS6.400GiB.0094frames and0106frames each TP0/FP0/FN14,macro/microF1=0 across12types.011observations on two-window subset TP0/FP0/FN6,macroF1=0 across6supportedtypes. Zero event-recognition gain; do not adopt6frames as a quality win.011 improved failure visibility only: repeated generic possession descriptions despite distinct images and visible motion in both games. Inference descriptions are not trusted ground truth. Model unloaded after completion. Offline suite345passed,4skipped,1final_holdout test deselected. Holdout untouched.

Implemented additive all-event detector/scorer with paired outputs,raw-output checkpoints,12-category macro and per-type metrics; production highlight path remains single-label. Source exports720p,actualimages768x431/432. References remain provisional clip timestamps and windows label-informed; neither high nor low diagnostic scores establish exact action localization or full-game generalization. Do not silently repair timestamps from uncertain contact sheets. Next concrete experiment proposed after user's YOLO/RF-DETR question: freeze development source intervals,annotate visible-ball/player boxes and audit event timing,benchmark small YOLO+tracking,then compare detector-assisted crops/track evidence+Qwen with Qwen-only on identical intervals. RF-DETR alternative if measured detection failures warrant comparison. No detector installed/benchmarked yet. Run stages serially,cachetracks,measurememory; no assumption of automatic quality gain. Preserve new all-events-history.jsonl alongside legacyhistory. No further prompt-only batch or fullgame/holdout run started.

Earlier status entries below are historical.

Current all-event run (2026-09-12):009 complete,010 running. New multi-event detector/scorer covers all12 categories before highlight selection.009:8 calls,524.24s,TP0/FP0/FN14,macroF1=0,peak sampled llama RSS5.294GiB,no provider failure.010 changes only4→6 frames on same8 diagnostic windows;720p exports resized768x431/432. Timing provisional; no release pass.344 tests passed,4 skipped,final holdout test deselected. See new iterations/all-events-history.jsonl and latest implementation notes.

# Evaluation status

Last updated: 2026-09-12

For the dated, append-only implementation narrative and ordered next steps, see [`IMPLEMENTATION_NOTES.md`](IMPLEMENTATION_NOTES.md).

## Current decision

Latest source checkpoint (2026-09-12T17:18:58.740967+05:30): **Both720p-class owner exports verified and cached; download blocker resolved.** Game1 1280x718/30fps;game2 1280x720/25fps. Four sampled timing checks per game match zero offset. See studio-source-game1.json and studio-source-game2.json. No new inference. Next: all-event multi-output detector/scorer and timing audit, then frozen broad development evaluation. Keep resize/provenance explicit; third dataset sealed. Older statuses below are historical.

Latest source checkpoint (2026-09-12T17:10:04.600810+05:30): **game1 owner export acquired at1280x718/30fps; game2 browser export blocked**. Four sampled game1 alignment checks match zero time offset. New cache downloads/KBETdDRM70Q.studio-720p.mp4; baseline preserved. Game2 Studio Options→Download left open for owner manual click after ERR_BLOCKED_BY_CLIENT. No new inference; all-event detector/scorer remains pending. Third dataset sealed.

Latest owner scope correction (2026-09-12T17:02:18.680880+05:30): **All462 development labels are in scope; historical highlight-only scope is superseded.** Additive all-events-v2 reference ledger/manifest prepared with12 event/outcome categories and4 passing coverage tests. Broad evaluation NOT run; multi-event detector/scorer and timing audit still required. Owner confirmed uploader ownership; visible Google YouTube sign-in awaiting user. No inference running. Read latest notes before continuing; third dataset sealed.

Latest completed matrix (2026-09-12T16:55:40.791209+05:30): **007 and008 completed both development slices; quality still fails**. Retaining640x360 and then increasing3→5 central frames both yieldedTP0/FP0/FN2 per game. All22 provider calls succeeded, no observed crash/timeout; peak sampled model RSS5.613GiB. HD browser playback verified, no usable localHD export yet; uploader ownership clarification pending. Reference timing audit is now a priority alongside HD acquisition. Model unloaded; no inference running. Read newest implementation notes and preserved007/008 reports. Older statuses below are historical.

Current source-quality work (2026-09-12T16:42:38.357437+05:30): HD playback verified for both development games, but no local HD file acquired.007 game1 completed at native360p/3frames:TP0/FP0/FN2,6 successful calls,261.06s,peak sampled model RSS4.685GiB.007 game2 is running with the same configuration.008 planned5 central frames/context8192 at native360p. Source download route pending uploader-account clarification. Older entries below are historical; the holdout remains sealed.

Latest006 completed batch (2026-09-12T16:20:40.181919+05:30): **both local development slices completed despite memory warnings; recognition gate fails**.11/11 requests succeeded (7 vision,4 judge); no crashes/timeouts/provider errors. Total pipeline324.76s, peak sampled llama-server RSS4.69GiB. Both gamesTP0/FP0/FN2; recall0, precision/F1 undefined.007 may test denser core frames as a separately declared experiment; no full-game/holdout run. Warning-only aborts are superseded by the owner. Read006 full reports and latest implementation notes; older statuses below are historical.

Latest006 continuation (2026-09-12T16:17:46.446164+05:30): **game1 completed under memory warnings; game2 running**. Owner explicitly superseded warning-only aborts. Game1 completed six calls in194.70s without provider errors; TP0/FP0/FN2, recall0, precision/F1 undefined. Peak sampled llama-server RSS4.61GiB. This demonstrates a completed bounded run despite warnings; quality gate still fails. Previous002–005 aborts were monitor-policy outcomes, not observed crashes.

Latest refinement (2026-09-12T15:50:14.353575+05:30): **per-call checkpoints implemented;005 stopped during model loading, no observed crash**. Three-frame/context4096/batch128 probe stopped on memory pressure at24.58s; highest sampled llama-server RSS2.99GiB (not total physical peak). Journal preserved one started call and interruption; no returned tokens or completed classification. Sustained viability remains unproven;006/game2 not started. Read latest IMPLEMENTATION_NOTES and005 loading evidence. Existing quality baseline remains001.

Latest session (2026-09-12T14:17:14.239217+05:30): **003 and 004 stopped for memory pressure; no new completed accuracy results**. The unchanged game1 baseline stopped after 35.41s. A separately declared prompt-batch128 experiment stopped after 110.67s and is not a proven remedy. Model unloaded; game2 inference not started. Per-attempt execution JSON records and append-only notes/history preserve both failures. Offline verification: 326 passed, 4 skipped, 1 holdout test deselected. Next live run requires a revised memory plan and should retain per-call results before interruption. Third dataset remains sealed. Earlier status entries below are historical.

Latest continuation (2026-09-12T14:04:22.349901+05:30): **baseline 002 stopped for memory pressure; no new accuracy result**. Game1 vision inference was interrupted at macOS pressure level 2; model unloaded, pressure still elevated. Game2 is cached and preflighted but not evaluated. Attempt and limitations preserved in `iterations/ollama-development-002-game1.aborted.json`. Development recipe paths and generator relocation fixed, labels unchanged. Restore normal memory pressure before fresh serial baseline runs. Holdout remains sealed.

Latest update (2026-09-12 13:42 IST): **local execution works; basketball quality does not yet pass**. Ollama 0.33.3 and `qwen3-vl:4b-instruct` passed text/image smoke tests and completed four real development windows in 321.2 seconds. All four classifications were null: TP=0, FP=0, FN=2; recall=0%, temporal recall@0.30=0%, precision/F1 undefined under the current evaluator. Schema pass=100%, vision-provider error rate=0%. Candidate coverage@0.30=100% did not translate to event recognition. See the [preserved full report](iterations/ollama-development-001.report.json).

The local-only app is available while its process runs at `http://127.0.0.1:8502`; restart instructions are in [local setup](../docs/OLLAMA.md). No full-game rendering or holdout evaluation ran. Local API cost was $0; cumulative estimated cloud spend remains $2.53027.

Two earlier smoke tests with generic `qwen3-vl:4b` failed by output truncation; that tag selects the thinking variant. Their records remain alongside the successful explicit-Instruct smoke test. The evaluation's second text-judge attempt hit the five-call cap and the pre-existing graph fallback returned “accept.” This was not a quality pass; the deterministic metrics above remain the release criterion. A subsequent offline-tested fix makes local text errors propagate into the graph's “judge unavailable” feedback rather than silently returning empty text.

The Nebius account lists `Qwen/Qwen3.5-397B-A17B`, but direct tests returned HTTP 400 for both image and video input. See the [capability test record](iterations/qwen-nebius-capability-20260912.json). Brev/Cosmos remains deferred because credits are unavailable.

The development release gate is **not yet met**, so neither the full first-video run nor the sealed holdout has been executed.

The best tuned development slice was iteration 18:

| Metric | Result | Gate |
|---|---:|---:|
| Candidate recall at IoU 0.30 | 1.000 | 0.800 |
| Selected-event precision | 0.667 | 0.700 |
| Selected-event recall | 1.000 | 0.700 |
| Selection F1 | 0.800 | 0.700 |
| Selected-event recall at IoU 0.30 | 1.000 | 0.700 |
| Schema pass rate | 1.000 | 1.000 |

The clean independent slice from a different game was iteration 20:

| Metric | Result | Gate |
|---|---:|---:|
| Candidate recall at IoU 0.30 | 1.000 | 0.800 |
| Selected-event precision | 1.000 | 0.700 |
| Selected-event recall | 0.500 | 0.700 |
| Selection F1 | 0.667 | 0.700 |
| Selected-event recall at IoU 0.30 | 0.500 | 0.700 |
| Negative-window specificity | 1.000 | monitored |
| Schema pass rate | 1.000 | 1.000 |

The independent slice therefore fails the recall, F1, and temporal-recall gates. Iteration 21 tested an alternative-label verifier, regressed to zero recall, and was rejected; its behavior was reverted while its result remains in the audit trail.

## Cost status

- Cumulative estimated Nebius spend: **$2.53027**
- Hard cap: **$5.00**
- Remaining headroom: **$2.46973**

The cumulative source of truth is [`iterations/spend-ledger.json`](iterations/spend-ledger.json). It is never cleared between iterations.

## What has been accepted

- One-to-one, label-aware temporal matching.
- Candidate and selected-event recall at IoU 0.10, 0.30, and 0.50.
- Precision, recall, micro/macro F1, confusion matrices, balanced accuracy, specificity, average precision, calibration error, and threshold sweeps.
- Proposal-to-classification-to-selection funnel metrics.
- Centered clip shaping for long evidence windows.
- Dense action-frame sampling with explicit before/after context.
- Contrastive verification against rebounds, misses, and unforced turnovers.
- A recipe-level two-second separation between selected highlight fragments.
- Append-only iteration results with change notes, dataset hashes, code revision, provider usage, and cumulative spend.

## Current limitation

The evaluated Nebius vision model is `openbmb/MiniCPM-V-4_5`; this is not a claim that it is the account's only listed model. It has changed semantic verdicts across temperature-zero runs and has confused or rejected steals, rebounds, and made baskets. The present single-label clip schema also cannot represent two different events occurring inside one candidate window.

More prompt tuning against known timestamps risks overfitting. The immediate experiment is local Qwen3-VL Instruct using ordered frames. Native-video and multi-label temporal detection remain separate future work, not implemented capabilities of this adapter.

## Audit trail

- Human-readable cumulative table and decisions: [`iterations/iteration-log.md`](iterations/iteration-log.md)
- Append-only complete run records: [`iterations/history.jsonl`](iterations/history.jsonl)
- Cumulative provider cost: [`iterations/spend-ledger.json`](iterations/spend-ledger.json)
- Metric definitions and release gates: [`iterations/README.md`](iterations/README.md)
- Development golden datasets: [`golden/cases/development.pipeline.jsonl`](golden/cases/development.pipeline.jsonl)
- Sealed holdout dataset: [`holdout/`](holdout/)

## Next action

Executable continuation plan for another agent: [`AGENT_HANDOFF.md`](AGENT_HANDOFF.md).
It covers the 21 historical iterations, local baseline, both development datasets,
preflight checks, controlled experiments, metrics, and stop conditions.

Inspect whether ordered frames capture the full action, then compare a predeclared temporal-sampling configuration on fixed development slices with a sufficient (still bounded) text-judge call allowance. Do not tune to exact reference timestamps or treat the small null-output run as proof that all Qwen configurations fail. Record latency as well as accuracy: observed vision calls took 59–95 seconds each. Multi-label temporal detection remains unimplemented. Do not run full games until development gates pass. Keep the original $5 cloud ceiling with no cloud fallback; the holdout remains sealed.
