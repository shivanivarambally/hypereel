## Latest checkpoint — Funded Gemini tests complete 2026-09-12T23:08:05.527570+05:30

Read evals/iterations/gemini-funded-summary/results.md,confirmation.json,and latest IMPLEMENTATION_NOTES. All8developmentwindows14references12types complete via successful024/027/028video calls. DirectGeminiTP5/FP8/FN9,F1.37037 vs MiniCPMTP3/FP31/FN11,F1.125.025transcript8/8valid,TP4/FP5/FN10,F1.34783;moreprecision,lessrecall.026missingimage2/6valid;staged3windowconfirmationcomplete. NoYOLOadded,noholdoutused. Newfundedspend$0.208809of$2cap,remaining$1.791191;reserve$3ofuserreported$5creditfordemo. Historicalledger$7.401104;neverreset.400tests pass,4skip,1holdouttestdeselected. No inference running/scheduled. Keep directGeminibaseline;defertranscript/genericYOLO. Nextrecommended experiment audits longercontext/shotoutcomevisibility with frozen scoring. Olderquota/partialstatuses below superseded.

---

## Funded continuation — 2026-09-12T23:02:35.564073+05:30

User reports$5Google funding; cap newevaluationat$2,reserve$3for demo. Policy:evals/iterations/gemini-funded-budget.json; fixed baseline$7.192294875,cumulativeceiling$9.192294875,noreset. Budget enforced before everyrequest/retry. Twelve focused checks pass.028video6/7and026images2/6next;025transcriptprepared. Older dailyquota/$8notes below are historical; paidgeneration availability still toverify by nextauthorizedcall.

---

## Latest checkpoint — Gemini quota blocked 2026-09-12T22:51:12.553566+05:30

Read evals/iterations/gemini-development-summary/results.md and report.json, then latest IMPLEMENTATION_NOTES.023confirmationpartial;024/027combined strict-valid video0–5cover8references8types:GeminiTP3/FP4/FN5,P42.86%,R37.5%,F1.40;matched historicalMiniCPMTP1/FP25/FN7,F1.05882. Video6/7missing,so all12categoryevaluationNOTcomplete. Image2/6confirmationmissing. GoogleHTTP429dailyquota20/model/project exhausted; do not retryshortRetryInfo or change keys toreset. Need paidquotaor dailyreset(midnightPacific;Sep13 12:30PMIST). No inference running/scheduled. Ledger$7.192295/$8includesunknownusage reservations.025transcriptscript/planprepared,unrun;026missing-imageplanprepared,unrun. New retryhandler stopsdailyquota. GenericYOLOdeferred based020fragmentedballtracks. Third dataset remains sealed. Earlier statuses below are historical.

---

## Latest checkpoint — Gemini021/022 2026-09-12T22:36:14.743400+05:30

Read evals/iterations/gemini-pilot-021/results.md and latest IMPLEMENTATION_NOTES.md.021sixcalls complete but strict JSON rejects Markdown fences; separate formatting-only reparse shows videoTP4/FP3/FN6,F1.47059 vs cached same-subset MiniCPMTP3/FP13/FN7,F1.23077. ImagesTP2/FP0/FN8,F1.33333.022JSON output mode first call valid,secondHTTP503high demand; stopped with no paired confirmation score. No inference running or scheduled. Ledger$6.753083/$8 includes unknown-usage reservation. Third dataset sealed. Next: separately logged capacity recovery/JSON confirmation, then broader eight-window/all12type test if improvement holds. No production architecture shift. Earlier statuses below are historical.

---

## Gemini021 access update — 2026-09-12T22:28:18.664203+05:30

API key is now configured and authenticated models listing succeeded. No further user prerequisite currently identified. Next: implement diagnostic adapter, freeze model/rates and bounded request settings, then run authorized six-request pilot. Generation quota remains untested; no Gemini inference or spend yet. See gemini-pilot-021/plan.json and latest IMPLEMENTATION_NOTES.md. This supersedes the awaiting-key checkpoint below.

---

## Latest checkpoint — Gemini pilot021 planned, awaiting API key

Updated 2026-09-12T22:20:28.754710+05:30. User authorized a Gemini comparison. API key absent; current SDK absent; no Gemini inference or spend. Plan:6requests,3existing development windows, same-image Gemini vs historical MiniCPM control and continuous-video Gemini at target4fps. Freeze accessible model/rates/settings before calls. Remaining estimated budget$1.3537 under cumulative$8. All12event types retained,9supported by this subset; third dataset sealed. Read evals/iterations/gemini-pilot-021/plan.json and latest IMPLEMENTATION_NOTES.md. Next prerequisite: GEMINI_API_KEY stored locally in repository .env; agent handles adapter/setup. Earlier recommendations are historical, superseded by this authorized pilot.

---

## Latest checkpoint — YOLO/ByteTrack transcript pilot020

Updated 2026-09-12T21:51:35.991675+05:30:020tested YOLO11n+ByteTrack+track-augmented transcript+MiniCPM against shared visual transcript+MiniCPM, on3fully paired development windows(10references,9supported types). TP3→3,FP6→4,FN7→7;precision33.33%→42.86%,recall30%unchanged,microF1 31.58%→35.29%. Modest numerical gain,not reliable event recognition. Native tracking1023frames:only8observed ball-track frames,longest0.133s;no ball tracks in free-throw orCampus clips. All3TPs inCampus;none of7experimental predictions cited a track observation. Evidence errors remain. Local126.33s,peak0.4454GiB;9cloud calls20.83s,$0.28511increment,ledger$6.6463of$8.388tests passed,4skipped,1holdout-test deselected. No inference running,third dataset untouched. Read evals/iterations/track-transcript-020/results.md and plans/raw tracks/report, then latest IMPLEMENTATION_NOTES. Sustained ball tracking is the next unresolved prerequisite; no further experiment scheduled.

Earlier next-action statements below are historical.

---

## Latest continuation —018/019

Current checkpoint 2026-09-12T21:37:57.009084+05:30:018/019 complete with invalid windows. Corrected v2 rules,4fps source sequences and native rim crops tested.018:31calls,no paired valid windows.019:50calls,one paired window,both armsTP0/FP0/FN4. No demonstrated recognition gain. Mixed-view row duplication and continuing visual errors remain. Total incremental estimated$1.29907;ledger$6.36119of$8.388tests passed,4skipped,1holdout-test deselected. No inference running; third dataset untouched. Read evals/iterations/evidence-state-019/results.md first, then018/019plans/reports and latest IMPLEMENTATION_NOTES. Next decision is a separately frozen perception-component comparison, not another silent MiniCPM prompt retry. Original017code/results remain unchanged; new contract is src/hypereel/evaluation/ball_state_v2.py. No production integration or full court geometry.

Older next-action statements below are historical and superseded by this checkpoint and the latest user authorization.

---

## Agent starting point — updated 2026-09-12T21:13:24.038011+05:30

Read this first. Everything below is historical and contains superseded next-action statements.

### Status

The development evaluation track is concluded at pilot017. No inference is running or scheduled. Ledger $5.06212 of the $8 ceiling the owner authorized; never reset. Third dataset never inspected. Nothing committed.

### What017 changed and found

Owner asked for an architectural recommendation, implemented and tested. The016 diagnosis was that the model asserts outcomes it has not seen and the scorer cannot tell an assertion from an observation. 017 removes the opportunity rather than instructing against it: the model reports per-frame ball state from a closed vocabulary (held, in_flight, rim_contact, through_net, deflected, loose, not_visible) and events are derived deterministically in src/hypereel/evaluation/ball_state.py. Identical frames to016, same model and decoding, same references and matcher; only the output contract changed.

**Derived TP0/FP1/FN14, microF1 0**, against dense016 direct .12698 and sparse013 direct .125. The score fell to zero.

The reason is the result. Across48 frames the model reported held24, loose20, in_flight3, through_net ONCE, rim_contact ZERO. Team identifiable in15 of48 frames, court zone unknown in13. Eight windows containing five shot-outcome references produced not one observed rim contact. Constrained to report only what is visible, this model does not report shot outcomes. Every made and missed shot scored in009 through016 was asserted, not observed — previously an audit inference, now measured.

