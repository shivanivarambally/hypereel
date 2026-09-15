# Fixed verifier on the full development set — 045

Completed 15 September 2026. Applies the 044 verifier fix (re-keyed shot-family
criteria plus de-anchored `observed` field) to all seven development windows at
8 fps, single-pass control reused frozen from 038.

## Headline

Two-phase now beats the one-phase baseline on the six reviewed positive labels
in W1–W5, reversing the standing conclusion from 041.

| Stage | 041 (old verifier) | 045 (fixed) |
|---|---:|---:|
| single_pass control | 2/0/4 — F1 **0.500** | 2/0/4 — F1 **0.500** |
| discovery | 3/2/3 — F1 0.545 | **4/1/2 — F1 0.727** |
| confirmed | 2/2/4 — F1 0.400 | **4/1/2 — F1 0.727** |
| confirmed_plus_potential | 3/2/3 — F1 0.545 | **4/1/2 — F1 0.727** |
| selected | 2/2/4 — F1 0.400 | **4/1/2 — F1 0.727** |

Precision 0.50 → 0.80, recall 0.33 → 0.67 on the confirmed stage. All four
stages now agree, meaning nothing is lost between discovery, verification and
selection.

Per-window confirmed output:

| Window | Predicted | Reference | Result |
|---|---|---|---|
| W1 | `three_point_miss`, `defensive_rebound` | `free_throw_made` | FP + FN (label disputed) |
| W2 | `turnover`, `steal`, `two_point_made` | `steal`, `two_point_made` | both correct |
| W3 | — | — | correct negative |
| W4 | **`free_throw_miss`** | `free_throw_miss` | **correct** |
| W5 | `two_point_miss`, `defensive_rebound` | `missed_field_goal`, `block` | shot matched; `block` missed |

## The confound, and it is serious

**This run cannot cleanly attribute the gain to the verifier fix.** Discovery
itself changed, and discovery was not modified in 044.

W4's label across every run ever made:

| Run | Label | Confidence | Decision |
|---|---|---:|---|
| 040 @4 fps | `free_throw_made` | 0.95 | confirmed |
| 041 @4 fps | `free_throw_made` | 0.95 | confirmed |
| 043 @8 fps | `free_throw_made` | 0.90 | confirmed |
| 044 @8 fps, fixed verifier | `free_throw_made` | 0.49 | potential_event |
| **045 @8 fps, fixed verifier** | **`free_throw_miss`** | 0.85 | confirmed |

Four runs said made. 044 said made but the fixed verifier declined it. 045's
*discovery* said miss on its own. Human adjudication established that miss is
correct, so 045 is right — but it is right for a reason the verifier fix does
not explain.

The same instability appears elsewhere:

- **W1 shot type:** `two_point_miss` in 040, 041 and 043; `three_point_miss` in
  045. Same clip, same prompt, same frame rate.
- **W5 second event:** `offensive_rebound` in 043; `defensive_rebound` in 045.
  These are opposite team attributions of the same rebound.
- **W5 routing:** `potential_event` at 0.49 in 040/041; `confirmed` at 0.85–0.90
  in 043/045.

With six positive labels, one event is 16.7% of recall. The observed run-to-run
variance is at least one event on at least three of the five scored windows.
**A single run's F1 on this set is not a reliable estimate, and 0.545 → 0.727
conflates a real fix with sampling noise of comparable size.**

What the fix *did* demonstrably do is visible in 044, not here: the verifier
independently rejected a proposal its own discovery pass had made, with reasoning
that differed from the discovery text. In 045 the verifier echoed discovery on
all 11 classifications, because discovery happened to be right more often and
nothing needed catching. Independence appears only when there is a disagreement
to have.

## Verifier behaviour

- Independent verification reasons: **0 of 11**
- Echoed: **11 of 11**
- Decisions: 11 confirmed, 0 potential_event, 0 rejected

Compared with 32/33 echoes before the fix, this is not evidence the echo problem
is solved. It is evidence that on this particular run there were no
disagreements to surface. The 044 result remains the only direct demonstration
that the verifier can now reject.

## Budget

- Ledger before: $9.904063875
- Live video calls: **13**, zero provider errors
- Incremental estimated spend: **$0.2735783**
- Ledger after: **$10.177642175**
- Ceiling $11.192294875; remaining headroom **$1.014653**

Session total across 043, 044 and 045: **$0.4837898**.

## What is now known, and what is not

Known:

- The verifier was rubber-stamping (32/33 echoes) and its contrastive criteria
  were keyed to a retired taxonomy so that 13 of 14 labels received only a
  generic instruction. Both are fixed and tested.
- The fixed verifier can reject a false proposal with independent reasoning
  (044, W4).
- W4's reference label `free_throw_miss` is correct, by human adjudication.
- All four pipeline stages now report identical counts, so no events are lost
  downstream of discovery.

Not known:

- Whether 0.727 is reproducible. It has been measured once.
- How much of the gain is the verifier fix and how much is variance.
- Whether W1's reference is correct. Five runs now disagree with it, and the
  fifth disagrees in a new way (`three_point_miss`), which weakens the
  "consistent model error" reading and strengthens the "ambiguous footage"
  reading.
- Proposer recall, which remains unmeasured on fixed windows.

## Next

1. **Repeat 045 three times with no changes.** Roughly $0.82 at current rates,
   which exceeds remaining headroom, so run two repeats (~$0.55) or restrict to
   W1/W4/W5 (~$0.35). Without a variance estimate no further comparison on this
   set is interpretable, and this is now the binding constraint rather than any
   model change.
2. **Re-adjudicate W1.** Free. Clip extracted at
   `evals/adjudication/disputed-w1-w4/w1_disputed_5.5-10.0.mp4` (file starts at
   source 5.5 s, so the disputed events at 7.375 s and 8.25 s sit at roughly
   1.9 s and 2.75 s into that file).
3. **Grow the reference set** past six labels before any further tuning.

## Limitations

Six positive labels across two development games, single run, fixed reviewed
windows. W6 and W7 ran but are outside the scored subset and remain qualitative.
Single-pass control reused from 038 rather than re-run at 8 fps, so the baseline
comparison holds frame rate constant only for the two-phase arm. 443 passed,
4 skipped. Holdout untouched; golden labels unmodified. No commit or push.
