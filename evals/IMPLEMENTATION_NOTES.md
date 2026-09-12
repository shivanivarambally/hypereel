# Evaluation implementation notes

This is an append-only, human-readable record of the evaluation work: what changed, what was learned, the current decision, and the next action. Add a timestamped entry after every material implementation or evaluation milestone. Do not rewrite earlier entries when a later experiment changes the conclusion; record the correction in a new entry.

Machine-readable run details remain in [`iterations/history.jsonl`](iterations/history.jsonl), and cumulative provider cost remains in [`iterations/spend-ledger.json`](iterations/spend-ledger.json).

---

## 2026-09-12 12:04:59 IST — Consolidated state before native-video benchmark

### Repository state

- All accepted work is merged into `main`.
- PR #2, **Add LLM-as-a-Judge support to evaluation framework**, is merged at `40bb404`.
- The local working tree and `origin/main` were synchronized before this entry.
- The full automated test suite passed after the merge, with four tests skipped.
- The remaining warning is the deprecated `google.generativeai` dependency; migration to `google.genai` is recommended but is not blocking the evaluation work.

### Reference data

Three externally labeled basketball games are stored in the repository:

- Two development games may be used for implementation, prompt refinement, thresholds, and model comparison.
- One sealed holdout game is reserved for the final unbiased validation.
- The holdout has not been used to choose code, prompts, thresholds, sampling, or models.

### Evaluation coverage

The framework now records:

- Candidate recall, including IoU thresholds 0.10, 0.30, and 0.50.
- Selected-event precision, recall, micro F1, and macro F1.
- Per-event-type results, confusion matrices, and balanced accuracy.
- Temporal IoU, event-time error, boundary error, action completeness, and near misses.
- False positives per video minute, duplicate rate, and selected-clip overlap.
- Negative-window specificity, average precision, calibration error, and threshold sweeps.
- Proposal-to-classification-to-selection funnel survival.
- Schema validity, operational success, latency, provider calls, token usage, estimated spend, and cost per true positive.
- LLM-as-a-Judge results as an advisory signal. The judge sees prediction/reference metadata rather than rendered video, so it must not replace deterministic release gates or human media review.

All paid evaluation iterations are retained. Reports are append-only and include change notes, dataset hashes, code revision, working-tree state, provider usage, and cumulative spend.

### Current Nebius results

Best tuned development slice, iteration 18:

| Metric | Result | Required gate |
|---|---:|---:|
| Candidate recall at IoU 0.30 | 1.000 | 0.800 |
| Selected-event precision | 0.667 | 0.700 |
| Selected-event recall | 1.000 | 0.700 |
| Selection F1 | 0.800 | 0.700 |
| Selected-event recall at IoU 0.30 | 1.000 | 0.700 |
| Schema pass rate | 1.000 | 1.000 |

Clean independent slice from a different development game, iteration 20:

| Metric | Result | Required gate |
|---|---:|---:|
| Candidate recall at IoU 0.30 | 1.000 | 0.800 |
| Selected-event precision | 1.000 | 0.700 |
| Selected-event recall | 0.500 | 0.700 |
| Selection F1 | 0.667 | 0.700 |
| Selected-event recall at IoU 0.30 | 0.500 | 0.700 |
| Negative-window specificity | 1.000 | monitored |
| Schema pass rate | 1.000 | 1.000 |

The independent slice fails the recall, F1, and temporal-recall gates. Iteration 21 attempted alternative-label recovery, regressed to zero recall, and was rejected. Its result remains in history, while its implementation behavior was reverted.

### Cost position

- Cumulative estimated Nebius spend: **$2.53027**.
- Original hard ceiling: **$5.00**.
- Remaining headroom under that ceiling: **$2.46973**.
- The spend ledger is cumulative and must never be cleared between iterations.

### What is working

- Local motion proposal generation usually finds the externally labeled action regions.
- IoU-aware scoring now distinguishes loose overlap from a usable, correctly timed clip.
- Centered clip shaping reduces action truncation.
- Dense action frames and explicit before/after context improved temporal grounding.
- Contrastive rejection rules reduced some rebound, miss, and turnover false positives.
- The evaluation identifies whether an event was lost during proposal, classification, or final selection.
- Results, failed experiments, code changes, and provider cost are auditable rather than overwritten.

### Principal learnings and limitations

