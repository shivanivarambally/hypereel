# W2 assist parse failure diagnosed, and per-event-type comparison — 051

Completed 15 September 2026. **No inference, no spend.** Ledger unchanged at
$10.983116625; headroom $0.209178.

Diagnoses the silent recall loss that the 050 phase-transition log surfaced, and
answers a question that had been asked twice and answered only in aggregate:
does the two-phase approach perform better for different *types* of event?

## The W2 assist failure — a spec gap, not a model failure

Both phases agreed the event was an assist, by the same two players. They
disagreed about **which instant an assist is anchored to**.

| Phase | Anchor | Time | Stated reason |
|---|---|---:|---|
| 1 (discovery) | the resulting basket | **12.1 s** | *"Player #0 in blue passes ahead around 08.7 to teammate #23 who makes a layup"* |
| 2 (verification) | the pass | **8.7 s** | *"player #0 throws a full-court forward pass directly to teammate #23 who makes the layup"* |

Gap 3.4 s. `parse_verification` rejects any shift beyond 2 s as
`ValueError('Verifier substituted a different action time')`, so the event was
downgraded to `potential_event` with the prefix `UNCERTAIN: invalid verification
event`. The raw verification JSON was well-formed and marked `confirmed`; it was
discarded on a timestamp convention.

Phase 1 also contradicted itself: its reason describes the pass at 08.7 while its
`time_seconds` field says 12.1. That is the tell — it had no anchor rule to
follow and picked inconsistently.

**Root cause.** The discovery prompt specifies anchors for three event families
and omits a fourth:

> *"For shots anchor outcome; for possession changes anchor control; for blocks
> anchor contact."*

Nothing for assists, which are the one event in the taxonomy spanning two
separated moments. The 2-second guard is doing its job — it exists to stop the
verifier drifting onto an unrelated action — and it fired on a disagreement the
spec never resolved.

**Fix.** Both prompts now state the same anchor: *"for an ASSIST anchor the
moment of the PASS, not the resulting basket"*, with phase 2 told explicitly to
use phase 1's anchors. One line each, plus a regression test asserting both
prompts carry it. **459 passed, 4 skipped.**

**Not yet verified live.** Remaining headroom ($0.209178) is under one full-set
run, so this fix is untested against the model. It is a prompt-consistency change
with a test, not a measured improvement.

**Scope of the loss.** `assist` is not in the reference set for W2
(`steal`, `two_point_made`), so this cost no F1 in 050. It would on any reference
set containing assists, and the failure mode generalises to every event that
spans two moments. The transition log is the only reason it was visible at all —
without it the symptom was a missing assist with no explanation.

## Per-event-type comparison

Summed over the five post-verifier-fix runs (045, 046, 047, 048, 050), confirmed
stage. The single-pass control is the frozen 038 result reused each time, so its
counts are one answer repeated five times with zero variance by construction; the
comparison is fair on accuracy, not on stability.

| Event type | Single-pass TP/FP/FN | Two-phase TP/FP/FN | Verdict |
|---|---|---|---|
| `steal` | 0/0/5 | **5/0/0** | two-phase wins outright |
| `missed_field_goal` | 0/0/5 | **5/0/0** | two-phase wins outright |
| `two_point_made` | 5/0/0 | 5/0/0 | tie |
| `free_throw_miss` | **5/0/0** | 3/0/2 | **two-phase loses** |
| `block` | 0/0/5 | 0/0/5 | neither ever detects it |
| `free_throw_made` (W1) | 0/0/5 | 0/2/5 | neither; two-phase adds FPs |
| `two_point_miss` | 0/0/0 | 0/3/0 | two-phase FPs only (W1) |
| `three_point_miss` | 0/0/0 | 0/2/0 | two-phase FPs only (W1) |

### Reading

**Two-phase wins exactly where a window contains more than one scorable event.**
W2 holds a steal and a basket; W5 holds a block and a missed shot. Single-pass
emits one label per window, so the second event was not being missed, it was
structurally unreachable. Both classes move 0% → 100%. This is the entire source
of the aggregate gain, and it is a capability difference rather than an accuracy
difference.

**Two-phase loses on single-event precision.** `free_throw_miss` falls from 5/5
to 3/5. That is W4's run-to-run instability: the frozen control is one fixed
answer, while two-phase re-samples and inverts the outcome in two runs of five.

**Neither approach solves two classes.** `block` has never been detected by any
arm, at any frame rate, in any run — the only pure recall failure left.
`free_throw_made` is W1, the systematic misread confirmed by human review against
an unoccluded rim. Two-phase additionally contributes every false positive in the
table, and all of them are W1's wrong shot labels.

### Consequence for the headline number

Aggregate confirmed F1 moved 0.500 → mean 0.655 across the post-fix runs. That
decomposes as **+2 classes recovered, −1 class degraded, 3 classes unchanged**.
Quoting the aggregate alone overstates how general the improvement is: it is a
multi-event capability win, offset by a single-event stability loss.

Practical implication: two-phase should be preferred for windows expected to hold
multiple events, and the single-pass path remains competitive for windows with
one. Consensus over repeats (0.727 deterministic) is the remedy for the
stability loss, at 4× inference.

## Budget

No spend. Ledger **$10.983116625**; headroom **$0.209178**. Session total
043–050 remains $1.3892644.

## Next

1. Verify the assist anchor live when budget allows (~$0.19 for the full set).
2. `block` is the only untouched recall failure and needs its own experiment.
   With one reference instance it is currently unmeasurable — this is another
   argument for growing the reference set first.
3. Reference set remains the binding constraint: six labels, sd 0.100.

## Limitations

The per-class table has one reference instance per class per run, so a class
verdict rests on a single window. `two_point_miss` and `three_point_miss` appear
as false positives only because they are W1's wrong answers, not because those
classes were tested. The assist fix is untested against the model. Holdout
untouched; golden labels unmodified; no commit or push.
