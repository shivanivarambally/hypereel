# Rules gate, phase-transition observability, and W1 occlusion refuted — 050

Completed 15 September 2026. Adds the deterministic rules gate and the phase-1 →
phase-2 observability requested by the project owner, and records a human
observation that refutes the standing W1 hypothesis.

## W1: the occlusion theory is wrong

The owner supplied a screenshot at ~2 s into `w1_disputed_5.5-10.0.mp4`. **The
rim and net are clearly visible and unoccluded**, with the ball at the net.

That refutes the hypothesis carried since 043, which held that the made/missed
errors came from the camera not showing the rim. It does not. The model has a
clean view of a visible outcome and reports the opposite.

This is a worse finding than occlusion but a more accurate one. Occlusion would
have been a data limitation with an honest remedy — route to review, which the
044 verifier already does when it recognises it. Misreading a clearly visible
ball-through-net is a perception failure in the model, and no prompt, rule or
frame-rate change addresses it. W4's verifier reporting occlusion for the
adjacent window remains true for that window and should not be generalised.

## What was built

**Rules gate** (`apply_rules_gate` in `src/hypereel/analyze/phase_transitions.py`,
called per window from `classify_moments`). Runs `validate_sequence` on each
window's resolved events. An `illegal` violation forces the involved events to
`potential_event` at confidence ≤0.49 with the rule text as the reason and the
expert flag raised; a `review` violation raises the expert flag only. **It never
deletes an event** — when a pair is illegal, either the shot label or the
follow-up is wrong and code cannot tell which, so both are surfaced rather than
one silently dropped.

Applied per window, because legality is a property of a sequence: a rebound is
judged against the shot preceding it in the same possession, not against events
in an unrelated window.

**Phase-transition observability.** Every phase-1 proposal now produces a
`Transition` record carrying both labels, the phase-2 verdict, the verifier's
stated reason, the expert flag and any rule violation that fired. Outcomes are
bucketed as `confirmed_unchanged`, `corrected_relabel`, `routed_to_review`,
`rejected` or `rules_blocked`. `transition_metrics()` aggregates a run into
survival rate, relabel pairs, which phase-1 labels fail to survive, and which
rules fired. The runner writes per-event records and the aggregate into
`report.json` under each arm.

This answers what was previously unanswerable: when phase 1 proposes N events and
phase 2 keeps fewer, **why**.

**Taxonomy bug found and fixed.** `validate_sequence` initially knew only the
fourteen-label set, so the older four-label recipes (`made_basket`,
`three_pointer`, still used by `basketball_team_evaluation` and friends) were not
recognised as shots and R5 fired spuriously on a legitimate block. This is the
same class of bug as the verification-prompt failure found in 044, where criteria
keyed to a retired taxonomy made the second pass a no-op for 13 of 14 labels.
Both taxonomies are now covered, with a regression test.

Suite: **458 passed, 4 skipped** (443 before this work, plus 15 rules tests).

## Result

Confirmed stage, W1–W5, six reviewed positive labels: **3/2/3, precision 0.60,
recall 0.50, F1 0.545.**

That is the low end of the measured distribution, not a regression. Across five
post-verifier-fix runs:

| Run | TP/FP/FN | F1 |
|---|---:|---:|
| 045 | 4/1/2 | 0.727 |
| 046 | 4/1/2 | 0.727 |
| 047 | 4/1/2 | 0.727 |
| 048 | 3/2/3 | 0.545 |
| **050** | **3/2/3** | **0.545** |

n=5, mean **0.655**, sd **0.100**, range 0.545–0.727. The 0.182 spread measured
in 046–048 holds. Single-pass control 0.500; consensus over 045–048 gives 0.727
deterministically.

**The rules gate fired zero times.** No window produced an illegal combination,
so it was a no-op safety net on this run. It has not been shown to improve
anything; it has been shown not to harm anything. Its value stays hypothetical
until a run produces an illegal sequence.

## What the transition log immediately surfaced

Eight proposals: 6 `confirmed_unchanged`, 2 `routed_to_review`, 0 relabels,
0 rules fired.

| Window | Label | Outcome | Verifier reason |
|---|---|---|---|
| W2 | `assist` | routed_to_review | *"UNCERTAIN: invalid verification event; East Bay Elite player #0 throws a full-court forward pass directly to teammate #23 who makes the layup."* |
| W5 | `defensive_rebound` | routed_to_review | referee whistle / foul ambiguity while white gathers the ball |

The W2 entry matters. The verifier's prose **describes a textbook assist** — a
pass leading directly to a made layup — and the event was still routed to review
as an *invalid verification event*. That prefix comes from
`parse_verification`'s exception path, so this is a **schema or parse failure,
not a judgement**: the verifier agreed and its answer was discarded on a
technicality.

Without the transition log this would have been invisible, appearing only as a
missing assist. That is one concrete defect found by observability on its first
run, and it is a silent recall loss that the log says has been happening.

## Budget

- Incremental: **$0.1908487** (9 calls)
- Ledger: **$10.983116625**; remaining headroom **$0.209178**
- Session total 043–050: **$1.3892644**

Headroom is now under one full-set run. No further paid runs without explicit
authorisation.

## Next

1. **Diagnose the W2 assist parse failure.** Free — the raw verifier response is
   in `provider-calls`. A verifier that agrees but fails validation is a silent
   recall loss.
2. **Do not pursue W1 further by prompt or rules.** The outcome error is
   perception on a clearly visible event. The options are a different model, or
   accepting that shot outcome needs human confirmation on this footage.
3. **Grow the reference set.** Six labels, sd 0.100, spread 0.182. Every
   remaining question is gated on this, and it costs annotation time, not spend.
4. The rules gate needs a run containing an illegal sequence before its value can
   be assessed.

## Limitations

One run. The gate fired zero times so is untested against real violations. Rules
are NBA; the footage is amateur/club and likely NFHS or FIBA — R3 is marked
NBA-specific, R1/R2/R4/R5 are consistent across codes. Fixed reviewed windows, so
proposer recall remains unmeasured. Holdout untouched; golden labels unmodified;
no commit or push.
