## Publication index — 2026-09-16

- 033–037: human-observation rescoring, possession/rebound investigation and broader prompt changes; see the matching numbered directories.
- 038–041: [initial two-phase and temporal multi-event workflow](two-phase-e2e-041/results.md), including live UI/render checks and selection metadata replay.
- 042–048: family scoring, denser-frame experiments, contrastive verification, [variance and consensus](variance-consensus-046-048/results.md).
- 049–051: [rules encoding](rules-encoding-049/results.md), [rules gate](rules-gate-050/results.md), [assist anchor](assist-anchor-051/results.md).
- 052–053: [routing analysis](routing-analysis-052/summary.json), [discovery-only experiment](discovery-only-053/results.md).
- 054: [source-golden expansion and dense windows](golden-expansion-054/results.md).
- 055: [100-window contiguous discovery sweep](proposer-sweep-055/results.md), current broadest live development sample.
- 056: [offline publication replay](publication-audit-056.json), explicit game identity and half-open windows; no new model calls.

Refer to [current status](../STATUS.md) for interpretation corrections, available budget and the sealed-holdout policy. Earlier entries below describe their own checkpoints.

---

## Commit/push checkpoint — 2026-09-13T00:56:24.665196+05:30

User authorized committing and pushing all pending project changes. Full pre-push suite:411 passed,4 skipped,1 final-holdout test deselected; one legacy Gemini SDK warning. Demo integration029, live UI030, failed three-clip031, successful six-clip032 and subsequent user render/approval feedback fixes included. User's own later render output verified89.5seconds; no claim its Chrome gate2 was visually inspected. Provider spend ledger $8.982478125; funded use $1.790183 of$2, remaining $0.209817. This is insufficient for another similar ~$0.53 full inference run within the current cap. No paid calls made for commit validation; do not reset ledger.

Code, recipes, tests, raw response/usage records and timestamped notes are included. Credentials, local source/render media, preview cache, runtime lock and working scratch remain excluded. Live server remains running; pushing does not redeploy/restart it. Existing historical “uncommitted” entries describe their original checkpoint and are superseded by this commit preparation.

---

## Latest: six-clip live demo 032 — 2026-09-13T00:24:02.826138+05:30

Fresh both-teams Gemini run on a continuous ten-minute development excerpt selected six non-overlapping clips and rendered an87-second reel in469.46s (~$0.534). Full app/agent diagram and both HITL video review gates restored at ?demo=full-flow; root and old live-demo URL route there. No saved classifications in live mode. 411 tests pass, actual six-player UI/MP4 checks pass. 031 only produced three clips; preserved. Read multiclip-live-032/results.md for evidence, scope, budget and launch state. Full-game accuracy remains unproven; holdout untouched.

---

## Latest: Live HITL demo 030 verified — 2026-09-12T23:59:15.148085+05:30

Fresh live Gemini analysis through actual UI selected a clip, paused for human video review, then rendered and displayed/downloaded the reel after approval. New /?demo=live-demo and root use fixed real 40-second source and dedicated recipe; advanced form at ?demo=live. Not a replay; not full-game accuracy validation. 31.99 seconds, $0.023884 incremental, funded use $0.320506/$2. See live-hitl-030/results.md and latest IMPLEMENTATION_NOTES. No holdout or sharing.

---

## Demo recovery — 2026-09-12T23:53:02.562026+05:30

Use ?demo=verified (also ?demo=recording) for explicitly labelled replay of the real 029 Gemini result with preview, approval and saved reel download; no inference. Generic live run again produced zero clips with different settings. Live recognition reliability is not resolved. See latest IMPLEMENTATION_NOTES.

---

## Approval UI update — 2026-09-12T23:45:39.646237+05:30

Gate 1 now includes per-clip source video previews and Keep controls; Gate 2 includes the final reel player and download. Empty selections and missing source/output block the corresponding approval. 38 focused UI tests pass; no additional inference or holdout access. See latest IMPLEMENTATION_NOTES and demo-integration-029/results.md. Running app reload required for the updated UI.

---

## Latest checkpoint — Demo 029 ready — 2026-09-12T23:43:06.544495+05:30

