# State pilot017 — grounded derivation: the model reports ball state, code derives events

Architectural change, not a prompt change. Pilots 009–016 asked "what events happened" and the
model answered by asserting outcomes it had not seen. 017 removes the opportunity: the model
reports per-frame ball state from a closed vocabulary and `src/hypereel/evaluation/ball_state.py`
derives events deterministically from state transitions.

Identical dense frames to 016 (same JPEG bytes), same model, temperature 0, seed 0, 1536 output
cap, same 14 references, definitions and five-second one-to-one matcher. 8 calls, $0.17668.

## Result: the score goes to zero, and that is the finding

| | TP | FP | FN | Precision | Recall | micro F1 |
|---|---:|---:|---:|---:|---:|---:|
| sparse 013 direct | 3 | 31 | 11 | .08824 | .21429 | .12500 |
| dense 016 direct | 4 | 45 | 10 | .08163 | .28571 | .12698 |
| **derived 017** | **0** | **1** | **14** | **.00000** | **.00000** | **.00000** |

The derivation emitted **one event across eight windows**. Not because the logic is broken — its
13 unit tests pass and it is the only stage in this project whose behaviour is verifiable without
a model — but because the state reports contain almost nothing to derive from.

## What the model actually reported, across 48 frames

| ball_state | count |
|---|---:|
| held | 24 |
| loose | 20 |
| in_flight | 3 |
| through_net | **1** |
| rim_contact | **0** |
| deflected | 0 |
| not_visible | 0 |

Team was identifiable in 15 of 48 frames. Court zone was `unknown` in 13.

**Zero rim contacts across eight windows containing five shot-outcome references.** Constrained to
report only what is visible, the model does not report shot outcomes at all. Every made and missed
shot that iterations 009–016 scored was asserted, not observed. That is now measured rather than
inferred from an audit.

## The single derived event

Window 1, reference `free_throw_made@225`. The model reported `held(blue, inside_arc)` ×3, then
`in_flight(blue, beyond_arc)`, then **`through_net(blue, beyond_arc)`** at 229.4.

It saw the outcome correctly — the shot was made — and misclassified the court zone, so the
derivation typed it `three_point_made` and scored a false positive. Had the zone been
`free_throw_line`, the derived `free_throw_made@229.4` would have matched the reference at 225
within the five-second tolerance and scored a true positive.

So made/miss detection worked in the one case where the ball was visible through the net, and
shot-type classification was the failure. One case out of fourteen references.

## What the architecture did deliver

- **Zero contradictory label pairs**, structurally, against 26 in 016's direct arm. A single
  flight can yield at most one outcome; the type is no longer available to hedge across.
- **Zero scoreboard-derived events.** The scoreboard is not in the vocabulary, so the pathology
  that produced three "baskets" from one unchanged score in 016 cannot occur.
- **A testable stage.** The derivation has 13 unit tests covering made/miss, rebound team
  attribution, turnover-versus-rebound, block, out-of-window events and the exclusivity property.
- **Visible recall loss.** Every non-emission is recorded as a derivation note rather than a
  silent gap.

## Operational

8 of 8 calls returned completed output, no provider error or retry, 17.71s, $0.17668, ledger
$5.06212 of $8. Four of eight windows failed strict parsing because the model returned a
timestamp-keyed object rather than `{"frames": [...]}`; the per-frame content was valid.
`parse_states` was extended post-hoc to accept that serialisation and events were re-derived from
retained raw text in `reparse.json` — no re-run, no semantic validation relaxed. The original
strict outcome (0 events, recall 0) stands unchanged in `report.json`.

One rule was removed as unsound during implementation: `assist` was being derived from consecutive
`held` frames by one team, which is continued possession rather than an observed pass.
Distinguishing them needs player identity, which this vocabulary does not carry, so the rule was
deleted rather than kept as a guess.

## Conclusion

Grounding removes fabrication and it removes the score with it, because the underlying perception
cannot supply the primitive every scored event depends on: a visible shot outcome. No prompt,
representation or scoring change operating on six 768px frames of 720p broadcast footage will
reach the .70 gates. The gap is not tuning.