One derived event, and it is the sharpest signal available: window1 reference free_throw_made@225; model reported through_net at229.4 with court_zone beyond_arc, so the derivation typed three_point_made and scored a false positive. Outcome seen correctly, shot type wrong. With the right zone it matches inside tolerance. One case in fourteen; do not generalise from it.

Kept regardless of score: zero contradictory label pairs by construction against26 in016's direct arm; zero scoreboard-derived events since the scoreboard is not in the vocabulary;13 unit tests over the only stage in this project verifiable without a model; every non-emission recorded as a derivation note so lost recall stays visible.

### Conclusion

Grounding removes fabrication and removes the score with it, because the perception layer cannot supply the primitive every scored event depends on: a visible shot outcome. Best measured results anywhere are microF1 .25 direct and .50 to .60 on a two-window transcript subset, both shown ungrounded by the entailment audit; the honest grounded score is 0, against gates of .70 on precision, recall and F1. Four distinct changes have now hit the same wall: transcripts015, detector crops013/014, denser frames016, grounded derivation017.

**Do not propose another prompt, representation or scoring change over six768px frames of720p broadcast footage.** What would be needed is a change to the evidence: rim-region frames at much higher effective resolution so through-net and rim contact are resolvable at all; sampling dense enough around a release to contain the outcome, which at this provider's six-image limit means far shorter windows, not denser eight-second ones; and a court-zone signal from geometry rather than from the same model that misread a free throw as beyond the arc. Those are data and instrumentation changes. **None is started and none is authorized by this section.**

### Read next, in order

1. evals/iterations/state-pilot-017/results.md then reparse.json — the017 result, state distribution and the single derived event.
2. evals/iterations/dense-pilot-016/results.md and analysis.json — the density result and the hedging measurement.
3. evals/STATUS.md, then the newest entries in evals/IMPLEMENTATION_NOTES.md.
4. evals/iterations/transcript-pilot-015/ — entailment-audit.json, gate-replay.json, observation-audit.json. All unchanged.
5. evals/iterations/CATALOGUE.md, iteration-log.md, all-events-history.jsonl.

Code: ball_state.py (state vocabulary, parser, derivation, contradictory_pairs); shared boundary policy check_window_span/partition_by_core/parse_window_events in basketball_events.py and parse_window_extracted_events in transcript.py; entailment rubric with screen_extracted_events/reject_unentailed in transcript.py. Scripts prepare_dense_pilot.py, run_dense_pilot.py, analyze_dense_pilot.py, run_state_pilot.py, reparse_state_pilot.py, audit_transcript_entailment.py, replay_entailment_gate.py. Tests378 passed,4 skipped,1 final_holdout deselected; git diff --check clean.

### Standing boundaries

Never inspect or evaluate the third golden dataset. Never expose reference labels to prediction generation. Never alter HoopIQ labels or times. Never overwrite an existing report; record corrections rather than applying them silently, as017's post-hoc parser change and016's metric naming correction both are. reject_unentailed must never be enabled in one arm of a comparison alone or applied after seeing scores. No full-game evaluation, production architecture adoption, rendering, external upload or deployment is authorized.

---

## Agent starting point — updated 2026-09-12T20:58:58.907711+05:30

Read this current section first. Everything below is historical and contains superseded next-action statements.

### Status

The development evaluation track reached a conclusion at pilot016. No further inference is running or scheduled. Owner raised the cumulative ceiling from $5 to $8; ledger stands at $4.88544 and was never reset. Third dataset never inspected. Nothing committed.

### What016 tested and found

016 tested the one hypothesis the015 audit pointed at: that sparse evidence, not the output representation, was binding. Single declared change, frame spacing 2.4s across12s to 1.6s across the8s core, everything else fixed, both arms sharing one boundary policy from the outset. Declared confound: at the six-image provider limit density and span cannot be varied independently.

**Not supported.** Direct arm across all8 windows,14 references: microF1 .125 to .12698, precision and macroF1 falling, predictions34 to49. Both arms on windows1 and6: direct .16667 to .25, transcript .60 DOWN to .50. Extraction validity fell to4/8. Entailment fell to0 of20 screened events, against2 of8 in015.

The recall gain is hedging, measured not asserted. Dense016 direct emitted26 mutually exclusive label pairs across5 windows against sparse013's3 across2. One-to-one same-label matching credits whichever member of a made/miss pair is correct and charges the other a single false positive. Window0, which carries no annotations, emitted all four exclusive pairs at one timestamp. Do not read the recall rise as recognition.

Density did fix the window1 narration error015 recorded: what015 called a player in black near the three-point line is a free-throw setup, and016 narrates it correctly. Perception improves with denser frames; grounded extraction does not.

### Sample-size warning that applies to every earlier comparison in this log

015's primary paired figure was .40 on windows[2,6]. The identical retained output scores .60 on windows[1,6]. Window choice moves the headline more than any treatment tested. Treat every per-iteration delta in history.jsonl, all-events-history.jsonl and iteration-log.md accordingly.

### Conclusion

Iterations009 to016 do not produce reliable basketball event recognition, and the failure is localised: the model asserts outcomes and possession its own evidence does not contain, and the scorer cannot distinguish an assertion from an observation. Best measured result is microF1 .25 on the direct arm and .50 to .60 on a two-window transcript subset, against gates requiring precision, recall and F1 each at least .70; the grounded score, counting only events whose cited evidence supports them, is 0. Three representation changes have now failed (transcripts in015, detector crops in013/014, denser frames in016), consistent with assertion-under-uncertainty being primary rather than evidence sparsity.

Closing the gap needs architecture, not prompts: a detector that must ground an outcome in a visible event rather than being asked not to guess; a scorer that penalises mutually exclusive predictions for one action instead of rewarding whichever lands; and audited action timings so a five-second point tolerance is not doing the work. **None of this is started, and none is authorized by this section.**

### Read next, in order

1. evals/iterations/dense-pilot-016/results.md then analysis.json — the016 result, like-for-like comparisons, hedging counts and the naming correction.
2. evals/STATUS.md — current checkpoint.
3. evals/IMPLEMENTATION_NOTES.md — newest entries carry the full reasoning and the running per-call log.
4. evals/iterations/transcript-pilot-015/ — entailment-audit.json, gate-replay.json, observation-audit.json, results.md, report.json. All unchanged.
5. evals/iterations/CATALOGUE.md, iteration-log.md, all-events-history.jsonl.

Code: shared boundary policy check_window_span/partition_by_core/parse_window_events in src/hypereel/evaluation/basketball_events.py and parse_window_extracted_events in transcript.py; entailment rubric and screen_extracted_events/reject_unentailed in transcript.py; scripts prepare_dense_pilot.py, run_dense_pilot.py, analyze_dense_pilot.py, audit_transcript_entailment.py, replay_entailment_gate.py. Tests364 passed,4 skipped,1 final_holdout deselected; git diff --check clean.

### Standing boundaries

Never inspect or evaluate the third golden dataset. Never expose reference labels to prediction generation. Never alter HoopIQ labels or times. Never overwrite an existing report; record corrections rather than applying them silently. Keep every step timestamped in IMPLEMENTATION_NOTES.md. reject_unentailed must never be enabled in one arm of a comparison alone or applied after seeing scores. No full-game evaluation, production architecture adoption, rendering, external upload or deployment is authorized.

---

## Agent starting point — updated 2026-09-12T20:34:35.595700+05:30

Read this current section first. Sections below are historical and may contain superseded next-action statements. The two prerequisites the previous section named are now discharged; its scope, budget and evidence-integrity boundaries still apply in full.

### What changed since the previous section

Offline work only. No provider call, no spend, no holdout access, no new iteration number. Ledger remains $4.33608 of $5. report.json and observation-audit.json verified byte-identical before and after (report.json sha256 236ee0f70cef981c41676654cfbf318f21f81f1aafe2f41cba21fe3688c88292). No HoopIQ label or timestamp altered, no existing report overwritten, no unrelated working-tree change touched, nothing committed.