1. **The main remaining failure is semantic classification, not proposal recall.** Motion is useful for locating activity but cannot determine whether the action is a steal, rebound, turnover, miss, or basket.
2. **Scoreboard changes are supporting evidence only.** They may be delayed, manually updated, or absent and cannot ground steals, turnovers, rebounds, or blocks.
3. **Sparse independent frames are inadequate for subtle possession changes.** Basketball events require ordered motion and often several frames per second.
4. **The current Nebius model is not sufficiently reliable.** The account exposes `openbmb/MiniCPM-V-4_5`, which confused steals, rebounds, and made baskets, rejected valid steals, and changed semantic verdicts across identical temperature-zero runs.
5. **One label per candidate window is structurally insufficient.** A 10–15-second proposal may contain multiple legitimate events, each needing its own label and temporal interval.
6. **Prompt tuning has reached diminishing returns.** More timestamp-specific fixes against the same clips would be a whack-a-mole solution and would overfit the development data.
7. **The holdout must stay sealed.** It is only useful if code, model, prompt, thresholds, and sampling are frozen before its single final evaluation.

### Architecture decision

Move toward native-video, multi-label temporal detection. A classifier should return zero or more events per candidate clip, for example:

```json
{
  "events": [
    {
      "type": "steal",
      "start_seconds": 3.2,
      "end_seconds": 4.7,
      "confidence": 0.91,
      "evidence": "Defender deflects the pass and establishes possession"
    },
    {
      "type": "made_basket",
      "start_seconds": 8.0,
      "end_seconds": 9.4,
      "confidence": 0.87,
      "evidence": "Ball visibly passes through the rim"
    }
  ]
}
```

Overlapping proposal clips must then be consolidated without collapsing distinct events that happen close together.

### Model strategy

1. Benchmark `nvidia/Cosmos-Reason2-2B` first using native 8–15-second video clips at approximately 4 FPS.
2. If 2B approaches but misses the gates, benchmark Cosmos-Reason2-8B.
3. Compare Qwen2.5-VL-7B and, optionally, Molmo2-8B before training.
4. Use Fireworks Qwen3 Omni only after verifying dedicated-deployment cost and automatic shutdown behavior.
5. Keep Nebius as a baseline or secondary signal, not the sole production classifier.
6. Fine-tune only after untuned comparisons identify consistent, correctable errors.

If fine-tuning is justified, Qwen2.5-VL-7B with LoRA is the current preferred candidate because it has native video support and mature video-training tooling. Training must include positive events and hard negatives: steals, baskets, three-pointers, blocks, turnovers, offensive and defensive rebounds, missed shots, fouls, free throws, timeouts, dead balls, adjacent-court action, occlusion, and varied lighting.

The two development games may support a feasibility experiment but are not sufficient evidence of broad generalization. Additional venues, camera angles, uniforms, age groups, and lighting conditions will be needed before making a production-quality claim.

### Ordered next steps

1. Run `brev login` locally and complete browser authentication. Do not place Brev credentials in the repository.
2. Search Brev for the cheapest stoppable GPU with at least 24 GB VRAM.
3. Before provisioning, define a new-compute ceiling of $5 and a time-based automatic shutdown.
4. Deploy Cosmos-Reason2-2B and verify native-video inference on one short non-holdout clip.
5. Add a provider adapter and multi-label temporal schema behind a feature flag so the current deterministic path remains available.
6. Add tests for zero events, multiple events, overlapping proposals, invalid intervals, unknown labels, duplicates, and provider failures.
7. Run the same development slices used for the Nebius comparison and append every result to the existing history.
8. Compare precision, recall, F1, IoU-threshold recall, specificity, stability, latency, and total cost against the Nebius baseline.
9. If the gates fail, test Cosmos-Reason2-8B or Qwen2.5-VL-7B before considering LoRA.
10. When all development gates pass on an independent slice, freeze the implementation and run the complete first development video end-to-end.
11. Run the sealed third game exactly once for final validation. Do not tune after examining its result.
12. Produce the final evaluation report with deterministic metrics, advisory judge output, human media review, provider cost, and known limitations.

### Immediate blocker

The Brev CLI is installed but not authenticated. The next action requiring the project owner is:

```bash
brev login
```

After authentication, the Cosmos-Reason2-2B benchmark can begin without sharing account credentials.
