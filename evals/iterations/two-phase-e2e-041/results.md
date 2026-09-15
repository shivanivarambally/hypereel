# Temporal multi-event retest — 2026-09-15T19:54:00+05:30

## Outcome

Multi-event discovery helps candidate coverage, but the second pass has **not** demonstrated an accuracy improvement. Do not promote this opt-in feature as a better automatic detector yet.

Same fixed W1–W5 windows, six reviewed positive labels plus W3 negative; partial adjudication means precision is conditional, not full-game precision:

| Output | TP / FP / FN | Precision | Recall | F1 |
|---|---|---|---|---|
| Frozen original one-phase control (038) | 2 / 0 / 4 | 100% | 33.3% | 50.0% |
| Previous single-label two-phase (039) | 1 / 0 / 5 | 100% | 16.7% | 28.6% |
| New multi-event discovery (040) | 3 / 2 / 3 | 60.0% | 50.0% | 54.5% |
| New verified automatic events (040/041) | 2 / 2 / 4 | 50.0% | 33.3% | 40.0% |
| Confirmed + pending review (040/041) | 3 / 2 / 3 | 60.0% | 50.0% | 54.5% |

The last row measures retained candidates, **not human-finalized accuracy**. The multi-event discovery-to-verification comparison uses the same actual proposals and footage: verification removed one reviewed true positive into the review queue, removed neither scorable false positive, and corrected no labels. The original one-phase control uses a different, single-label contract; it is not a controlled ablation of phase count alone. Six positives are insufficient for generalized claims.

## Changes and iteration history

- **040, live:** native Gemini discovery enumerates multiple events, each with an ID, timestamp, evidence and optional team attribution. Verification checks all proposals in one second call and can correct a label for the same action. Unknown IDs, malformed/missing verification and incomplete evidence cannot silently confirm proposals. Original labels/times remain attached. Thirteen live video calls on seven development windows; no provider errors.
- **041, offline replay:** replayed exactly the 040 inference after fixing overlapping-clip selection to retain all confirmed event annotations contained in the chosen footage. The 040 selected-clip metadata scored F1 22.2% because it retained only a primary label. The 041 selected event metadata scores F1 40.0%, matching confirmed detection. This is a bookkeeping repair, **not new model accuracy**. No new vision calls.
- Contextual review clips now carry event timestamp/ID/team alongside the uncertainty reason. The original proposal windows remain in graph state. Legacy single-label APIs and default-off behavior are preserved.

## Evidence and remaining failures

- W2 now captures both the reviewed steal and basket with anchors at source 761.5s and 766.0s. A turnover is additionally predicted but remains unadjudicated, so it receives no accuracy credit.
- W1 predicts a two-point miss, conflicting with the reviewed free-throw make. W4 predicts a made free throw, conflicting with the reviewed miss. The verifier confidently agrees with both discoveries; repeated agreement is not independent grounding evidence.
- W5 keeps a generic-compatible missed attempt as potential, flags foul/occlusion ambiguity for expert review, and omits the reviewed block.
- W6 emits a fuller sequence but its team/possession account conflicts with human narration. Its home/away aliases are not validated team mappings. W7 still over-specifies shot value despite the human reference leaving it unknown. Both remain outside the primary numeric score.
- The separate interval audit reports the same counts at 0/2/5-second slack around approximate human intervals. This demonstrates interval consistency for matched labels, not exact timestamp accuracy or visual proof. No baseline timing comparison is possible because the frozen control lacks event anchors.

## Execution and cost

Full regression: **442 passed, 4 skipped, 1 final-holdout test deselected**. Actual Streamlit/graph continuations passed selection, local approval, rendering, share-gate pause and download checks: W2 rendered 15 seconds with all three model event records preserved; W5 rendered 8 seconds after a **simulated** correction to generic missed field goal. That simulated review never changes gold data or earns metric credit. Nothing published.

These are end-to-end continuations from fixed, live-classified short clips, **not** full-video ingestion/proposal-recall evaluations. W2 `ui-e2e.json` originally says “fresh 041”; the correct inference provenance is **live 040, replayed in 041**, as recorded in `report.json`. The later W5 UI artifact uses that corrected wording. Existing raw artifacts were retained.

Additional estimated spend this turn: **$0.14822775** = $0.14453925 across 13 video calls + $0.0036885 across 5 judge/summary calls. All 18 calls completed. Cumulative ledger **$9.693852375** of **$11.192294875** authorized ceiling; remaining **$1.4984425**. No ceiling increase or ledger reset. UI text usage records remain under `../demo-integration-029/`; video records are under `../two-phase-e2e-040/provider-calls/`.

## Next steps

1. Independently check the exact cached media and reference alignment for W1/W4 and the team/possession sequence in W6. Preserve disagreements; do not revise gold merely to agree with the model.
2. Test an independent evidence-first verification strategy, with explicit visible outcome/possession observations and normalized team identities, against these frozen cases. Same-model confirmation currently repeats errors. Do not add a third “expert” model pass without evidence that it improves the measured tradeoff.
3. Keep uncertainty review enabled, add cross-window event deduplication, and propagate all event labels into narrative summaries (currently they emphasize the primary clip label).
4. Expand adjudicated development coverage and measure proposer recall before a first-game full run. Keep the third-game final holdout sealed until the development policy is frozen.

Machine-readable evidence: [metrics](metrics.json), [temporal support](temporal-support.json), [replayed outputs](report.json), [original live outputs](../two-phase-e2e-040/report.json), [render check](ui-e2e.json), [review check](ui-potential-e2e.json). No commit/push in this turn.
