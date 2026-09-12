# Nebius iteration log

Provider model: `openbmb/MiniCPM-V-4_5`. Dollar estimates use deliberately conservative configured token rates because a verified model-specific rate was unavailable. Every paid run was capped at five provider calls. Results below are development data only.

| Iteration | Slice / change | Candidate recall | Precision | Recall | F1 | Schema pass | TP/FP/FN | Estimated spend | Cumulative |
|---:|---|---:|---:|---:|---:|---:|---|---:|---:|
| 1 | Opening baseline; first four chronological candidates | N/A* | 0.00 | N/A | N/A | 0.75 | 0/2/0 | $0.05452 | $0.05452 |
| 2 | 60-100s positive slice; three frames | 0.00** | 0.00 | 0.00 | N/A | 1.00 | 0/2/1 | $0.05200 | $0.10652 |
| 3 | Added four-second context and five frames | 1.00** | 0.00 | 0.00 | N/A | 0.50 | 0/1/1 | $0.07806 | $0.18458 |
| 4 | Six-second context, nine frames, temporal basketball rubric, tolerant JSON | 1.00 | 0.00*** | 0.00*** | N/A | 1.00 | 0/2/1*** | $0.10725 | $0.29183 |
| 5 | Independent 145-190s slice with two events | 1.00 | 0.00 | 0.00 | N/A | 1.00 | 0/2/2 | $0.12119 | $0.41302 |
| 6 | Spread sampling plus shot-evidence guard and null-clip filter | 1.00 | 1.00 | 0.50 | 0.667 | 1.00 | 1/0/1 | $0.11207 | $0.52509 |
| 7 | Different-lighting game; spread sampling | 1.00 | 0.00 | 0.00 | N/A | 1.00 | 0/3/2 | $0.10672 | $0.63181 |
| 8 | Reference-stratified diagnostic sampling | 1.00 | 0.333 | 0.50 | 0.40 | 1.00 | 1/2/1 | $0.10614 | $0.73795 |
| 9 | Dense central-action frames | 1.00 | 0.333 | 0.50 | 0.40 | 1.00 | 1/2/1 | $0.10833 | $0.84628 |
| 10 | Reduced temporal context | 1.00 | 0.333 | 0.50 | 0.40 | 1.00 | 1/2/1 | $0.10954 | $0.95582 |
| 11 | Explicit before/action/after frame roles | 1.00 | 0.50 | 0.50 | 0.50 | 1.00 | 1/1/1 | $0.11358 | $1.06940 |
| 12 | Maximum-IoU diagnostic candidate alignment | 1.00 | 0.00 | 0.00 | N/A | 1.00 | 0/1/2 | $0.11040 | $1.17980 |
| 13 | Three-second proposal padding; exposed overly permissive matching† | 1.00 | 1.00† | 1.00† | 1.00† | 1.00 | 2/0/0† | $0.09189 | $1.27169 |
| 14 | IoU-aware primary match correction | 1.00 | N/A | 0.00 | N/A | 1.00 | 0/0/2 | $0.09085 | $1.36254 |
| 15 | Deterministic temperature; padded candidates | 1.00 | 0.667 | 1.00 | 0.80 | 1.00 | 2/1/0 | $0.09316 | $1.45570 |
| 16 | Core-frame verification | 1.00 | 0.667 | 1.00 | 0.80 | 1.00 | 2/1/0 | $0.15164 | $1.60734 |
| 17 | Explicit rebound/miss/turnover negatives | 1.00 | 0.667 | 1.00 | 0.80 | 1.00 | 2/1/0 | $0.15578 | $1.76312 |
| 18 | Centered clips plus contrastive verification | 1.00 | 0.667 | 1.00 | 0.80 | 1.00 | 2/1/0 | $0.15299 | $1.91611 |
| 19 | Fresh slice; revealed boundary and multi-event ambiguity | 0.667 | 0.50 | 0.333 | 0.40 | 1.00 | 1/1/2 | $0.20560 | $2.12171 |
| 20 | Clean slice on the other development game | 1.00 | 1.00 | 0.50 | 0.667 | 1.00 | 1/0/1 | $0.20528 | $2.32699 |
| 21 | Alternative-label verifier experiment (rejected) | 1.00 | N/A | 0.00 | N/A | 1.00 | 0/0/2 | $0.20328 | $2.53027 |