**Boundary parity is now enforced in shared library code.** The015 defect was in the callers, not the parser. run_transcript_pilot.py:91 validated direct output over the supplied image span and filtered to core; line102 validated extraction over core and raised, so one out-of-range event discarded the whole window. Window1 left paired coverage because extraction emitted233.0s, itself a supplied frame timestamp the direct arm would have accepted and filtered; window2 direct emitted two_point_made at766.0, equally out of core, and kept its window. Added check_window_span, partition_by_core and parse_window_events to basketball_events.py, and the symmetric parse_window_extracted_events to transcript.py. Nothing was loosened: the strict parsers keep their signatures and are pinned by their own test. run_transcript_pilot.py is deliberately unmodified and its snapshot stays byte-identical.

**Entailment is now a measured axis.** Re-parsing retained raw extraction text under parity recovers window1, so the audit covers19 events across all three windows (11 direct,8 transcript), not the6 the original parser accepted. Transcript:1 entailed,7 unsupported. Direct:0 entailed,3 asserted,8 unsupported, of which5 infer a basket from the scoreboard against explicit instruction, twice citing an unchanged 7-0 score for further baskets. The transcript arm extracted two mutually exclusive rebound labels from one identical observation at one timestamp.

### Result interpretation, and what must not be claimed

Under parity the arms produce5 label/time matches (direct2, transcript3). **None is entailed.** Four are unsupported, one merely asserted. Every one of the transcript arm's3 matches rests on evidence that does not establish the event it claims. The015 numerical lift remains real as a label/time measurement and remains recorded unchanged; it is not evidentially grounded. Do not describe015 or this audit as demonstrating improved recognition.

Label/time scoring under parity reproduces observation-audit.json exactly (direct TP2/FP8/FN8 microF1 0.20; transcript TP3/FP4/FN7 microF1 0.35294), independently confirming the parity implementation. Primary paired_metrics are untouched and unrestated. The entailment-gated numbers (transcript keeps1 of7, TP0/FP1/FN10, microF1 0; direct keeps3 of10 at a weaker asserted bar, TP1/FP2/FN9, microF1 0.15385) are a clearly labelled SECONDARY diagnostic. They lower both arms, were not used to select or remove anything from the primary result, and are gated at non-equivalent bars because direct events cite no frozen text. Never present them as a clean paired comparison or substitute them into any report.

Treat three axes as separate and never collapse them: observation accuracy, entailment of an event by its cited evidence, and label/time matching. The single entailed transcript event, window1 two_point_miss at228.2s, proves why: the015 contact sheet shows that window is a free-throw setup narrated as a shot near the three-point line, so it is a faithful extraction from a false narration. A valid citation, an entailed event and high model confidence each establish nothing about correctness. Every unsupported transcript event carries confidence1.0.

The lexical screen in ENTAILMENT_CUES is deliberately over-permissive and is NOT a verdict. A missing element is strong evidence against entailment; a found element is not evidence for it. Screen and auditor disagreed on5 direct and1 transcript event, in both directions. Auditor verdicts are agent inspection of frozen text held in an explicit keyed table, not independent human reannotation.

### Read next, in order

1. evals/iterations/transcript-pilot-015/entailment-audit.json — per-event entailment rows, observation hedging table, match cross-tab, parity metrics and the gated diagnostic.
2. evals/IMPLEMENTATION_NOTES.md — the two newest timestamped entries carry the full reasoning; older entries below them.
3. evals/STATUS.md — current checkpoint.
4. evals/iterations/transcript-pilot-015/results.md, observation-audit.json, plan.json, report.json — the frozen015 run, unchanged.
5. evals/iterations/CATALOGUE.md, iteration-log.md, all-events-history.jsonl — navigation and history.

Code: src/hypereel/evaluation/basketball_events.py (check_window_span, partition_by_core, parse_window_events, score_events); src/hypereel/evaluation/transcript.py (parse_window_extracted_events, ENTAILMENT_REQUIREMENTS, ENTAILMENT_CUES, entailment_elements, hedging_tokens); scripts/audit_transcript_entailment.py; tests/test_transcript.py. Tests:363 passed,4 skipped,1 final_holdout test deselected; git diff --check clean. The parity guard was verified red by reverting the transcript-side bounds, not assumed. Reproduce the audit with `.venv/bin/python scripts/audit_transcript_entailment.py`; it re-derives everything from report.json and writes only entailment-audit.json.

### Next decision

A larger fixed development comparison can now test whether the transcript numerical gain repeats, because both arms share one boundary policy from the outset. Any such run must record entailment and observation accuracy during execution rather than as a post-hoc audit, keep event definitions, references and the five-second one-to-one matcher frozen, and predeclare its plan before inference. Richer temporal evidence or a different visual model are separately declared changes, not silent additions to the transcript ablation. Do not raise event limits, discard unmatched predictions, or filter on entailment to improve a reported score.

Unchanged and non-negotiable: never inspect or evaluate the third golden dataset; never expose reference labels to prediction generation; never alter HoopIQ labels or times; never overwrite existing reports or commit unrelated working-tree changes; keep every step timestamped in IMPLEMENTATION_NOTES.md. No live run is running or scheduled. No full-game evaluation, production architecture adoption, external upload or deployment is authorized.

---

## Agent starting point — updated 2026-09-12T19:59:37.946110+05:30

Read this current section first. Historical checkpoints below preserve previous decisions and may contain superseded instructions.

### Latest user clarification and result interpretation

Iteration015 did NOT combine YOLO, Qwen and transcripts. It compared hosted openbmb/MiniCPM-V-4_5 in two workflows: identical six frames → direct events; identical six frames → observation transcript → a second, text-only MiniCPM call → events. No local Qwen or YOLO was involved in015. Earlier013/014 tested generic YOLO crops, not continuous tracking.

On two valid common windows (nine reference events), direct produced TP2/FP6/FN7 versus transcript TP3/FP3/FN6. Precision25%→50%, recall22.22%→33.33%, microF1 23.53%→40%. This is a real numerical improvement: one extra reference match and three fewer unmatched predictions. Do not dismiss it, and do not describe it as demonstrated dramatic or reliable recognition improvement. It is a small diagnostic sample. The third transcript extraction violated core timestamp bounds; primary paired results exclude it. Separate post-hoc boundary-consistent results are retained in the audit, not substituted into the primary report.

Observation audit found narration errors and extraction of confirmed misses/rebounds from descriptions that did not establish an outcome or possession. A label/time match can pass the scorer despite unsupported evidence. All3 transcript matches were in the campus window. All6 accepted extraction events had confidence1.0, which is not validated accuracy. Transcript remains promising as an intermediate representation and diagnostic tool, but reliable semantic improvement is unproven.

### User intent and non-negotiable boundaries

Improve all basketball events, including shots made/missed, free throws, assists, blocks, steals, turnovers, offensive and defensive rebounds. User confirmed supplied labels originate from specialist HoopIQ. Use existing development labels as references; do not require the user to create an audited benchmark. Never expose reference labels to prediction generation or silently alter them to improve results. Preserve uncertainty about exact action timing.

NEVER inspect or evaluate the third golden dataset: reserved for the final run. Work only with the two development games. Every implementation, experiment, failure, observation and decision needs a timestamped entry in IMPLEMENTATION_NOTES.md and the relevant iteration history. Preserve raw outputs and failed iterations. Do not overwrite existing reports or commit unrelated working-tree changes. The repository contains substantial uncommitted work.

The user authorized bounded experiments and subsequently requested documentation. No further live run is currently running or scheduled. Existing cumulative cloud estimate is$4.33608 of$5; do not reset the ledger or exceed the ceiling. Figures are conservative accounting estimates, not invoices. Warning-level memory pressure alone is not a stop condition; actual failures and budget limits remain relevant. No full-game evaluation, production architecture adoption, external upload or deployment is authorized by this documentation update.

### Read next, in order