Live app now uses opt-in Gemini native video with a prefilled real 40-second East Bay excerpt. Production graph generated and verified a real 11.5-second MP4, score 0.66. Dedicated recipe retains minimum score 0.50. This known-action demo is not a new benchmark result; no holdout, YOLO or transcript used. 405 tests passed, 4 skipped, 1 holdout deselected; additional UI smoke passed and live form verified. Ledger $7.428182; funded usage $0.235887/$2. See evals/iterations/demo-integration-029/results.md and latest IMPLEMENTATION_NOTES for evidence and runtime requirements. App running at http://127.0.0.1:8501/?demo=ready; no automated evaluation scheduled.

---

# Latest020 entry

Updated 2026-09-12T21:51:35.991675+05:30:020tested YOLO11n+ByteTrack+track-augmented transcript+MiniCPM against shared visual transcript+MiniCPM, on3fully paired development windows(10references,9supported types). TP3→3,FP6→4,FN7→7;precision33.33%→42.86%,recall30%unchanged,microF1 31.58%→35.29%. Modest numerical gain,not reliable event recognition. Native tracking1023frames:only8observed ball-track frames,longest0.133s;no ball tracks in free-throw orCampus clips. All3TPs inCampus;none of7experimental predictions cited a track observation. Evidence errors remain. Local126.33s,peak0.4454GiB;9cloud calls20.83s,$0.28511increment,ledger$6.6463of$8.388tests passed,4skipped,1holdout-test deselected. No inference running,third dataset untouched. Read evals/iterations/track-transcript-020/results.md and plans/raw tracks/report, then latest IMPLEMENTATION_NOTES. Sustained ball tracking is the next unresolved prerequisite; no further experiment scheduled.

[020results](track-transcript-020/results.md) · [Tracking](track-transcript-020/tracking.json) · [Inference](track-transcript-020/report.json)

# Latest018/019 entries

Current checkpoint 2026-09-12T21:37:57.009084+05:30:018/019 complete with invalid windows. Corrected v2 rules,4fps source sequences and native rim crops tested.018:31calls,no paired valid windows.019:50calls,one paired window,both armsTP0/FP0/FN4. No demonstrated recognition gain. Mixed-view row duplication and continuing visual errors remain. Total incremental estimated$1.29907;ledger$6.36119of$8.388tests passed,4skipped,1holdout-test deselected. No inference running; third dataset untouched. Read evals/iterations/evidence-state-019/results.md first, then018/019plans/reports and latest IMPLEMENTATION_NOTES. Next decision is a separately frozen perception-component comparison, not another silent MiniCPM prompt retry. Original017code/results remain unchanged; new contract is src/hypereel/evaluation/ball_state_v2.py. No production integration or full court geometry.

- [018raw results](evidence-state-018/report.json)
- [019raw results](evidence-state-019/report.json)
- [Detailed results and call catalogue](evidence-state-019/results.md)

# Evaluation evidence catalogue

Updated 2026-09-12T21:12:53.512927+05:30. Entries below point to retained execution records; the append-only implementation notes and iteration histories contain decisions and per-call details. Earlier21 legacy cloud iterations remain in history.jsonl and iteration-log.md. No holdout files are included.

Latest: [state017 results](state-pilot-017/results.md), [plan](state-pilot-017/plan.json), [raw report](state-pilot-017/report.json), [re-derivation](state-pilot-017/reparse.json). Previous: [dense016 results](dense-pilot-016/results.md), [plan](dense-pilot-016/plan.json), [raw report](dense-pilot-016/report.json), [analysis](dense-pilot-016/analysis.json). Previous: [transcript015 results](transcript-pilot-015/results.md), [plan](transcript-pilot-015/plan.json), [raw report](transcript-pilot-015/report.json), [offline audit](transcript-pilot-015/observation-audit.json), [entailment audit](transcript-pilot-015/entailment-audit.json).

## Retained run records