\* Iteration 1's capped horizon contained no reference positives, so positive-class recall is not applicable. Its original full-dataset candidate-recall value of 0 was invalid for a capped run.

\** Iterations 2 and 3 motivated the candidate-recall correction: a local motion window overlapped the labeled action interval but did not contain its single anchor timestamp. The current metric uses action-interval overlap. The table preserves the result available at each iteration and flags the definition change.

\*** Iteration 4 visibly produced a correctly labeled steal clip, but its historical report used anchor containment and also admitted an unclassified clip. These defects were fixed after the run; the historical numbers are retained rather than rewritten.

† Iteration 13 used any-overlap primary matching. Its mean temporal IoU was only 0.059 and recall at IoU 0.30 was zero, so the apparent perfect result was invalid. Iteration 14 corrected the definition; history remains unchanged.

## Decision

### Local evaluation 001 — 2026-09-12

Ollama `qwen3-vl:4b-instruct` on Apple M1 / 16 GB, game 1 seconds 295–340,
four reference-stratified diagnostic candidates, 5 frames, 6-second context,
448px edge, 8,192 context tokens, 256 output tokens, no verification.
Cached source was 640x360; this is not a controlled model-only comparison
against earlier runs with different sampling/provider settings.

| Candidate recall@0.30 | Precision | Recall | F1 | Temporal recall@0.30 | Schema pass | TP/FP/FN | Runtime | Cloud cost |
|---:|---:|---:|---:|---:|---:|---|---:|---:|
| 1.00 | N/A (no clips) | 0.00 | N/A (evaluator convention) | 0.00 | 1.00 | 0/0/2 | 321.2s | $0.00 |

All four classifications were valid null outputs, not provider errors. Negative-window
specificity was 1.00, which does not compensate for missing every positive event.
Five local requests completed (four vision, one judge). A subsequent judge attempt
was denied by the request cap; the existing graph fallback accepted progression to
human review. That is not acceptance of model quality. Local text exceptions now
surface as “judge unavailable” rather than empty responses; this infrastructure fix
was tested offline, not presented as another quality iteration.

The local feasibility test **passes execution but fails the quality gate**. No full
first-video or sealed-holdout run followed. All raw results are retained in
[`ollama-development-001.report.json`](ollama-development-001.report.json), with the
compact result also appended to `history.jsonl`. Cumulative estimated cloud spend
remains $2.53027. Earlier Nebius decisions below are historical.

The best tuned-slice result is iteration 18 (precision 0.667, recall 1.00, F1 0.80, IoU-0.30 recall 1.00). The clean independent slice in iteration 20 has perfect precision but only 0.50 recall and 0.667 F1, so the release gate is not met. Iteration 21 was rejected and its code change reverted. The Nebius account exposes only `openbmb/MiniCPM-V-4_5`; repeated temperature-zero runs still changed semantic verdicts. A full-video paid run or sealed-holdout run is therefore not authorized. The durable next step is a stronger video-capable provider/model or a multi-label temporal event schema, not further timestamp-specific prompt tuning.

### Local evaluation 002 game1 — 2026-09-12T14:04:22.349901+05:30

| Attempt | Outcome | TP/FP/FN, P/R/F1 | Runtime | Decision |
|---|---|---|---|---|
| ollama-development-002-game1 | Interrupted during vision inference, macOS memory pressure level 2 | N/A: incomplete, no completed report | Approximately 115.23s | Stop batch; no automatic retry |

Model/configuration unchanged except six-call cap. Partial usage unavailable after interruption; this is not a zero-output quality result. Game2 downloaded/cached and preflighted, but inference did not start. Full attempt evidence: `ollama-development-002-game1.aborted.json`. No cloud spend, full-game processing, highlight rendering, or holdout access.

### Local evaluation 003 game1 — 2026-09-12T14:12:03.080513+05:30

Unchanged six-call-cap baseline interrupted by monitor at 35.41s, pressure warning level 2 after normal readings through 30.07s. Vision HTTP wait interrupted; no complete TP/FP/FN, P/R/F1, or token accounting available. No inference retry within this batch; game2 not started. See `ollama-development-003-game1.execution.json`. No cloud cost or holdout use.

### Local evaluation 004 game1 — 2026-09-12T14:16:08.192021+05:30