1. evals/iterations/transcript-pilot-015/results.md — complete latest result, readable transcripts, per-type scores and timestamped call catalogue.
2. evals/iterations/transcript-pilot-015/observation-audit.json — visual/text audit and explicitly post-hoc boundary sensitivity.
3. evals/iterations/transcript-pilot-015/plan.json and report.json — frozen plan, exact inputs/prompts, raw responses, usage and primary metrics.
4. evals/IMPLEMENTATION_NOTES.md — cumulative timestamped implementation and interpretation record; newest entries at the end.
5. evals/iterations/CATALOGUE.md, iteration-log.md and all-events-history.jsonl — navigation and historical experiments; history.jsonl retains legacy iterations.
6. evals/STATUS.md and evals/iterations/spend-ledger.json — current checkpoint and budget.

Paths above are relative to repository root: /Users/shivani/code/AgentAICourse/week3/hypereel.

### Implementation and next decision

Latest code: src/hypereel/evaluation/transcript.py; scripts/run_transcript_pilot.py; scripts/audit_transcript_pilot.py; tests/test_transcript.py. Executed snapshots live in the015 folder. Tests:355passed,4skipped,1final_holdout test deselected; git diff --check passed. No production architecture integration.

Before a follow-up comparison, make core/context boundary handling identical between arms. Separately assess whether extracted events are actually entailed by frozen transcripts, and whether narration reflects visible action. Maintain existing label/time scores alongside evidence-quality observations; never retroactively remove unsupported predictions to inflate primary results. A subsequent larger, fixed development comparison can test whether the numerical gain repeats. Richer temporal evidence or another model would be separately declared changes, not silently folded into the transcript ablation. Do not claim015 tested native continuous video: inputs were six768pixel-wide frames,2.4seconds apart, spanning12seconds including context.

---

## Current checkpoint — transcript pilot015

Transcript pilot015 completed at 2026-09-12T19:47:12.041385+05:30; final audit recorded 2026-09-12T19:50:21.866669+05:30.

User identifies HoopIQ as the specialist source of the supplied golden labels. No replacement specialist or new user annotation was required. Tested fresh direct detection against observation-only visual narration followed by text-only event extraction, using the same Nebius MiniCPM-V-4_5 for all stages. Three frozen development windows [1,2,6],10 references across9 supported types, all12 event definitions available. Identical6frame JPEG sequences per visual arm,768pixel wide,2.4second gaps across12seconds including2seconds context either side. This isolates representation change on sparse evidence; it is not continuous-video transcription or speech recognition. No references entered model prompts. Third dataset untouched.

Nine of nine provider calls returned completed output in 20.26s; no provider crash, timeout or retry. All3 narrations parsed, all3 direct results parsed,2of3 extraction outputs passed the original strict core-time validation. Window1 emitted an event at233s outside223–231, so that whole transcript result was excluded from primary paired metrics. All raw outputs, input hashes, prompts, observation IDs, per-call timestamps, latencies, usage and memory/pressure checkpoints are preserved. Per-call raw text and parsed window outputs were appended to IMPLEMENTATION_NOTES during execution.

Primary matched coverage: windows2and6,9 references across8 supported types. Direct TP2/FP6/FN7,precision25%,recall22.22%,microF1 23.53%,macroF1 10%. Transcript TP3/FP3/FN6,precision50%,recall33.33%,microF1 40%,macroF1 25%. Unmeasured categories must not be described as passing. Available-only full direct metrics use3windows and cannot be directly compared with2window transcript metrics.

Audit identified asymmetric boundary handling: direct accepted observed context then filtered; extraction required core bounds. Retained original report unchanged. A separately labeled post-hoc offline sensitivity applies direct's context/filter policy to retained extraction outputs acrossall3windows: direct TP2/FP8/FN8,P20%,R20%,F1 20%;transcript TP3/FP4/FN7,P42.86%,R30%,F1 35.29%. No fresh inference or reference changes. Future paired runner must apply identical boundary policy from the outset.

The numerical lift is not established semantic improvement. All6 accepted transcript events cite observations that do not establish their claimed miss or possession outcome. All3 matches are in campus window6. All6 accepted events haveconfidence1.0. All18 narrator rows say visibility=clear despite several descriptions explicitly stating uncertainty. Contact-sheet inspection found clear visual errors: free-throw setup mislabeled as a shot near the three-point line; midcourt ball handling narrated as a shot towards the basket. Full qualitative audit is in observation-audit.json. This audit is agent inspection, not independent human reannotation; original HoopIQ labels/times remain unchanged.

Implementation: added evaluation/transcript.py for timestamp-anchored observations, text-only extraction and valid observation-ID checks; scripts/run_transcript_pilot.py for bounded paired inference and live notes; scripts/audit_transcript_pilot.py for reproducible offline sensitivity. Citation validation establishes ID existence, not factual entailment. No semantic filter was retroactively used to boost scores. Production application architecture unchanged.

Tests:355 passed,4 skipped,1 final_holdout test deselected; no holdout evaluation. Three new tests cover time anchoring/order, paired events, invented citations and empty-transcript evidence. Spend estimateincrement$0.18957,ledger cumulative$4.33608 against$5 ceiling; historical conservative estimates,not invoice prices. No inference remains running.

Decision: retain the transcript and evidence-link format as a diagnostic tool; do not adopt this MiniCPM narration/extraction combination as a reliable detector. Both visual narration and text-to-event reasoning failed. Next refinement should first enforce common boundary handling and evaluate extraction entailment on these frozen transcripts, then test visual narration with genuinely richer temporal evidence or a better visual model under a separately frozen comparison. Treat observation accuracy and event matching separately; do not equate a valid citation or high model confidence with correctness. No new architecture switch or paid run was started after this audit.

---

Earlier checkpoints below are historical.

## Current checkpoint — bounded pilot013/014 completed (2026-09-12)

Bounded pilot 013/014 finished with arm failures; no production architecture adoption.

User authorization to run this pilot superseded the earlier analysis-only pause. Used Nebius MiniCPM-V-4_5 consistently across input arms and local YOLO11n COCO for optional ball crops. The two development games, original eight core windows, 14 reference events, 12 category definitions and five-second one-to-one matcher remained frozen. Third dataset untouched.

013: six wide frames plus context completed 8/8 windows: TP3/FP31/FN11, precision8.82%, recall21.43%, microF1 12.50%, macroF1 4.71%. Twelve-image and crop requests each failed on first request with BadRequestError; exact error body was not retained, so the exact provider limit is unknown. These arms have no valid semantic result.

014: predeclared compatibility change packed the same12 timestamps into six two-row sheets, equal canvas in dense/crop arms. Dense arm returned20events against the maximum12 and stopped at0/8 valid. Crop arm completed3/8 windows then returned20events and stopped: partial TP1/FP21/FN4, precision4.55%, recall20%, microF1 7.41%. Both schema failures had finish_reason=stop, not output truncation. Raw responses preserved; no relaxed validation or automatic retries. No planned identical-input reuse actually occurred. No common completed dense/crop window exists, so there is NO valid paired estimate of YOLO benefit. Differences from013 also confound packing and coverage.

YOLO produced ball candidates in6/96 sampled frames (only two windows; none for campus). This is candidate frequency, not audited ball recall. Detector preparation22.33s, sampled peak process RSS0.410GiB. No observed machine crash. Cloud client RSS is not hosted model memory. Repeated frame-level shot/rebound stories and scoreboard-based explanations remain a grounding/event-identity failure despite explicit instructions; greater visible detail alone did not establish reliable event recognition.

Actual15 cloud attempts across both iterations. Conservative ledger increment$1.20313 includes$0.60 reserved for two rejected requests with unknown usage; cumulative$4.14651 of$5. These are estimates, not invoice charges. No further inference is running or scheduled. New isolated detector environment, preparation/runner scripts, frame manifests/hashes, boxes, memory checkpoints, raw responses, usage and failure audits retained. Production application unchanged.

Validation:352 tests passed,4 skipped,1 final_holdout test deselected. Do not treat failed/unattempted windows as zero-event successes. Existing labels and provisional timing are best-effort evidence, not an audited benchmark; annotation-empty controls are not verified negatives.

Decision: do not adopt the generic YOLO crop pipeline based on this pilot. The next bounded refinement should first validate provider-compatible structured output and require distinct action evidence across timestamps, using retained development clips/raw outputs to address repeated invented events. Keep event definitions and scoring frozen, then predeclare any fresh comparison. Do not increase event limits, discard unmatched predictions, or integrate tracking merely to improve the reported score. No user annotation work is required to interpret this pilot.