- [evidence-pilot-013](evidence-pilot-013/report.json): start 2026-09-12T19:04:45.996339+05:30; end 2026-09-12T19:05:17.625268+05:30; status completed_with_arm_failures.
- [evidence-pilot-014](evidence-pilot-014/report.json): start 2026-09-12T19:09:34.336779+05:30; end 2026-09-12T19:10:34.865039+05:30; status completed_with_arm_failures.
- [nebius-matched-012](nebius-matched-012/report.json): start 2026-09-12T18:11:37.737212+05:30; end 2026-09-12T18:12:34.306345+05:30; status failed_or_interrupted.
- [ollama-all-events-009](ollama-all-events-009/report.json): start 2026-09-12T17:26:07.326233+05:30; end 2026-09-12T17:34:51.571464+05:30; status completed.
- [ollama-all-events-010](ollama-all-events-010/report.json): start 2026-09-12T17:34:57.001187+05:30; end 2026-09-12T17:47:50.410372+05:30; status completed.
- [ollama-all-events-011](ollama-all-events-011/report.json): start 2026-09-12T17:48:05.252927+05:30; end 2026-09-12T17:50:18.447607+05:30; status completed.
- [ollama-development-001.report.json](ollama-development-001.report.json): retained local execution/preflight/report record.
- [ollama-development-002-game1.aborted.json](ollama-development-002-game1.aborted.json): retained local execution/preflight/report record.
- [ollama-development-002-preflight.json](ollama-development-002-preflight.json): retained local execution/preflight/report record.
- [ollama-development-003-game1.execution.json](ollama-development-003-game1.execution.json): retained local execution/preflight/report record.
- [ollama-development-004-game1.execution.json](ollama-development-004-game1.execution.json): retained local execution/preflight/report record.
- [ollama-development-005-game1.execution.json](ollama-development-005-game1.execution.json): retained local execution/preflight/report record.
- [ollama-development-006-game1.execution.json](ollama-development-006-game1.execution.json): retained local execution/preflight/report record.
- [ollama-development-006-game1.frame-sampling.json](ollama-development-006-game1.frame-sampling.json): retained local execution/preflight/report record.
- [ollama-development-006-game1.observations.json](ollama-development-006-game1.observations.json): retained local execution/preflight/report record.
- [ollama-development-006-game1.report.json](ollama-development-006-game1.report.json): retained local execution/preflight/report record.
- [ollama-development-006-game2.execution.json](ollama-development-006-game2.execution.json): retained local execution/preflight/report record.
- [ollama-development-006-game2.frame-sampling.json](ollama-development-006-game2.frame-sampling.json): retained local execution/preflight/report record.
- [ollama-development-006-game2.observations.json](ollama-development-006-game2.observations.json): retained local execution/preflight/report record.
- [ollama-development-006-game2.report.json](ollama-development-006-game2.report.json): retained local execution/preflight/report record.
- [ollama-development-007-game1.execution.json](ollama-development-007-game1.execution.json): retained local execution/preflight/report record.
- [ollama-development-007-game1.frame-sampling.json](ollama-development-007-game1.frame-sampling.json): retained local execution/preflight/report record.
- [ollama-development-007-game1.observations.json](ollama-development-007-game1.observations.json): retained local execution/preflight/report record.
- [ollama-development-007-game1.report.json](ollama-development-007-game1.report.json): retained local execution/preflight/report record.
- [ollama-development-007-game2.execution.json](ollama-development-007-game2.execution.json): retained local execution/preflight/report record.
- [ollama-development-007-game2.frame-sampling.json](ollama-development-007-game2.frame-sampling.json): retained local execution/preflight/report record.
- [ollama-development-007-game2.observations.json](ollama-development-007-game2.observations.json): retained local execution/preflight/report record.
- [ollama-development-007-game2.report.json](ollama-development-007-game2.report.json): retained local execution/preflight/report record.
- [ollama-development-008-game1.execution.json](ollama-development-008-game1.execution.json): retained local execution/preflight/report record.
- [ollama-development-008-game1.frame-sampling.json](ollama-development-008-game1.frame-sampling.json): retained local execution/preflight/report record.
- [ollama-development-008-game1.observations.json](ollama-development-008-game1.observations.json): retained local execution/preflight/report record.
- [ollama-development-008-game1.report.json](ollama-development-008-game1.report.json): retained local execution/preflight/report record.
- [ollama-development-008-game2.execution.json](ollama-development-008-game2.execution.json): retained local execution/preflight/report record.
- [ollama-development-008-game2.frame-sampling.json](ollama-development-008-game2.frame-sampling.json): retained local execution/preflight/report record.
- [ollama-development-008-game2.observations.json](ollama-development-008-game2.observations.json): retained local execution/preflight/report record.
- [ollama-development-008-game2.report.json](ollama-development-008-game2.report.json): retained local execution/preflight/report record.
- [state-pilot-017](state-pilot-017/report.json): start 2026-09-12T21:08:21.590041+05:30; status completed_with_invalid_windows; 8/8 calls; derived 1 event after re-parse.
- [dense-pilot-016](dense-pilot-016/report.json): start 2026-09-12T20:52:23.928678+05:30; status completed_with_invalid_windows; 24/24 calls, extraction valid 4/8.
- [transcript-pilot-015](transcript-pilot-015/report.json): start 2026-09-12T19:46:51.779503+05:30; end 2026-09-12T19:47:12.041385+05:30; status completed_with_invalid_windows.