| Change | Result | TP/FP/FN; P/R/F1 | Runtime | Decision |
|---|---|---|---|---|
| Explicit num_batch128; all visual/scoring settings unchanged | Memory warning; interrupted during vision HTTP wait | N/A, incomplete; partial token usage unknown | 110.67s | Not sufficient to complete this attempt; stop batch |

Normal pressure through the earlier 50s checkpoint did not establish runtime viability. Do not infer an accuracy improvement or causal memory benefit from longer elapsed time in a single run. Game2 not started, no cloud cost, no highlight rendering, holdout sealed. Detailed observations and hashes: `ollama-development-004-game1.execution.json`; traceback retained under results/iterations/ollama-development-004-game1/.

### Local evaluation005 game1 — 2026-09-12T15:50:14.353575+05:30

| Change | Outcome | Time | Peak sampled llama-server RSS | Completed classifications / usage |
|---|---|---|---|---|
| Three core frames, context4096, batch128, durable per-call checkpoints | Monitor stopped at memory warning during model loading; no observed crash | 24.58s | 3,137,376 KiB = 2.99 GiB | 0; one started call, returned tokens unknown |

Server log confirms client cancellation before loading finished; this is not an observed OOM crash or inference-accuracy result. Checkpoint preserved request start and KeyboardInterrupt scope exit. Probe did not pass operational continuation condition, so006 and game2 were not launched. No cloud cost, highlight rendering, or holdout access. Execution samples and loading evidence preserved.

### ollama-development-006-game1 — 2026-09-12T16:15:37.349332+05:30

| TP/FP/FN | Precision | Recall | F1 | Runtime | Peak sampled RSS | Quality gate |
|---|---|---|---|---|---|---|
| {'tp': 0, 'fp': 0, 'fn': 2} | None | 0.0 | None | 194.70s | 4.614GiB | False |

Memory warnings recorded without aborting per owner instruction. None metrics are N/A. Full evidence: `ollama-development-006-game1.report.json`, `ollama-development-006-game1.execution.json`, `ollama-development-006-game1.observations.json`, and checkpoint directory.

### ollama-development-006-game2 — 2026-09-12T16:18:16.142567+05:30

| TP/FP/FN | Precision | Recall | F1 | Runtime | Peak sampled RSS | Quality gate |
|---|---|---|---|---|---|---|
| {'tp': 0, 'fp': 0, 'fn': 2} | None | 0.0 | None | 130.06s | 4.693GiB | False |

Memory warnings recorded without aborting per owner instruction. None metrics are N/A. Full evidence: `ollama-development-006-game2.report.json`, `ollama-development-006-game2.execution.json`, `ollama-development-006-game2.observations.json`, and checkpoint directory.

### ollama-development-007-game1 — 2026-09-12T16:38:49.202153+05:30

| TP/FP/FN | Precision | Recall | F1 | Runtime | Peak sampled RSS | Quality gate |
|---|---|---|---|---|---|---|
| {'tp': 0, 'fp': 0, 'fn': 2} | None | 0.0 | None | 261.06s | 4.685GiB | False |

Memory warnings recorded without aborting per owner instruction. None metrics are N/A. Full evidence: `ollama-development-007-game1.report.json`, `ollama-development-007-game1.execution.json`, `ollama-development-007-game1.observations.json`, and checkpoint directory.

### ollama-development-007-game2 — 2026-09-12T16:42:45.709021+05:30

| TP/FP/FN | Precision | Recall | F1 | Runtime | Peak sampled RSS | Quality gate |
|---|---|---|---|---|---|---|
| {'tp': 0, 'fp': 0, 'fn': 2} | None | 0.0 | None | 228.05s | 4.658GiB | False |

Memory warnings recorded without aborting per owner instruction. None metrics are N/A. Full evidence: `ollama-development-007-game2.report.json`, `ollama-development-007-game2.execution.json`, `ollama-development-007-game2.observations.json`, and checkpoint directory.

### ollama-development-008-game1 — 2026-09-12T16:50:07.190879+05:30

| TP/FP/FN | Precision | Recall | F1 | Runtime | Peak sampled RSS | Quality gate |
|---|---|---|---|---|---|---|
| {'tp': 0, 'fp': 0, 'fn': 2} | None | 0.0 | None | 409.03s | 5.613GiB | False |