---

Historical content below is preserved; earlier analysis-only/cloud prohibition/next-action statements are superseded by the current checkpoint and subsequent user authorization.

# Continue local Qwen evaluation

Prepared 2026-09-12 13:50 IST. This is a handoff plan, not a record of new inference runs.

## Objective and boundaries

Continue HypeReel evaluation using **Ollama + qwen3-vl:4b-instruct** on the two
development games. Improve measured event recognition through reproducible
experiments, not timestamp-specific prompt patches. Keep the third game sealed.
Do not confuse Ollama (runtime), Qwen (model), or a text-only Llama model.

Repository: `/Users/shivani/code/AgentAICourse/week3/hypereel`.
The local integration and reports are currently uncommitted working-tree changes.
Preserve them; inspect `git status` before editing. A fresh clone alone does not
contain this implementation until it has been committed and transferred.

Do not use paid/cloud inference or enable cloud fallback. The historical estimated
cloud ledger is $2.53027 against the original $5 cumulative ceiling. Local cost is
zero API charge, not zero runtime or electricity. Run inference serially on this
16 GB M1; do not run competing model jobs. Do not render/share automatically.

## Read first

1. `IMPLEMENTATION_NOTES.md`: dated decisions, local setup failures and fixes.
2. `iterations/iteration-log.md` and `iterations/history.jsonl`: all 21 Nebius
   iterations and the subsequent local result. Read historical caveats, not just scores.
3. `STATUS.md` and `iterations/README.md`: current decision and metric gates.
4. `iterations/ollama-development-001.report.json`: actual windows, classifications,
   configuration, model usage, timing and metrics.
5. `../docs/OLLAMA.md`: installation, restart, caching and local commands.
6. `golden/README.md`, `golden/manifest.json`, and the two development source-label
   files. Do not inspect `holdout/` while choosing implementation changes.

## What has already been learned

| Iterations | Finding to retain |
|---|---|
| 1–5 | Early slices had missing positives, poor candidate coverage, malformed responses, and misleading full-video denominators. Use the processed slice and inspect the funnel. |
| 6–12 | Spread/stratified sampling and dense action/context frames helped diagnosis, but did not establish generalization. Reference-stratified proposals are label-informed diagnostics. |
| 13–14 | Any-overlap matching falsely suggested perfect quality. Keep one-to-one, same-label, IoU-aware matching; never restore the permissive matcher. |
| 15–18 | Deterministic settings, contrastive verification and centered clips produced best tuned P=.667, R=1, F1=.8. Precision still failed the .7 gate. |
| 19–20 | Boundary/multiple-event ambiguity remained; independent game-1 slice P=1, R=.5, F1=.667 failed recall. |
| 21 | Alternative-label verification regressed to zero recall; rejected code was reverted, not its historical record. |
| Local 001 | Instruct model executed successfully but returned null for all four windows: TP=0, FP=0, FN=2, R=0. Hosting works; quality does not pass. |

Generic `qwen3-vl:4b` selects the thinking variant and exhausted 32/256 output-token
limits during text smoke tests. Explicit `4b-instruct` passed text and image checks.
Do not repeat the failed alias experiment. Instruct digest tested:
`ee4b975b58c17ce268cd19d40db35d5edc64603035d2ffc1fee1968eb0947f7b`.

Local 001: 5 frames, 6-second outer context, 448px edge, 8192 context tokens,
256 output tokens, no verifier. Four vision calls took 59–95 seconds each;
pipeline took 321.21 seconds. Five calls allowed four classifications and one
judge, but denied the second judge after a revision. The graph's fallback accepted
progression, not quality. Local LLM exceptions now propagate into “judge unavailable”
feedback; the graph can still proceed to human approval. Check that feedback and
usage, not just exit code or `status=success`.

Last offline verification: 319 passed, 4 skipped, one existing Gemini SDK warning.
No local game-2 quality run or full-game run has been completed.

## Dataset preflight — do this before expensive execution

Canonical combined references: `golden/cases/development.pipeline.jsonl`.
Game 1 video ID: `KBETdDRM70Q`; game 2: `rHSdABRoBeE`.

**Known path defect:** the combined file currently uses
`../../recipes/basketball_team_evaluation.yaml`. Relative to `evals/golden/cases/`
this resolves to missing `evals/recipes/`. Correct the recipe path to
`../../../recipes/basketball_team_evaluation.yaml` (and inspect the individual
case files and generators for the same issue). Add a regression test that loads
each development case and resolves its recipe. Record this as a fixture-path
correction, not a change to labels or a model improvement. This handoff has not
made that correction.

Verify video identity, duration, time origin and a sample of annotations against
the footage. Action bounds generated around event times are provisional (-5/+4 s),
not precisely human-annotated starts/ends. Do not silently treat their IoU as exact
action completeness. Record any audited corrections in versioned fixtures.
The current recipe/reference mapping covers selected highlight categories, not
every externally labeled turnover, miss or rebound. Keep raw labels and report
exactly which ontology is scored. A nearby steal and turnover can describe the
same possession change; do not force mutually exclusive labels without a mapping.

Cache each video once, recording hash, resolution and frame rate. Game 1 is already
at `downloads/KBETdDRM70Q.mp4` (640x360). Match preprocessing for comparisons.
The ordinary evaluator uses a temporary directory and can redownload URL inputs;
use new experiment fixtures pointing at cached sources rather than editing golden
labels to suit local paths. Downloads and model weights stay out of git.

## First execution sequence

From the repository root:

```sh
git status --short
.venv/bin/python -m pytest -o addopts='' -q
curl --noproxy '*' -s http://127.0.0.1:11434/api/tags
ollama ps
```

If the server is absent, follow `docs/OLLAMA.md`; do not start a second listener.
Existing app port 8502 is local-only; 8501 may still use old providers. Prefer the
evaluation CLI: the interactive app does not enforce a total-run call budget.

Run unchanged configuration on both existing small slices before tuning:

```sh
HYPEREEL_MAX_PROVIDER_CALLS=6 bash scripts/run_local.sh eval \
  --dataset evals/experiments/game-1-ollama-local.pipeline.jsonl \
  --output evals/results/iterations/ollama-development-002-game1 \
  --change-note "Repeat local baseline; same five-frame configuration; six-call cap permits both judge passes"

HYPEREEL_MAX_PROVIDER_CALLS=6 bash scripts/run_local.sh eval \
  --dataset evals/experiments/game-2-iteration-08.pipeline.jsonl \
  --output evals/results/iterations/ollama-development-002-game2 \
  --change-note "First local game2 baseline; same five-frame configuration; six-call cap"
```

Choose new output names if these already exist. The second command currently uses
a URL and may download the full game; preferably prepare a cached-source experiment
copy first with unchanged references and valid relative paths. Six calls per case
cover four classifications and up to two judge passes with verification disabled.
Caps are per case, not a combined dataset cap. Do not automatically retry failures.

## Refinement sequence

1. Inspect the actual ordered frames for false negatives: is possession change
   visible, are frames correctly ordered, and is the ball legible? Save frame times
   and sampling configuration. Frame inspection is diagnostic; labels must not be
   passed to inference or used to position production candidates.
2. Predeclare one hypothesis and one controlled change. For example, compare five
   central-action frames without outer context against the existing three central
   frames plus two context frames. Treat this as a proposed experiment, not a proven
   improvement. Keep model, resolution, matcher and recipe fixed.
3. Apply each configuration to both development slices. Record regressions as well
   as improvements. Repeat a configuration to assess instability before claiming a
   win. Temperature zero alone does not prove determinism.
4. Expand to a fixed source-time interval containing the first 10–15 **reference**
   events per game, plus negatives and more than steals. Freeze interval selection
   before inference. Never stop at the first 10–15 successful predictions: that hides
   misses and makes recall incomparable. Include every eligible reference in the
   observed interval, with explicit boundary-context policy.
5. Separate label-informed diagnostic sampling from source-driven proposal testing.
   Before release, measure candidate recall on source-driven intervals without using
   reference labels to select proposals. Report scores per game and event type as
   well as pooled counts; two games are not broad generalization evidence.
