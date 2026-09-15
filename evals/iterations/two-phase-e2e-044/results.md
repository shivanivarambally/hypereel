# Verifier de-anchoring and shot-family criteria — 044

Completed 15 September 2026. Follows the W4 human adjudication, which confirmed
the reference label `free_throw_miss` is **correct** and the model's repeated
`free_throw_made` was **wrong**. That ruled out the label-error explanation and
made the verifier the prime suspect.

## Diagnosis

Two compounding bugs, found by checking whether the verifier's stated reason
ever differed from the discovery reason it was asked to check.

**1. The verifier was rubber-stamping.** Across 040, 041 and 043 the
`verification_reason` was byte-identical to the discovery `reason` in **32 of 33
classifications**. The single exception was W5 at 0.49 confidence, the one case
where discovery was already uncertain. A second pass that restates the first
pass is not verification; it converts an error into a *confirmed* error while
costing an extra inference call.

**2. The contrastive criteria were keyed to a retired taxonomy.**
`build_verification_prompt` selected reject-criteria from a dict keyed
`steal`, `made_basket`, `three_pointer`. The recipe in use emits fourteen labels
(`two_point_made`, `free_throw_made`, `made_field_goal`, …). **Only `steal` ever
matched.** Thirteen of fourteen labels fell through to the generic fallback,
"reject unless the ordered frames directly establish the proposed event."

The criterion W4 needed already existed, under `made_basket`: *"Accept only with
visible ball-through-rim/net evidence."* It never fired, because the label was
`free_throw_made`. Every shot label — the entire family where all observed
errors live — got the weakest instruction available.

## Changes

`src/hypereel/providers/_util.py`:

- Re-keyed the contrastive criteria to the taxonomy actually in use. Every
  made/missed label now carries an explicit outcome test (ball visibly down
  through the net for a make; rim/backboard carom, airball or contested rebound
  for a miss; hidden outcome is UNCERTAIN, not a make), plus its shot-type test.
  Added criteria for `turnover`, `block`, `offensive_rebound` and
  `defensive_rebound`.
- De-anchored the prompt. The verifier must now write an `observed` field first,
  describing the decisive moment in its own words without reference to the
  proposed label, and explicitly stating whether the ball passes down through
  the net, caroms out, or is hidden. The verdict is judged against that
  observation.

Regression suite: **443 passed, 4 skipped.**

## Result

Re-ran W4 (the confirmed failure) and W2 (control, already correct) at 8 fps
against the frozen 038 single-pass baseline. Scope is three reviewed positive
labels: `steal`, `two_point_made` (W2), `free_throw_miss` (W4).

| Stage | Verifier | TP/FP/FN | Precision | Recall | F1 |
|---|---|---:|---:|---:|---:|
| discovery | old (041) | 2/1/1 | 0.67 | 0.67 | 0.667 |
| discovery | fixed (044) | 2/1/1 | 0.67 | 0.67 | 0.667 |
| **confirmed** | old (041) | 2/1/1 | 0.67 | 0.67 | 0.667 |
| **confirmed** | **fixed (044)** | **2/0/1** | **1.00** | 0.67 | **0.800** |
| confirmed_plus_potential | old (041) | 2/1/1 | 0.67 | 0.67 | 0.667 |
| confirmed_plus_potential | fixed (044) | 2/1/1 | 0.67 | 0.67 | 0.667 |

Discovery is unchanged, as expected — the fix targets the second pass only.
**Confirmed precision rises from 0.67 to 1.00** because the verifier now rejects
the false positive it previously confirmed.

W4 behaviour, before and after:

| | 041 / 043 | 044 |
|---|---|---|
| Label | `free_throw_made` | `free_throw_made` |
| Confidence | 0.95 / 0.90 | **0.49** |
| Decision | `confirmed` | **`potential_event`** (human review) |
| Verification reason | identical to discovery | **independent** |

The new verification reason: *"White player #11 shoots a free throw around
07.0–08.5s, but the basketball hoop and net outcome are completely
occluded/off-camera behind court elements."*

That is the honest answer. Human adjudication established the free throw does
not go in; the model's viewing angle cannot resolve the outcome at all. Before
this change it asserted a make at 0.95 confidence. It now declines and routes to
review. W2's three correct events are unaffected and still confirm.

The verifier still echoes discovery on W2, where it agrees. Independence appears
where it matters — on the case whose evidence does not support the proposal.

## Budget

- Ledger before: $9.814099875
- Live video calls: 4, zero provider errors
- Incremental estimated spend: **$0.0899640**
- Ledger after: **$9.904063875**
- Ceiling $11.192294875; remaining headroom **$1.288231**

Session total across 043 + 044: $0.2102115.

## Limitations

Three positive labels across two windows. This validates the mechanism, not the
magnitude; the fix has not been run against W1, W5, W6 or W7. Discovery is
untouched, so recall is unchanged and the `block` miss in W5 remains. Single-pass
control reused from 038 rather than re-run. Holdout untouched; golden labels
unmodified.

## Next

Re-run all seven windows with the fixed verifier to measure the effect on the
full development set, then re-adjudicate W1, whose reference is still
contradicted by four independent runs.