Memory warnings recorded without aborting per owner instruction. None metrics are N/A. Full evidence: `ollama-development-008-game1.report.json`, `ollama-development-008-game1.execution.json`, `ollama-development-008-game1.observations.json`, and checkpoint directory.

### ollama-development-008-game2 — 2026-09-12T16:55:40.676837+05:30

| TP/FP/FN | Precision | Recall | F1 | Runtime | Peak sampled RSS | Quality gate |
|---|---|---|---|---|---|---|
| {'tp': 0, 'fp': 0, 'fn': 2} | None | 0.0 | None | 301.67s | 5.479GiB | False |

Memory warnings recorded without aborting per owner instruction. None metrics are N/A. Full evidence: `ollama-development-008-game2.report.json`, `ollama-development-008-game2.execution.json`, `ollama-development-008-game2.observations.json`, and checkpoint directory.

### 2026-09-12T17:34:51.577274+05:30 ollama-all-events-009

{"name": "ollama-all-events-009", "status": "completed", "elapsed_seconds": 524.2359207090049, "attempted_calls": 8, "completed_windows": 8, "planned_windows": 8, "peak_sampled_llama_rss_gib": 5.2940673828125, "error_type": null, "tp": 0, "fp": 0, "fn": 14, "macro_f1": 0.0, "micro_f1": 0.0, "measured_types": 12}

### 2026-09-12T17:47:50.420748+05:30 ollama-all-events-010

{"name": "ollama-all-events-010", "status": "completed", "elapsed_seconds": 773.3768672499864, "attempted_calls": 8, "completed_windows": 8, "planned_windows": 8, "peak_sampled_llama_rss_gib": 5.583953857421875, "error_type": null, "tp": 0, "fp": 0, "fn": 14, "macro_f1": 0.0, "micro_f1": 0.0, "measured_types": 12}

### 2026-09-12T17:50:18.449221+05:30 ollama-all-events-011

{"name": "ollama-all-events-011", "status": "completed", "elapsed_seconds": 133.19093837498804, "attempted_calls": 2, "completed_windows": 2, "planned_windows": 2, "peak_sampled_llama_rss_gib": 6.400054931640625, "error_type": null, "tp": 0, "fp": 0, "fn": 6, "macro_f1": 0.0, "micro_f1": 0.0, "measured_types": 6}

### 2026-09-12T18:12:34.311555+05:30 nebius-matched-012

{"name": "nebius-matched-012", "status": "failed_or_interrupted", "error_type": "ValueError", "http_status": null, "attempted_calls": 17, "elapsed_seconds": 56.56678270897828, "estimated_spend_usd": 0.41311000000000003, "metrics": {"009": {"tp": 4, "fp": 32, "fn": 10, "micro_f1": 0.16, "macro_f1": 0.05979020979020979}, "010": {"tp": 5, "fp": 49, "fn": 9, "micro_f1": 0.14705882352941177, "macro_f1": 0.09615384615384615}, "011": {"tp": 0, "fp": 0, "fn": 0, "micro_f1": null, "macro_f1": null}}}

### 2026-09-12T19:05:17.629979+05:30 evidence-pilot-013

{"name": "evidence-pilot-013", "status": "completed_with_arm_failures", "attempted_calls": 10, "elapsed_seconds": 31.626363916002447, "estimated_spend_usd": 0.8289200000000001, "arms": {"wide6_context": {"status": "completed", "completed": 8, "tp": 3, "fp": 31, "fn": 11, "micro_f1": 0.125, "macro_f1": 0.04708994708994709}, "wide12_context": {"status": "failed", "completed": 0, "tp": 0, "fp": 0, "fn": 0, "micro_f1": null, "macro_f1": null}, "wide12_ball_crops": {"status": "failed", "completed": 0, "tp": 0, "fp": 0, "fn": 0, "micro_f1": null, "macro_f1": null}}}

### 2026-09-12T19:10:34.868433+05:30 evidence-pilot-013

{"name": "evidence-pilot-014", "status": "completed_with_arm_failures", "attempted_calls": 5, "elapsed_seconds": 60.52487195798312, "estimated_spend_usd": 0.37421, "arms": {"wide12_context": {"status": "failed", "completed": 0, "tp": 0, "fp": 0, "fn": 0, "micro_f1": null, "macro_f1": null}, "wide12_ball_crops": {"status": "failed", "completed": 3, "tp": 1, "fp": 21, "fn": 4, "micro_f1": 0.07407407407407407, "macro_f1": 0.05714285714285714}}}