6. If sparse frames cannot show the action, design short overlapping temporal
   windows and multi-label timestamped output as an explicit schema change, with
   tests for multiple events, duplicates, invalid intervals and missed negatives.
   Do not merely lower confidence thresholds until everything becomes a highlight.

Five images required about 5823 prompt tokens in the tested runtime. The adapter
currently caps context at 8192; increasing to nine frames can exceed it. Do not
disable truncation checks or infer context usage from resized image dimensions.
Local 001's nominal 295–340 s horizon read padded windows/context approximately
283–358.33 s. Fix or document the boundary policy before broad interval comparisons.

## Metrics, gates and records for every iteration

Record TP/FP/FN; precision/recall/micro and macro F1; per-type confusion;
candidate and selected recall@IoU .1/.3/.5; specificity/false positives per observed
minute; schema/provider failures; invalid intervals/duplicates/overlaps; and the
proposal → classification → selection funnel. Record timing, tokens, actual model
digest, frame settings, source hash, dataset/recipe hash, code revision and dirty state.
Calibration/AP are secondary on tiny samples and may be uninformative for all-null
predictions. Precision/F1 currently report N/A for no selected clips; never call
that a pass. Changing the convention requires a metric version, not rewritten history.

Existing gates: candidate recall@.3 >=.8; selected precision, recall and F1 each
>=.7; selected recall@.3 >=.7; schema pass=1; invalid boundaries=0; overlap rate=0.
Require no provider failures or capped/unavailable judge masquerading as a success.
An LLM judge is advisory metadata review, not visual ground truth or the release gate.

Use a fresh report directory and meaningful `--change-note` every time. CLI appends
`iterations/history.jsonl`; never clear it or `spend-ledger.json`. Also append a row
to `iterations/iteration-log.md` and a dated decision to `IMPLEMENTATION_NOTES.md`;
update `STATUS.md`. Preserve full reports outside ignored results for handoff, as
with `iterations/ollama-development-001.report.json`. Never rewrite failed attempts.

Stop a batch on memory pressure, persistent timeout, context overflow, invalid
output or the request cap. Record it and diagnose before extending the batch.
Do not run either full game merely because local API cost is zero. After gates hold
on development data not used for the immediately preceding fix, freeze configuration
and run the first game end-to-end with human render/share gates. Only then use the
third game for final validation; never tune against its result.

## Completion report expected from the next agent

Provide per-game before/after metrics, each hypothesis/change and its decision,
operational failures and runtime, exact artifacts and reproducible commands, remaining
limitations, and whether gates actually passed. State clearly which slices/full
videos were processed and whether rendering occurred. No success claim from unit
tests, installation, empty output, or a judge fallback alone.

## Continuation addendum — 2026-09-12T14:17:14.239217+05:30

Development recipe-path defect is corrected and regression-tested. Game2 is cached as downloads/rHSdABRoBeE.mp4 with an unchanged-reference experiment file evals/experiments/game-2-ollama-local.pipeline.jsonl. Read the latest IMPLEMENTATION_NOTES and STATUS first: attempts 002, 003 and 004 stopped for memory pressure without completed accuracy metrics. 003 repeated the baseline after owner freed memory (35.41s); 004 explicitly tried num_batch128 (110.67s), which was insufficient. No game2 inference has completed or started. Optional OLLAMA_NUM_BATCH defaults to zero/unset, preserving server behavior; do not treat128 as validated. Execution records include hashes, commands, pressure samples and timestamps; partial classifications/tokens were lost on interruption. Next identifier005. No automatic retries, no full games, no third-dataset access. Consider durable per-call checkpoints and a revised memory plan before further inference. Offline suite:326 passed,4 skipped,1 holdout test deselected.

## Checkpoint refinement addendum — 2026-09-12T15:50:14.353575+05:30

Per-call checkpoints are now implemented through HYPEREEL_PROVIDER_CHECKPOINT_DIR. Read docs/OLLAMA.md and tests/test_call_checkpoints.py for durable events/recovery limits. Three-frame memory probe005 stopped at24.58s during model loading; sampled llama-server RSS max2.99GiB is not full physical peak. Monitor cancellation, not observed crash; one call start and interrupt preserved, no response/tokens/classification. Do not run006 automatically: operational expansion condition failed. Preserve existing history; no game2 or holdout inference. Current source remains uncommitted.

## 2026-09-12T16:12:12.205274+05:30 — Owner supersedes memory-warning stop policy;006 declared

Owner explicitly instructed continuation without prematurely stopping on memory pressure alone. Earlier002–005 interruptions reflected a conservative monitor policy, not demonstrated inability to run or evidence of imminent crash. Revised monitor records pressure levels and swap plus RSS every second but never cancels merely for pressure. Keep existing180s per-request timeout, six-call cap, valid-input/schema requirements, local-only providers, serial jobs, and durable checkpoints. Actual timeout/provider error/process exit is an operational failure, not automatically an OOM crash. No arbitrary system memory knobs or other user applications changed.

Run006 with four diagnostic candidates each on game1 and game2: three central frames, zero outer context,4096 context, output256,batch128,448px; model/source/labels/matcher unchanged. These settings define a distinct smaller visual baseline, not directly comparable with five-frame001. Record each game outcome before launching the next. Third dataset remains sealed.

## 2026-09-12T16:20:40.181919+05:30 — 006 batch complete; correction to earlier memory interpretation

Both bounded development slices completed under warning pressure. Game1:4 vision +2 judge calls,194.70s,16,153 tokens, peak sampled llama-server RSS4.614GiB. Game2:3 vision +2 judge calls,130.06s,12,376 tokens, peak sampled RSS4.693GiB. Combined:11 successful requests,28,529 tokens,324.76s pipeline time; no provider errors/timeouts, no observed crashes, no cap denials. All final classifications were null. Each gameTP0/FP0/FN2, recall0, precision/microF1/macroF1 undefined for empty selection. Candidate recall@IoU.3=1 for each; selected recall@.3=0; schema1; specificity1; quality gates fail. Each judge gave quality_score0 and requested broadening; graph revision limit ended progression, not quality acceptance.

Game2 began at pressure level2 and remained at2 for all124 observations. Game1 recorded23 normal and162 warning samples. System swap used increased from3,631.12MiB at game1 start to5,008.81MiB at its end, then6,379.06MiB at game2 end. These are system-wide readings, not exclusive attribution to Qwen. Model unloaded only after both completed, to release resources; warning pressure still present immediately afterward. This demonstrates completed bounded operation despite warnings. Earlier aborted002–005 runs do not establish hardware infeasibility; they were prematurely stopped by our prior warning-only rule, now explicitly superseded by the owner. Full-game stability remains untested.

Reporting defect found: reference-stratified sampler may return fewer candidates than cap when eligible positive/negative choices are exhausted. Game2 actually selected/classified3, but progress message printed configured cap4. Fixed only the message to len(ordered); no sampler/label/metric change. Historical006 reports retain original message and actual candidate/classification arrays.37 existing graph tests passed after this logging-only correction; diff check passed.

Ordered frame times saved for both games. Roughly6-second gaps plausibly miss transient possession changes, but this has not been proven causal. Next quality experiment should predeclare denser core sampling on both fixed development slices while keeping matcher/model fixed and preserving the new observe-only memory policy. No new experiment or full game launched in this batch. Holdout remains untouched. All reports, checkpoint journals, execution samples, observations, frame schedules, cumulative history, notes and status saved.

## 2026-09-12T16:34:15.537622+05:30 — Source quality preflight;007/008 controlled plan

Owner asked whether HD input quality affects misses, requested execution of next plan, and asked about rebounds/turnovers. ffprobe confirms both cached sources640x360 (game1 30fps,game2 25fps). Production adapter previously resized to448x252 and JPEG85; tests006 did not operate on HD. Source-quality lookup1 using existing authenticated HD profile failed on game1 with page-needs-reloaded. Lookup2 unauthenticated current base profile succeeded for both but exposed only progressive640x360 playable video. Lookup3 alternate documented clients/current player script failed video-unavailable on both. Metadata results preserved in work/hd-source-check; these access outcomes do not prove the original uploads lack HD. Asked owner asynchronously for local HD originals; no path available yet. No new video download, no upscaling passed off asHD.

