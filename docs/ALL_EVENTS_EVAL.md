# All-event development evaluation

> **Historical local-model protocol.** For the latest Gemini development comparison and live-demo results, start with [evaluation status](../evals/STATUS.md). The commands below describe the earlier local-model experiments.

The event detector in `src/hypereel/evaluation/basketball_events.py` scores detection
before highlight selection. It preserves multiple events per sequence, including
steal/turnover and missed-shot/rebound pairs. It does not change the production
legacy single-label API. The opt-in native Gemini graph now also supports multiple timestamped events per window; see [the current workflow](TWO_PHASE_REVIEW.md). This document's local-model run descriptions below remain historical.

Only the two allowlisted development games are loaded. Never use the third golden
or holdout game during development. Source exports are approximately720p; actual
encoded inputs are768x431 or768x432. The original009–011 experiments below use no cloud provider or judge. Later012–027 pilots include hosted MiniCPM and Gemini; Gemini video inputs use native1280-wide muted clips at requested4fps. Current status and limits are in `../evals/AGENT_HANDOFF.md` and `EVALUATION_TESTING.md`.

## Reproducible experiments

Run from the repository root. Existing output directories are never overwritten;
these commands document completed/planned experiment identities, not retries.

```sh
.venv/bin/python scripts/eval_all_events_local.py --iteration 009 --frames 4 --variant direct
.venv/bin/python scripts/eval_all_events_local.py --iteration 010 --frames 6 --variant direct
.venv/bin/python scripts/eval_all_events_local.py --iteration 011 --frames 6 --variant observations
```

009/010 use the same8 frozen windows in diagnostic-009.json:14 annotations spanning
all12 categories, across64 seconds of sampled source coverage. These were selected
using labels to diagnose coverage, not by production proposals. Two windows contain
no annotations but are not verified negatives. 011 is a two-window explanatory
subset (original windows1 and6); compare it only with the corresponding010 windows.

All runs use local qwen3-vl:4b-instruct with pinned digest,8192 context,768 output,
batch128,768px image edge,temperature0,seed0,180s per-request timeout and serial calls.
Memory warnings alone do not stop execution. An actual provider/schema/context/
timeout/budget failure stops the batch; no automatic retries. Unprocessed references
are not counted as completed misses or negatives. Check completed/planned coverage.

## Metrics and limits

Per-type precision,recall,F1,support and TP/FP/FN are primary evidence. Macro F1
averages supported reference classes equally; micro F1 pools events. Worst-type
recall highlights complete category failures. Model-reported confidence is not a
quality score. Every emitted event is scored without confidence filtering.

Matching is maximum-cardinality,one-to-one,same-game,same-label with a frozen5-second
point tolerance. Duplicate predictions remain false positives. External timestamps
are provisional clip timestamps,not audited action bounds: do not claim action IoU
or exact temporal accuracy. No release pass can be inferred from this diagnostic,
even if its tiny class samples score perfectly. Representative continuous intervals,
verified negatives and audited timing are needed before development quality gates
or any final validation. Full-game proposal recall and highlight selection quality
are not measured by this detector diagnostic.

## Evidence and notes

Each `evals/iterations/ollama-all-events-NNN/` retains report,raw-response checkpoints,
usage,memory samples,and code snapshots. Reconstructed input audits preserve JPEG
hashes and actual dimensions separately from runtime checkpoints. 011 raw responses
include required per-image observations even when events are empty. Invalid output
is retained before parsing and is never silently converted to a successful empty list.

Append every hypothesis/result to IMPLEMENTATION_NOTES.md,iteration-log.md and the
all-event-specific `iterations/all-events-history.jsonl`; preserve legacy history.
Update STATUS.md and AGENT_HANDOFF.md. Never overwrite failed attempts or labels to
fit predictions. Offline checks: exclude the `final_holdout` test during development.