### Bounded pilot013/014 — final interpretation

Bounded pilot 013/014 finished with arm failures; no production architecture adoption.

User authorization to run this pilot superseded the earlier analysis-only pause. Used Nebius MiniCPM-V-4_5 consistently across input arms and local YOLO11n COCO for optional ball crops. The two development games, original eight core windows, 14 reference events, 12 category definitions and five-second one-to-one matcher remained frozen. Third dataset untouched.

013: six wide frames plus context completed 8/8 windows: TP3/FP31/FN11, precision8.82%, recall21.43%, microF1 12.50%, macroF1 4.71%. Twelve-image and crop requests each failed on first request with BadRequestError; exact error body was not retained, so the exact provider limit is unknown. These arms have no valid semantic result.

014: predeclared compatibility change packed the same12 timestamps into six two-row sheets, equal canvas in dense/crop arms. Dense arm returned20events against the maximum12 and stopped at0/8 valid. Crop arm completed3/8 windows then returned20events and stopped: partial TP1/FP21/FN4, precision4.55%, recall20%, microF1 7.41%. Both schema failures had finish_reason=stop, not output truncation. Raw responses preserved; no relaxed validation or automatic retries. No planned identical-input reuse actually occurred. No common completed dense/crop window exists, so there is NO valid paired estimate of YOLO benefit. Differences from013 also confound packing and coverage.

YOLO produced ball candidates in6/96 sampled frames (only two windows; none for campus). This is candidate frequency, not audited ball recall. Detector preparation22.33s, sampled peak process RSS0.410GiB. No observed machine crash. Cloud client RSS is not hosted model memory. Repeated frame-level shot/rebound stories and scoreboard-based explanations remain a grounding/event-identity failure despite explicit instructions; greater visible detail alone did not establish reliable event recognition.

Actual15 cloud attempts across both iterations. Conservative ledger increment$1.20313 includes$0.60 reserved for two rejected requests with unknown usage; cumulative$4.14651 of$5. These are estimates, not invoice charges. No further inference is running or scheduled. New isolated detector environment, preparation/runner scripts, frame manifests/hashes, boxes, memory checkpoints, raw responses, usage and failure audits retained. Production application unchanged.

Validation:352 tests passed,4 skipped,1 final_holdout test deselected. Do not treat failed/unattempted windows as zero-event successes. Existing labels and provisional timing are best-effort evidence, not an audited benchmark; annotation-empty controls are not verified negatives.

Decision: do not adopt the generic YOLO crop pipeline based on this pilot. The next bounded refinement should first validate provider-compatible structured output and require distinct action evidence across timestamps, using retained development clips/raw outputs to address repeated invented events. Keep event definitions and scoring frozen, then predeclare any fresh comparison. Do not increase event limits, discard unmatched predictions, or integrate tracking merely to improve the reported score. No user annotation work is required to interpret this pilot.

### 2026-09-12T19:47:12.044347+05:30 — transcript-pilot-015

{"name": "transcript-pilot-015", "started_at": "2026-09-12T19:46:51.779503+05:30", "ended_at": "2026-09-12T19:47:12.041385+05:30", "status": "completed_with_invalid_windows", "elapsed_seconds": 20.259019332996104, "attempted_calls": 9, "estimated_spend_usd": 0.18957000000000002, "common_completed_indices": [2, 6], "paired_metrics": {"direct": {"tp": 2, "fp": 6, "fn": 7, "micro_precision": 0.25, "micro_recall": 0.2222222222222222, "micro_f1": 0.23529411764705882, "macro_f1": 0.1, "measured_types": 8}, "transcript": {"tp": 3, "fp": 3, "fn": 6, "micro_precision": 0.5, "micro_recall": 0.3333333333333333, "micro_f1": 0.4, "macro_f1": 0.25, "measured_types": 8}}}

### 2026-09-12T19:50:21.866669+05:30 — transcript-pilot-015 interpretation

Transcript pilot015 completed at 2026-09-12T19:47:12.041385+05:30; final audit recorded 2026-09-12T19:50:21.866669+05:30.

