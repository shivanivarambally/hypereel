# Disputed reference labels — W1 and W4

Two of the six positive labels in the development reference set are contradicted
by every pipeline run ever made against them. Until they are resolved, no tuning
result on this set is interpretable, because a third of the references are in
dispute.

Nothing here changes a golden label. Record the outcome, then update
`evals/golden/` deliberately and note it in `evals/STATUS.md`.

## W4 — the clean case, decide this one first

**Reference says:** `free_throw_miss`
**Every two-phase run says:** `free_throw_made`

| Source | Verdict | Confidence |
|---|---|---|
| Reference label | miss | — |
| 038 single-pass control | miss | — |
| 040 two-phase @4 fps | **made** | 0.95 |
| 041 two-phase @4 fps | **made** | 0.95 |
| 043 two-phase @8 fps | **made** | 0.90 |

The 8 fps run states it precisely: *"Player #11 in white shoots a free throw at
00:06.8–00:07.5, and the ball goes through the basket at around 00:08.7."*

**What to watch:** `w4_free_throw_6.0-10.5.mp4` (clip-relative time; the shot is
at ~6.8–7.5 s into this excerpt's parent, and the claimed outcome at ~8.7 s).
`w4_frames_7.8-9.6_at8fps.png` is a 5×3 tile of the decisive 1.8 seconds at 8 fps
if the video is ambiguous at speed.

**The question:** does the ball go through the net, or not?

## W1 — four runs against one label

**Reference says:** `free_throw_made`
**Every run says:** a missed field goal followed by a defensive rebound

| Source | Verdict |
|---|---|
| Reference label | `free_throw_made` |
| 038 single-pass control | `defensive_rebound` |
| 040 two-phase @4 fps | `two_point_miss` + `defensive_rebound` |
| 041 two-phase @4 fps | `two_point_miss` + `defensive_rebound` |
| 043 two-phase @8 fps | `two_point_miss` @7.375 + `defensive_rebound` @8.25 |

Four runs, two pipeline designs, two frame rates, all disagreeing in the same
direction. That is not the usual shape of correlated model error.

**What to watch:** `w1_disputed_5.5-10.0.mp4`, or the 5×4 tile
`w1_frames_6.5-9.0_at8fps.png`.

**The questions, in order:** is there a free throw in this window at all? If the
shot is a field goal rather than a free throw, is it made or missed? Is there a
defensive rebound after it?

## What each outcome implies

| Outcome | Consequence |
|---|---|
| Both labels wrong | Discovery on W1/W4/W5 becomes 3/0/1 instead of 1/2/3. The pipeline has been scored as failing while it was correct, and every comparison in 038–043 needs restating. |
| Both labels right | Outcome discrimination is a genuine and stubborn model failure that survives a doubling of temporal resolution. The structured-field schema becomes the next experiment. |
| Split | Fix the wrong one, re-score 038–043, and treat the remaining disagreement as a single real error rather than a pattern. |

## After adjudication

Re-score without spending anything:

```bash
for it in 038 039 040 041 043; do
  .venv/bin/python scripts/score_two_phase_e2e.py \
    --iteration $it --out metrics-family.json --force
done
```

Then append the result and the corrected counts to `evals/STATUS.md`.
