# Basketball rules encoded and tested on W1 — 049

Completed 15 September 2026, following W1 adjudication. The project owner
confirmed the free throw **was made** and that number 24 of the Black team
collected the ball, and supplied the governing rebound rules. Those rules were
verified against official NBA sources, written down, encoded as deterministic
validation, added to both model prompts, and tested on W1.

## Rules verification

Requested explicitly: confirm from NBA rules before encoding. Result is in
`docs/BASKETBALL_RULES.md`, with each rule carrying a citation and a status of
Verified, Inferred or Convention.

| Rule | Status | Source |
|---|---|---|
| Rebound requires a **missed** shot | Verified | NBA.com Stat Glossary: *"A rebound occurs when a player recovers the ball after a missed shot."* |
| Made free throw → opponent throw-in, no rebound | Verified | NBA Rule 9: *"After a successful free throw which is not followed by another free throw, the ball shall be put into play by a throw-in, as after any successful field goal."* |
| Non-final free throw → dead ball | Verified | NBA Rule 6 lists dead ball on a *"free throw which will not remain in play"* |
| Missed final free throw → live ball | **Inferred** | Follows from Rule 6's converse plus Rule 9's *"a free throw that is unsuccessful and the ball continues in play"* |
| Offensive/defensive by team | Verified | NBA.com Stat Glossary |
| Assist requires a made basket | Verified | NBA.com Stat Glossary |
| Block requires a shot attempt, defender tips the ball | Verified | NBA.com Stat Glossary |
| Held ball → jump ball | Verified, **NBA-only** | NBA Rule 4 and Rule 6 |

**One correction to the earlier draft.** It stated that an uncontrolled recovery
results in "a jump ball or alternating-possession throw-in". That conflated
codes. The NBA uses an actual jump ball and has no possession arrow; alternating
possession is NFHS and FIBA. The owner's original statement ("it's a jump ball")
was correct for the NBA and the draft's addition was wrong.

**League caveat recorded.** The development footage is amateur or club play
(East Bay Elite, Spartans, Campus, Unlimited), which would run under NFHS or
FIBA rules, not NBA. R1, R2, R4 and R5 are consistent across codes so this does
not matter for them. R3 is the exception and is marked NBA-specific.

## On the RAG question

Asked whether a retrieval pipeline over basketball rules would help. **No, and
it was not built.** The governing rule set for these twelve labels is one page
and closed, so there is no corpus to search; retrieval solves a
too-much-knowledge problem that does not exist here. It would add a real failure
mode — a retriever missing the free-throw rule on a free-throw window — plus
per-window latency and cost, for no gain over a constant string. The model was
never ignorant of what a rebound is; it produced an illegal combination from
visual ambiguity, and that is fixed by a constraint, not by more text to consult.

RAG would earn its place across multiple rulebooks (FIBA / NBA / NCAA / NFHS),
and even then as a keyed lookup by recipe rather than semantic retrieval.

## What was built

- `docs/BASKETBALL_RULES.md` — cited rules reference, R1 through R6.
- `src/hypereel/evaluation/basketball_rules.py` — `validate_sequence()` returns
  typed violations with severity `illegal` or `review`; `rules_prompt_text()`
  returns the constraints as a prompt constant. Violations are reported, never
  silently repaired: when a pair is illegal, either the shot label or the
  follow-up label is wrong and code cannot tell which.
- `tests/test_basketball_rules.py` — 14 tests including the exact W1 case.
- Rules text wired into both `discovery_prompt` and `verification_prompt`.

Suite: **457 passed, 4 skipped** (443 before, plus the 14 new).

## Result on W1 — half the error is fixed

| | Before (8 runs) | 049 (rules in prompt) |
|---|---|---|
| Shot type | field goal (`two_point_miss` ×7, `three_point_miss` ×1) | **`free_throw_miss`** |
| Outcome | missed | missed |
| Follow-up | `defensive_rebound` | `defensive_rebound` |
| Truth | **made free throw**, ball collected by Black #24 | |

**Shot type is now correct.** Phase 1 still proposed `three_point_miss`; the
verifier **corrected** it to `free_throw_miss`, citing the setup directly:
*"Blue #3 shoots a free throw from the foul line with players lined up along the
key."* The rules text gave the model the free-throw frame it had missed in all
eight prior runs, and the verifier's relabel path — added in 044 — did the work.

**Outcome is still wrong.** It reports *"the shot hits the rim and visibly
misses"* at 0.95 confidence. The free throw was made.

## Why validation does not catch what remains

The model has moved from an incoherent story to a **self-consistent but wrong**
one. Running the validator on both readings:

| Sequence | Verdict |
|---|---|
| 049 output: `free_throw_miss` → `defensive_rebound` | R1 **review** — legal if that was the final attempt |
| Truth: `free_throw_made` → a catch labelled `defensive_rebound` | R1 **illegal** — ball is dead, that is an inbound |

Validation fires on the truth-shaped error and not on the current output. That
is correct behaviour and it is also the limit of this approach: rules can reject
impossible combinations, but they cannot detect a plausible sequence built on a
misread outcome. The remaining W1 error is perception, not rules.

This sharpens the earlier hypothesis rather than confirming it. The theory was
that the model saw the catch, inferred a rebound, and back-inferred a miss. If
that were the whole story, naming the free throw should have removed the
pressure to see a miss. It did not. The model asserts positive rim contact, so it
is more likely reading the rim interaction directly and wrongly — consistent with
W4's verifier reporting for the adjacent window that *"the basketball hoop and
net outcome are completely occluded/off-camera behind court elements."*

## Budget

- Incremental: **$0.0436155** (1 window, 2 calls)
- Ledger: **$10.792267875**; remaining headroom **$0.400027**
- Session total 043–049: **$1.1984157**

## Next

1. **Confirm the occlusion theory on W1** by having a human check whether the
   rim and net are visible at the moment of the shot in
   `evals/adjudication/disputed-w1-w4/w1_disputed_5.5-10.0.mp4` (~2.0 s in).
   Free. If the rim is occluded, no prompt or rules change will fix W1 and the
   correct behaviour is to route it to review rather than assert an outcome,
   which the 044 verifier already does when it recognises occlusion.
2. **Re-run the full set with rules enabled** to check that the free-throw
   recognition generalises and costs nothing elsewhere. ~$0.19, affordable once.
3. Wire `validate_sequence` into the graph as a post-verification gate that
   routes `illegal` pairs to human review. Not yet done; currently the module is
   tested but not called in the pipeline.
4. Grow the reference set past six labels, still the binding constraint.

## Limitations

One window, one run. Shot-type recovery is a single observation and could be
sampling variance, given the measured run-to-run spread of 0.182 F1 on this set.
The validator is not yet called by the pipeline. Rules are NBA; the footage
likely is not. Holdout untouched; golden labels unmodified; no commit or push.