User identifies HoopIQ as the specialist source of the supplied golden labels. No replacement specialist or new user annotation was required. Tested fresh direct detection against observation-only visual narration followed by text-only event extraction, using the same Nebius MiniCPM-V-4_5 for all stages. Three frozen development windows [1,2,6],10 references across9 supported types, all12 event definitions available. Identical6frame JPEG sequences per visual arm,768pixel wide,2.4second gaps across12seconds including2seconds context either side. This isolates representation change on sparse evidence; it is not continuous-video transcription or speech recognition. No references entered model prompts. Third dataset untouched.

Nine of nine provider calls returned completed output in 20.26s; no provider crash, timeout or retry. All3 narrations parsed, all3 direct results parsed,2of3 extraction outputs passed the original strict core-time validation. Window1 emitted an event at233s outside223–231, so that whole transcript result was excluded from primary paired metrics. All raw outputs, input hashes, prompts, observation IDs, per-call timestamps, latencies, usage and memory/pressure checkpoints are preserved. Per-call raw text and parsed window outputs were appended to IMPLEMENTATION_NOTES during execution.

Primary matched coverage: windows2and6,9 references across8 supported types. Direct TP2/FP6/FN7,precision25%,recall22.22%,microF1 23.53%,macroF1 10%. Transcript TP3/FP3/FN6,precision50%,recall33.33%,microF1 40%,macroF1 25%. Unmeasured categories must not be described as passing. Available-only full direct metrics use3windows and cannot be directly compared with2window transcript metrics.

Audit identified asymmetric boundary handling: direct accepted observed context then filtered; extraction required core bounds. Retained original report unchanged. A separately labeled post-hoc offline sensitivity applies direct's context/filter policy to retained extraction outputs acrossall3windows: direct TP2/FP8/FN8,P20%,R20%,F1 20%;transcript TP3/FP4/FN7,P42.86%,R30%,F1 35.29%. No fresh inference or reference changes. Future paired runner must apply identical boundary policy from the outset.

The numerical lift is not established semantic improvement. All6 accepted transcript events cite observations that do not establish their claimed miss or possession outcome. All3 matches are in campus window6. All6 accepted events haveconfidence1.0. All18 narrator rows say visibility=clear despite several descriptions explicitly stating uncertainty. Contact-sheet inspection found clear visual errors: free-throw setup mislabeled as a shot near the three-point line; midcourt ball handling narrated as a shot towards the basket. Full qualitative audit is in observation-audit.json. This audit is agent inspection, not independent human reannotation; original HoopIQ labels/times remain unchanged.

Implementation: added evaluation/transcript.py for timestamp-anchored observations, text-only extraction and valid observation-ID checks; scripts/run_transcript_pilot.py for bounded paired inference and live notes; scripts/audit_transcript_pilot.py for reproducible offline sensitivity. Citation validation establishes ID existence, not factual entailment. No semantic filter was retroactively used to boost scores. Production application architecture unchanged.

Tests:355 passed,4 skipped,1 final_holdout test deselected; no holdout evaluation. Three new tests cover time anchoring/order, paired events, invented citations and empty-transcript evidence. Spend estimateincrement$0.18957,ledger cumulative$4.33608 against$5 ceiling; historical conservative estimates,not invoice prices. No inference remains running.

Decision: retain the transcript and evidence-link format as a diagnostic tool; do not adopt this MiniCPM narration/extraction combination as a reliable detector. Both visual narration and text-to-event reasoning failed. Next refinement should first enforce common boundary handling and evaluate extraction entailment on these frozen transcripts, then test visual narration with genuinely richer temporal evidence or a better visual model under a separately frozen comparison. Treat observation accuracy and event matching separately; do not equate a valid citation or high model confidence with correctness. No new architecture switch or paid run was started after this audit.

### 2026-09-12T19:59:37.946110+05:30 — User-facing interpretation clarified and handoff refreshed