Proceed with bounded comparisons that available sources support:007 removes only additional downscaling (640px edge,3 central frames,context4096), compared to006448px edge.008 uses5 central frames at640px edge,context8192 to accommodate input; otherwise fixed source/model/batch128/prompts/candidates/selection. Both games, serial,pressure-observe-only,checkpoints retained. Require candidate windows match006 before interpreting differences. Keep negative windows and both reference steals per game. Five-core spacing is approximately3s rather than6s; still not dense video. HD benefit remains untested without trueHD inputs. Progress means a reproducible finding per iteration, not a guaranteed score increase.

Raw development annotations contain90 rebounds (43 offensive,47 defensive) and95 turnovers. Current recipe positive types are made_basket,three_pointer,block,steal, while prompt explicitly excludes rebounds/unforced turnovers.006 measured only two reference steals per game and returned all-null; it cannot establish rebound/turnover detection. Broader event detection requires a separate versioned recipe/prompt and scored references, plus handling paired steal/turnover events in the same possession; do not rewrite current golden labels or historical metric denominators.

## 2026-09-12T16:49:09.762012+05:30 — Source quality and active comparison continuation

Both cached videos remain640x360;006 fed448x252,007 feeds640x360.007 completed both games with all-null classifications, TP0/FP0/FN2 each,11 successful calls,489.12s total pipeline time, peak sampled llama-server RSS4.685GiB; no crashes/provider errors. Candidate arrays exactly match006; checkpoint and report counts/classifications agree.008 five central frames/context8192/native360p is currently running game1, with game2 planned after completion and review. Check latest execution/observations before starting anything to avoid duplicate attempts. Both source games play in1080p in existing signed-in Codex browser (game1 decoded1920x1078;game2 1920x1080). No localHD file obtained: game1 YouTube Download menu offers480p and Premium upsell forHD; authenticated yt-dlp default+web_safari returned only storyboard assets for both. Owner says originals unavailable locally, offered account access; pending clarification whether account owns uploading channel. No credentials exported or subscription purchased.

A1fps diagnostic frame audit found the referee handling a restart at source330 in game1, so timestamp semantics/bounds need audit. Raw labels explicitly call times external clip timestamps, not precisely annotated actions. Do not shift/update golden references based on guesses. Current tests score only two steals per game; rebounds/turnovers are excluded by current recipe/prompt. They require a separately versioned ontology and evaluation. Preserve historical metrics and the sealed third dataset. Next after this bounded matrix: settle scoped HD retrieval and verify actual action timing before another model/prompt tweak.

## 2026-09-12T16:55:40.791209+05:30 — 007/008 quality comparison closed

Both predeclared iterations completed on both development games.007 retained native640x360 with3 central frames;008 used5 central frames at640x360/context8192. Each game in each iterationTP0/FP0/FN2, recall0, precision/F1 undefined, schema1, provider errors0, candidate recall@IoU.3=1, selected recall0, specificity1. No quality gates passed. All candidate arrays exactly match006. Checkpoint/report classification and call counts agree and every journal ends scope_finished. Total22 successful requests,73975 tokens,1199.82s pipeline time, peak sampled llama-server RSS5.613GiB. No timeout/context overflow/provider failure/cap denial/crash observed. Warning pressure recorded without cancelling. Every judge requested revision with score0; revision limit ends progression, not quality acceptance. No cloud inference or rendering; third dataset sealed.

Decision: neither retaining full360p detail nor five central frames demonstrated a recognition improvement on these diagnostic slices. Do not promote either as a validated fix. This is not an HD comparison and not proof that HD would or would not help. Browser HD availability is verified, local HD retrieval unresolved. Uploader-account clarification remains pending; no new account login, purchase or account-wide export performed. Boundaries are provisional external clip timestamps, with game1 source330 showing a restart in the1fps audit. Next: establish scoped uploader export/source resolution and continuous-motion timing semantics before more tuning; preserve original labels and version any audited corrections. After timing/source preflight, use source-driven short overlapping windows to test closer temporal sampling under an explicit call budget; do not target proposal centers at reference anchors. Broader rebounds/turnovers need a separately versioned ontology and scored development intervals. Full-game expansion is premature on accuracy evidence, not on warning pressure alone.

Per-run measurements (RSS sampled, system swap not model-exclusive):
[
  {
    "name": "ollama-development-007-game1",
    "seconds": 261.06259433401283,
    "calls": 6,
    "tokens": 16670,
    "peak_rss_gib": 4.6853790283203125,
    "swap_start": "total = 6144.00M  used = 4773.44M  free = 1370.56M  (encrypted)",
    "swap_end": "total = 6144.00M  used = 5612.50M  free = 531.50M  (encrypted)"
  },
  {
    "name": "ollama-development-007-game2",
    "seconds": 228.0543498749903,
    "calls": 5,
    "tokens": 12770,
    "peak_rss_gib": 4.657806396484375,
    "swap_start": "total = 6144.00M  used = 5612.50M  free = 531.50M  (encrypted)",
    "swap_end": "total = 8192.00M  used = 7421.38M  free = 770.62M  (encrypted)"
  },
  {
    "name": "ollama-development-008-game1",
    "seconds": 409.0317989170144,
    "calls": 6,
    "tokens": 25300,
    "peak_rss_gib": 5.6128387451171875,
    "swap_start": "total = 8192.00M  used = 7413.38M  free = 778.62M  (encrypted)",
    "swap_end": "total = 9216.00M  used = 7964.56M  free = 1251.44M  (encrypted)"
  },
  {
    "name": "ollama-development-008-game2",
    "seconds": 301.6722972499847,
    "calls": 5,
    "tokens": 19235,
    "peak_rss_gib": 5.47918701171875,
    "swap_start": "total = 9216.00M  used = 7972.19M  free = 1243.81M  (encrypted)",
    "swap_end": "total = 11264.00M  used = 10331.50M  free = 932.50M  (encrypted)"
  }
]

Implementation verification: no new production code changed in this quality matrix; per-run settings supplied through environment. Existing offline checks retained, git diff --check passed. New bounded runner/finalizer/export helpers in work preserve commands, hashes, reports, memory observations, exact frame schedules and per-call journals. Historical files/ledger not rewritten. Model unloaded after final run to release task resources.


## 2026-09-12T17:02:18.680880+05:30 — Owner corrects scope to all basketball events

Owner explicitly clarified ALL raw basketball event types are desired, including TOV, DR, OR, STL, missed/made2PT/3PT, FT and remaining types such as AST/BLK. Earlier highlight-only scope is superseded for future quality work. The old generator mapped only made2PT/made3PT/STL/BLK; the old recipe excluded misses/free throws and existing classifier contract holds one label per window. The recent steal-only slices were narrow diagnostics, not representative all-event quality. Keeping that scope without verifying owner intent was an evaluation design error. Preserve historical results as narrow-scope evidence; never treat their excluded events as negatives in the new evaluation.

Prepared additive basketball-all-events-development-v2 reference ledger and manifest under evals/experiments/all-events-v2 with scripts/build_all_events_development.py. Contains all462 raw events from exactly the two development games,12 categories separating shot type/outcome, source identities/provenance hashes and paired events. Unknown labels fail explicitly rather than silently dropping. Actual action intervals left null because source clip timestamp semantics are unverified; no invented boundaries. Original golden files and historical scores preserved. Four targeted tests passed: complete coverage/identity, unknown type/outcome rejection, paired steal/turnover preservation. This is a reference inventory and explicit scoring/sampling plan, NOT a runnable multi-event detector or completed broad benchmark.

Future metric version: per-type TP/FP/FN,precision,recall,F1/support,unweighted macroF1 plus microF1 and worst-type recall. Positive-supported classes with zero predictions get recall0/F1=0 (precision undefined); report absent classes as unmeasured and insufficient for passing. Require each class meet precision/recall gates and adequate sample support so abundant made baskets cannot mask missing steals/rebounds. Preserve one-to-one same-label matching, multiple events per window and duplicate controls; score detection before highlight budget/selection. Stratified diagnostic examples cover alltypes; continuous source-driven intervals score ALL events and verified background without label-selected proposals. Per-prediction confidence is not evaluation quality; more same-type examples do not establish other-type reliability. Matching tolerance/IoU policy must be frozen after timing audit. Need multi-event detector/prompt/scorer implementation before all-event inference; changing only the recipe would retain hardcoded exclusions and single-label loss.