## Pilot015 implementation and checks

- Observation parser and extraction contract: ../../src/hypereel/evaluation/transcript.py
- Bounded runner: ../../scripts/run_transcript_pilot.py
- Offline boundary audit: ../../scripts/audit_transcript_pilot.py
- Offline entailment audit: ../../scripts/audit_transcript_entailment.py
- Shared boundary policy (both arms): check_window_span, partition_by_core, parse_window_events in ../../src/hypereel/evaluation/basketball_events.py; parse_window_extracted_events in ../../src/hypereel/evaluation/transcript.py
- Entailment rubric: ENTAILMENT_REQUIREMENTS, ENTAILMENT_CUES, entailment_elements, hedging_tokens in ../../src/hypereel/evaluation/transcript.py
- Tests: ../../tests/test_transcript.py
-363passed,4skipped,1holdout-test deselected (355 at the015 run, plus8 boundary-parity and rubric tests).
-Source/scorer/runner snapshots and per-call checkpoints live in transcript-pilot-015.
-Entailment gate replay of015: transcript-pilot-015/gate-replay.json via ../../scripts/replay_entailment_gate.py

## Pilot016 implementation and checks

- Frame preparation: ../../scripts/prepare_dense_pilot.py
- Bounded runner: ../../scripts/run_dense_pilot.py
- Offline like-for-like analysis: ../../scripts/analyze_dense_pilot.py
- Entailment recorded inline as a flag via screen_extracted_events; reject_unentailed is the opt-in strict mode and was NOT used in scoring.
-364passed,4skipped,1holdout-test deselected.
-report.json metrics.all_windows covers the four windows where BOTH arms completed, not all eight; see analysis.json naming_correction.

## Pilot017 implementation and checks

- Grounded derivation (model reports ball state, code derives events): ../../src/hypereel/evaluation/ball_state.py
- Bounded runner: ../../scripts/run_state_pilot.py
- Post-hoc re-derivation from retained raw text: ../../scripts/reparse_state_pilot.py
- Tests: ../../tests/test_ball_state.py (13 derivation tests; the only model-free stage in the track)
-378passed,4skipped,1holdout-test deselected.
-report.json holds the original strict outcome; reparse.json is labelled post-hoc and does not replace it.

- 2026-09-12T22:20:28.754710+05:30: gemini-pilot-021/plan.json — authorized comparison plan, awaiting API key; no Gemini results or spend.

### 2026-09-12T22:36:14.743400+05:30 — Gemini021/022

021: completed six requests, strict-invalid Markdown wrappers; secondary video F1.47059 vs historical MiniCPM.23077.022: JSON-mode integration first request valid; next request503,stopped. See gemini-pilot-021/results.md,reparse.json and gemini-confirmation-022/report.json. Cumulative ledger$6.753083187500001. Third dataset untouched.

### 2026-09-12T22:51:12.553566+05:30 — Gemini broader partial

023confirmationinterrupted503;024/027validvideo0–5,8references8types,TP3/FP4/FN5,F1.40. Dailyfreequota20exhausted;video6/7andimage2/6missing.025transcript/026image recovery preparednotrun. See gemini-development-summary/results.md;thirdsealed.

### 2026-09-12T23:08:05.527570+05:30 — Funded Gemini completion

028video6/7,026images2/6and025all8transcriptscomplete. Full12type directF1.37037,transcript.34783. Newspend$0.208809of$2cap. See gemini-funded-summary/results.md;thirdsealed.