User asked whether015 used transcripts with YOLO/Qwen and whether metrics improved dramatically. Clarified: hosted MiniCPM only, direct versus two-stage narration/extraction; identical six frames, noYOLO orQwen. Numerical lift is real on two windows: TP2→3,FP6→3,FN7→6,precision25%→50%,recall22.22%→33.33%,F1 23.53%→40%. Small sample, third extraction invalid, unsupported event evidence prevent a reliable-improvement claim. Transcript approach remains worth testing; do not dismiss score gains or overstate them. AGENT_HANDOFF.md now provides a current single entry point, reading order, scope, budget, evidence distinctions, implementation paths and next decision. Documentation-only update; no inference, reference change or third-dataset access.

### 2026-09-12T20:53:43.581258+05:30 — dense-pilot-016

{"name": "dense-pilot-016", "started_at": "2026-09-12T20:52:23.928678+05:30", "ended_at": "2026-09-12T20:53:43.576834+05:30", "status": "completed_with_invalid_windows", "elapsed_seconds": 79.64662833302282, "attempted_calls": 24, "estimated_spend_usd": 0.5493600000000002, "metrics": {"all_windows": {"indices": [0, 1, 3, 6], "direct": {"tp": 2, "fp": 22, "fn": 4, "micro_precision": 0.08333333333333333, "micro_recall": 0.3333333333333333, "micro_f1": 0.13333333333333333, "macro_f1": 0.06666666666666667}, "transcript": {"tp": 3, "fp": 17, "fn": 3, "micro_precision": 0.15, "micro_recall": 0.5, "micro_f1": 0.23076923076923078, "macro_f1": 0.27777777777777773}}, "paired_with_015": {"indices": [1, 6], "direct": {"tp": 2, "fp": 8, "fn": 4, "micro_precision": 0.2, "micro_recall": 0.3333333333333333, "micro_f1": 0.25, "macro_f1": 0.16666666666666666}, "transcript": {"tp": 3, "fp": 3, "fn": 3, "micro_precision": 0.5, "micro_recall": 0.5, "micro_f1": 0.5, "macro_f1": 0.4444444444444444}}}, "entailment_screen": {"note": "Recorded, never filtered. Over-permissive lexical screen; not a correctness test.", "events": 20, "supported": 0, "unsupported": 20, "clear_but_hedged": 11, "observations": 48}}

### 2026-09-12T21:08:39.306500+05:30 — state-pilot-017

{"name": "state-pilot-017", "started_at": "2026-09-12T21:08:21.590041+05:30", "ended_at": "2026-09-12T21:08:39.301962+05:30", "status": "completed_with_invalid_windows", "elapsed_seconds": 17.71064741598093, "attempted_calls": 8, "estimated_spend_usd": 0.17668, "metrics": {"indices": [0, 3, 6, 7], "references": 6, "tp": 0, "fp": 0, "fn": 6, "micro_precision": null, "micro_recall": 0.0, "micro_f1": 0.0, "macro_f1": 0.0}, "derivation": {"events": 0, "notes": 2, "contradictory_pairs": 0}}

### 2026-09-12T21:33:02.333393+05:30 —018

{"name": "evidence-state-018", "status": "completed_with_invalid_windows", "started_at": "2026-09-12T21:32:17.756385+05:30", "ended_at": "2026-09-12T21:33:02.329823+05:30", "elapsed_seconds": 44.57331387500744, "attempted_calls": 31, "estimated_spend_usd": 0.47711000000000003, "common_completed_indices": [], "paired_metrics": {"sparse_wide": {"tp": 0, "fp": 0, "fn": 0, "micro_precision": null, "micro_recall": null, "micro_f1": null, "macro_f1": null}, "dense_rim": {"tp": 0, "fp": 0, "fn": 0, "micro_precision": null, "micro_recall": null, "micro_f1": null, "macro_f1": null}}}

### 2026-09-12T21:35:10.201683+05:30 —019

{"name": "evidence-state-019", "status": "completed_with_invalid_windows", "started_at": "2026-09-12T21:34:02.881659+05:30", "ended_at": "2026-09-12T21:35:10.197517+05:30", "elapsed_seconds": 67.31566324998857, "attempted_calls": 50, "estimated_spend_usd": 0.8219599999999998, "common_completed_indices": [2], "paired_metrics": {"sparse_wide": {"tp": 0, "fp": 0, "fn": 4, "micro_precision": null, "micro_recall": 0.0, "micro_f1": 0.0, "macro_f1": 0.0}, "dense_rim": {"tp": 0, "fp": 0, "fn": 4, "micro_precision": null, "micro_recall": 0.0, "micro_f1": 0.0, "macro_f1": 0.0}}}