Owner confirmed their account owns uploading channel and requested opportunity to login. Opened visible in-app YouTube Studio; existing session redirected to YouTube with a create-channel dialog, indicating it was not the uploader channel. Did not create a channel. Account switch flow now shows Google YouTube sign-in; user instructed to login directly and tell us when ready. No password/verification code requested in chat, no account-wide export or purchase. HD retrieval awaiting user login; no new inference in this scope-correction step. Third dataset remains sealed.

## 2026-09-12T17:10:04.600810+05:30 — Studio source acquisition checkpoint

Game1 owner export verified and cached:1280x718/30fps,H264+AAC,599,964,155bytes,duration2822.478367s,source time origin0. Four alignment checks at50/300/900/1800s against existing360p cache searched±1/3s; all best offsets0s,correlations0.9884–0.9909. Sample evidence supports reusing source timestamps; does not validate reference action labels or prove every-frame alignment. Source checksum/probe/alignment record saved evals/iterations/studio-source-game1.json. Existing cached360p untouched. Future HD inference must use this new path and explicitly record actual supplied image size; merely switching source while keeping448px resize would discard much of the detail.

Game2 direct Studio edit page verified title Shourya - Unl(47)vs campus(35),Your video,and owner Download option. Browser downloadMedia and standard click produced no completed/local partial second-video file. A direct navigation to the observed owner download link returned net::ERR_BLOCKED_BY_CLIENT. This is a concrete browser export blocker, not model failure or proof of absent HD. Left second-video Options→Download open and marked tab for handoff; owner asked to click manually. No attempt to bypass browser blocking or export session credentials. No account settings/video metadata changed. First export ready; second resolution/file still unverified. No new model inference or all-event accuracy score in this step. Third video/dataset untouched; never navigate to it for development. Continue after manual second download: verifyfile/hash/timing, then implement/run all-event benchmark with durable per-call notes and per-type gates as already specified.

## 2026-09-12T17:18:58.740967+05:30 — Both Studio development sources acquired

Owner reported campus download complete. Verified Downloads/Shourya - Unl(47)vs campus(35).mp4 as1280x720/25fps,H264+AAC,754,448,114bytes,duration2828.724535s,start0. Cached separately as downloads/rHSdABRoBeE.studio-720p.mp4; SHA256 5d0c2bcc274bb7335e3aa42817855484ea5c25ca0e01d9f4ccfb1d926017e1b2. Four sampled frame-alignment checks at50/300/900/1800s searched±0.4s; all best offsets0s,correlations0.9859–0.9908. This supports shared source timestamps at sampled positions, not exhaustive alignment or validation of provisional event labels. Full media metadata/hash/alignment saved studio-source-game2.json. Original360p sources and previous source-acquisition failure record preserved.

Both development higher-resolution sources are now ready:game1 1280x718/30fps,game2 1280x720/25fps. These are approximately720p exports, not original1080p. HD acquisition blocker resolved by owner's manual second download. No new inference or improved accuracy claim in this step. All-event scope remains462 labels/12categories; multi-event detector/scorer implementation and continuous-motion timing audit remain required before broad benchmark. Next runs must explicitly point to new cached sources and record model input resize; old448px default would discard much of acquired detail. Preserve bounded serial calls,checkpoint journal,observed memory policy,all per-type scores,original labels and no third dataset access.

## 2026-09-12 — All-event009–011 results and next action

009–011 completed:18/18 provider calls successful,no crash/timeout/schema failure,23.85min total measured batch runtime,peak sampled llama RSS6.400GiB.0094frames and0106frames each TP0/FP0/FN14,macro/microF1=0 across12types.011observations on two-window subset TP0/FP0/FN6,macroF1=0 across6supportedtypes. Zero event-recognition gain; do not adopt6frames as a quality win.011 improved failure visibility only: repeated generic possession descriptions despite distinct images and visible motion in both games. Inference descriptions are not trusted ground truth. Model unloaded after completion. Offline suite345passed,4skipped,1final_holdout test deselected. Holdout untouched.

Implemented additive all-event detector/scorer with paired outputs,raw-output checkpoints,12-category macro and per-type metrics; production highlight path remains single-label. Source exports720p,actualimages768x431/432. References remain provisional clip timestamps and windows label-informed; neither high nor low diagnostic scores establish exact action localization or full-game generalization. Do not silently repair timestamps from uncertain contact sheets. Next concrete experiment proposed after user's YOLO/RF-DETR question: freeze development source intervals,annotate visible-ball/player boxes and audit event timing,benchmark small YOLO+tracking,then compare detector-assisted crops/track evidence+Qwen with Qwen-only on identical intervals. RF-DETR alternative if measured detection failures warrant comparison. No detector installed/benchmarked yet. Run stages serially,cachetracks,measurememory; no assumption of automatic quality gain. Preserve new all-events-history.jsonl alongside legacyhistory. No further prompt-only batch or fullgame/holdout run started.

Runnable details:docs/ALL_EVENTS_EVAL.md;detector src/hypereel/evaluation/basketball_events.py;runner scripts/eval_all_events_local.py. All evidence preserved in evals/iterations/ollama-all-events-009,010,011,including pre-change code snapshots. Existing numbered output directories cannot be overwritten. Latest owner request asked status and detector+Qwen architecture; recommendation is a proposal,not evidence of implementation. Read latest notes before starting next numbered pilot.

## 2026-09-12 — Matched Nebius comparison012

Matched Nebius MiniCPM comparison completed both broad configurations with byte-identical JPEGs and prompt text against frozen local snapshots. Fourframes:TP4/FP32/FN10,P=.1111,R=.2857,microF1=.16,macroF1=.05979. Sixframes:TP5/FP49/FN9,P=.09259,R=.35714,microF1=.14706,macroF1=.09615. Qwen bothTP0/FP0/FN14,F1=0. These are provisional label/time matches,not independently visually confirmed detections; same14labels/12types,not fullgames. MiniCPM is more willing to emit events but has severe overprediction and weak evidence. Raw examples infer repeated scores from unchanged scoreboard and label being positioned for a rebound as completed control. Both violate prompt intent. Sixframes adds one turnover match but21moreFP than fourframes and lower microF1. No steals,assists,blocks,offensive rebounds,free throws,or three-point events matched. Do not call MiniCPM reliable or promote sixframes/YOLO based on this.

Explanation comparison against011 stopped on its first response:HTTP/completion finished successfully,141outputtokens (not truncation),but only1observation for6images. Strict parser correctly rejected it;0of2explanationwindows valid,second unattempted. Do not report zero-error18/18 or score rejected event. Total17paid requests,16schema-valid event outputs,1schema failure,no provider failure,no retries,56.57s batch elapsed. Conservative historical10/30 USD per million ledger estimateincrement$0.41311,total$2.94338 below$5;not confirmed invoice pricing. User explicitly authorized this hosted comparison; no ongoing general cloud fallback introduced. Third dataset untouched. Recordvalidation-audit.json preserves exactcause separate from genericValueError history. No model/label/prompt changes after seeing results. Nextpriority remains visual timing audit and bounding event outcomes to observable evidence; apples-to-apples evidence now available before an architectural choice.

Runner:scripts/eval_nebius_matched.py;13 targeted parity/scorer tests passed. Existing012 output cannot be overwritten. Read full report and per-type metrics before interpreting apparent TP as visually proven. Earlier local-only constraint is superseded only for the explicitly requested Nebius comparison. No YOLO integration started.

## Latest user boundary: architecture analysis only

User said not to implement the detector change yet and requested thorough analysis. Full proposal and offline findings are in outputs/hypereel-architecture-analysis.md and latest IMPLEMENTATION_NOTES. No inference, installs or application changes for that analysis. Do not execute earlier proposed YOLO pilot automatically. Keep third dataset sealed.