### 2026-09-12T21:37:57.009084+05:30 —018/019 final audit

Current checkpoint 2026-09-12T21:37:57.009084+05:30:018/019 complete with invalid windows. Corrected v2 rules,4fps source sequences and native rim crops tested.018:31calls,no paired valid windows.019:50calls,one paired window,both armsTP0/FP0/FN4. No demonstrated recognition gain. Mixed-view row duplication and continuing visual errors remain. Total incremental estimated$1.29907;ledger$6.36119of$8.388tests passed,4skipped,1holdout-test deselected. No inference running; third dataset untouched. Read evals/iterations/evidence-state-019/results.md first, then018/019plans/reports and latest IMPLEMENTATION_NOTES. Next decision is a separately frozen perception-component comparison, not another silent MiniCPM prompt retry. Original017code/results remain unchanged; new contract is src/hypereel/evaluation/ball_state_v2.py. No production integration or full court geometry.

### 2026-09-12T21:48:36.359409+05:30 —020

{"name": "track-transcript-020", "status": "completed", "started_at": "2026-09-12T21:48:15.523107+05:30", "ended_at": "2026-09-12T21:48:36.355351+05:30", "elapsed_seconds": 20.83217879102449, "attempted_calls": 9, "estimated_spend_usd": 0.28511, "common_completed_indices": [1, 2, 6], "paired_metrics": {"visual_transcript": {"tp": 3, "fp": 6, "fn": 7, "micro_precision": 0.3333333333333333, "micro_recall": 0.3, "micro_f1": 0.3157894736842105, "macro_f1": 0.2222222222222222}, "track_augmented_transcript": {"tp": 3, "fp": 4, "fn": 7, "micro_precision": 0.42857142857142855, "micro_recall": 0.3, "micro_f1": 0.35294117647058826, "macro_f1": 0.24074074074074073}}}

### 2026-09-12T21:51:35.991675+05:30 —020final audit

Updated 2026-09-12T21:51:35.991675+05:30:020tested YOLO11n+ByteTrack+track-augmented transcript+MiniCPM against shared visual transcript+MiniCPM, on3fully paired development windows(10references,9supported types). TP3→3,FP6→4,FN7→7;precision33.33%→42.86%,recall30%unchanged,microF1 31.58%→35.29%. Modest numerical gain,not reliable event recognition. Native tracking1023frames:only8observed ball-track frames,longest0.133s;no ball tracks in free-throw orCampus clips. All3TPs inCampus;none of7experimental predictions cited a track observation. Evidence errors remain. Local126.33s,peak0.4454GiB;9cloud calls20.83s,$0.28511increment,ledger$6.6463of$8.388tests passed,4skipped,1holdout-test deselected. No inference running,third dataset untouched. Read evals/iterations/track-transcript-020/results.md and plans/raw tracks/report, then latest IMPLEMENTATION_NOTES. Sustained ball tracking is the next unresolved prerequisite; no further experiment scheduled.

### 2026-09-12T22:20:28.754710+05:30 —021 planned
Gemini six-request comparison recorded; API key missing, no inference. See gemini-pilot-021/plan.json and IMPLEMENTATION_NOTES.md.

### 2026-09-12T22:36:14.743400+05:30 — Gemini021/022

021: completed six requests, strict-invalid Markdown wrappers; secondary video F1.47059 vs historical MiniCPM.23077.022: JSON-mode integration first request valid; next request503,stopped. See gemini-pilot-021/results.md,reparse.json and gemini-confirmation-022/report.json. Cumulative ledger$6.753083187500001. Third dataset untouched.

### 2026-09-12T22:51:12.553566+05:30 — Gemini broader partial

023confirmationinterrupted503;024/027validvideo0–5,8references8types,TP3/FP4/FN5,F1.40. Dailyfreequota20exhausted;video6/7andimage2/6missing.025transcript/026image recovery preparednotrun. See gemini-development-summary/results.md;thirdsealed.

### 2026-09-12T22:56:10.655605+05:30 — Versioned development checkpoint

User authorized commit/push of evaluation implementation and testing history.393tests pass;4skipped;1holdout excluded. No new inference. Current status remains dailyquota-blocked partial Gemini evaluation,not completed all12categories.
