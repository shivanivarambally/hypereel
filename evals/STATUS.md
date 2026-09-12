## Latest checkpoint — Gemini quota blocked 2026-09-12T22:51:12.553566+05:30

Read evals/iterations/gemini-development-summary/results.md and report.json, then latest IMPLEMENTATION_NOTES.023confirmationpartial;024/027combined strict-valid video0–5cover8references8types:GeminiTP3/FP4/FN5,P42.86%,R37.5%,F1.40;matched historicalMiniCPMTP1/FP25/FN7,F1.05882. Video6/7missing,so all12categoryevaluationNOTcomplete. Image2/6confirmationmissing. GoogleHTTP429dailyquota20/model/project exhausted; do not retryshortRetryInfo or change keys toreset. Need paidquotaor dailyreset(midnightPacific;Sep13 12:30PMIST). No inference running/scheduled. Ledger$7.192295/$8includesunknownusage reservations.025transcriptscript/planprepared,unrun;026missing-imageplanprepared,unrun. New retryhandler stopsdailyquota. GenericYOLOdeferred based020fragmentedballtracks. Third dataset remains sealed. Earlier statuses below are historical.

---

## Latest checkpoint — Gemini021/022 2026-09-12T22:36:14.743400+05:30

Read evals/iterations/gemini-pilot-021/results.md and latest IMPLEMENTATION_NOTES.md.021sixcalls complete but strict JSON rejects Markdown fences; separate formatting-only reparse shows videoTP4/FP3/FN6,F1.47059 vs cached same-subset MiniCPMTP3/FP13/FN7,F1.23077. ImagesTP2/FP0/FN8,F1.33333.022JSON output mode first call valid,secondHTTP503high demand; stopped with no paired confirmation score. No inference running or scheduled. Ledger$6.753083/$8 includes unknown-usage reservation. Third dataset sealed. Next: separately logged capacity recovery/JSON confirmation, then broader eight-window/all12type test if improvement holds. No production architecture shift. Earlier statuses below are historical.

---

## Latest checkpoint — YOLO/ByteTrack transcript pilot020

Updated 2026-09-12T21:51:35.991675+05:30:020tested YOLO11n+ByteTrack+track-augmented transcript+MiniCPM against shared visual transcript+MiniCPM, on3fully paired development windows(10references,9supported types). TP3→3,FP6→4,FN7→7;precision33.33%→42.86%,recall30%unchanged,microF1 31.58%→35.29%. Modest numerical gain,not reliable event recognition. Native tracking1023frames:only8observed ball-track frames,longest0.133s;no ball tracks in free-throw orCampus clips. All3TPs inCampus;none of7experimental predictions cited a track observation. Evidence errors remain. Local126.33s,peak0.4454GiB;9cloud calls20.83s,$0.28511increment,ledger$6.6463of$8.388tests passed,4skipped,1holdout-test deselected. No inference running,third dataset untouched. Read evals/iterations/track-transcript-020/results.md and plans/raw tracks/report, then latest IMPLEMENTATION_NOTES. Sustained ball tracking is the next unresolved prerequisite; no further experiment scheduled.

Earlier next-action statements below are historical.

---

## Latest continuation —018/019

Current checkpoint 2026-09-12T21:37:57.009084+05:30:018/019 complete with invalid windows. Corrected v2 rules,4fps source sequences and native rim crops tested.018:31calls,no paired valid windows.019:50calls,one paired window,both armsTP0/FP0/FN4. No demonstrated recognition gain. Mixed-view row duplication and continuing visual errors remain. Total incremental estimated$1.29907;ledger$6.36119of$8.388tests passed,4skipped,1holdout-test deselected. No inference running; third dataset untouched. Read evals/iterations/evidence-state-019/results.md first, then018/019plans/reports and latest IMPLEMENTATION_NOTES. Next decision is a separately frozen perception-component comparison, not another silent MiniCPM prompt retry. Original017code/results remain unchanged; new contract is src/hypereel/evaluation/ball_state_v2.py. No production integration or full court geometry.

Older next-action statements below are historical and superseded by this checkpoint and the latest user authorization.

---

## Current checkpoint — state pilot017, grounded derivation, and the localised conclusion

Recorded 2026-09-12T21:12:53.512927+05:30. Ledger $5.06212 of the $8 ceiling, not reset. Third dataset untouched.

Owner asked for a recommended architectural change, implemented and tested. The016 diagnosis was that the model asserts outcomes it has not seen and the scorer cannot distinguish an assertion from an observation. 017 removes the opportunity instead of instructing against it: the model reports per-frame ball state from a closed vocabulary and events are derived deterministically in src/hypereel/evaluation/ball_state.py. Identical frames to016, same model and decoding, same references and matcher; only the output contract changed.

**The score fell to zero, and that is the finding.** Derived TP0/FP1/FN14, microF1 0, against dense016 direct .12698 and sparse013 direct .125. Across48 frames the model reported held24, loose20, in_flight3, through_net ONCE and rim_contact ZERO times. Eight windows containing five shot-outcome references produced not one observed rim contact. Constrained to report only what is visible, this model does not report shot outcomes at all. Every made and missed shot scored in009 through016 was asserted, not observed — previously an audit inference, now a direct measurement.

The one derived event is instructive: window1 reference free_throw_made@225, model reported through_net at229.4 with court_zone beyond_arc, so the derivation typed it three_point_made and scored a false positive. Outcome seen correctly, shot type wrong. With the right zone it would have matched. One case in fourteen.

What the architecture delivered and keeps: zero contradictory label pairs by construction against26 in016; zero scoreboard-derived events, since the scoreboard is not in the vocabulary;13 unit tests over a stage that is verifiable without a model; and lost recall made visible as derivation notes rather than silent gaps.

CONCLUSION. Grounding removes fabrication and removes the score with it, because the perception layer cannot supply the primitive every scored event depends on. Best measured results anywhere in the track are microF1 .25 direct and .50 to .60 on a two-window transcript subset, both shown ungrounded; the honest grounded score is 0, against gates of .70 on precision, recall and F1. Four distinct changes have now hit the same wall: transcripts015, detector crops013/014, denser frames016, grounded derivation017. No prompt, representation or scoring change over six768px frames of720p broadcast footage will reach the gates. What is needed is a change to the evidence — rim-region frames at much higher effective resolution, sampling dense enough around a release to contain the outcome, and a court-zone signal from geometry rather than the same model. Those are data and instrumentation changes; none is started or authorized.

Validation:378 passed,4 skipped,1 final_holdout deselected; git diff --check clean. transcript-pilot-015 artifacts byte-identical throughout. No holdout access, no label change, no report overwritten, nothing committed.

---

Earlier checkpoints below are historical.

## Current checkpoint — dense pilot016 and overall conclusion

Recorded 2026-09-12T20:58:30.835777+05:30. Owner raised the cumulative ceiling from $5 to $8 and asked for the necessary changes and a conclusion. Ledger $4.88544 of $8, not reset. Third dataset untouched throughout.

Pilot016 tested the one hypothesis the015 audit actually pointed at: that sparse evidence, not the output representation, was the binding constraint. Single declared change, frame spacing 2.4s across12s becomes 1.6s across the8s core, same model, prompts, temperature, seed, output cap, references, definitions and matcher, both arms sharing one boundary policy from the outset. Declared confound: at the six-image provider limit density and span cannot be varied independently.

Execution:24 of24 calls completed, no provider error or retry,79.65s,39,878 tokens, $0.54936. Direct valid8/8, narration valid8/8, extraction valid4/8.

**The hypothesis is not supported.** Direct arm across all8 windows and14 references: sparse013 microF1 .125 to dense016 .12698, with precision and macroF1 falling and predictions rising 34 to49. Both arms on windows1 and6: direct .16667 to .25, transcript .60 DOWN to .50. The transcript arm got worse.

The recall gain is measured to be hedging, not recognition. Dense016 direct emitted26 mutually exclusive label pairs across5 windows against sparse013's3 across2. One-to-one same-label matching credits whichever member of a made/miss pair is right and charges the other only a false positive. Window0, which has no annotations, emitted all four exclusive pairs at one timestamp.

Evidence quality moved backwards:0 of20 dense transcript events pass the entailment screen, against2 of8 in015.

Density did fix one real thing: the window1 narration error the015 audit caught. 015 called it a player in black near the three-point line; it is a free-throw setup, and016 narrates it correctly. Perception improves with denser frames. Grounded event extraction does not.

Sample-size warning that applies retrospectively: 015's primary paired figure was .40 on windows[2,6]; the identical retained output scores .60 on windows[1,6]. Window choice moves the headline more than any treatment tested.

CONCLUSION. Iterations009 to016 do not produce reliable event recognition and the failure is now localised. The model asserts outcomes and possession its own evidence does not contain, and the scorer cannot tell an assertion from an observation. Best measured result is microF1 .25 direct and .50 to .60 on a two-window transcript subset against gates of .70 on precision, recall and F1; the grounded score is 0. Three representation changes have now failed (transcripts, detector crops, denser frames), which is consistent with assertion-under-uncertainty being primary rather than evidence sparsity. Closing the gap needs a detector that must ground an outcome in a visible event, a scorer that penalises mutually exclusive predictions for one action, and audited action timings. Those are architectural, not prompt-level, and none is started.

Tests364 passed,4 skipped,1 final_holdout deselected; git diff --check clean. transcript-pilot-015 artifacts verified byte-identical throughout. No holdout access, no label change, no rendering, upload, deployment or architecture change, nothing committed.

---

Earlier checkpoints below are historical.

## Current checkpoint — boundary parity and entailment audit of015

Recorded 2026-09-12T20:33:43.418354+05:30. Offline work only: zero provider calls, ledger unchanged at $4.33608 of $5, third dataset untouched. report.json and observation-audit.json verified byte-identical before and after. No new iteration number was claimed; this audits015.

Both prerequisites named in the previous checkpoint are now discharged. First, identical core/context boundary handling is enforced in shared library code rather than at each call site. The015 defect was in the callers, not the parser: the direct arm validated over the supplied image span and filtered to core, while the extraction arm validated over core and raised, so window1 left paired coverage because it emitted an event at233.0s, itself a supplied frame timestamp the direct arm would have accepted and filtered. The mirror case confirms asymmetry rather than a model difference: window2 direct emitted two_point_made at766.0, equally out of core, and it was retained as context. Added check_window_span, partition_by_core and parse_window_events to basketball_events.py and the symmetric parse_window_extracted_events to transcript.py. Nothing was loosened; the strict all-or-nothing parsers keep their signatures and are now pinned by their own test. scripts/run_transcript_pilot.py is deliberately unmodified and its015 snapshot stays byte-identical.

Second, entailment is now measured as its own axis. Re-parsing retained raw extraction text under the parity policy recovers window1, so the audit covers19 events across all three windows (11 direct,8 transcript), not the6 the original parser accepted. Transcript:1 entailed,7 unsupported. Direct:0 entailed,3 asserted,8 unsupported, of which5 infer a basket from the scoreboard against explicit prompt instruction, twice quoting an unchanged 7-0 score as evidence for further baskets. The transcript arm also extracted two mutually exclusive rebound labels from one identical observation at one timestamp.

Headline: under parity the arms produce5 label/time matches (direct2, transcript3). None is entailed;4 are unsupported and1 merely asserted. Every one of the transcript arm's3 matches rests on evidence that does not establish the event it claims.

Entailment-gated secondary diagnostic, never a replacement for the primary metrics: transcript keeps1 of7 scored events and falls to TP0/FP1/FN10, microF1 0; direct keeps3 of10 at a weaker asserted bar for TP1/FP2/FN9, microF1 0.15385. The gate lowers both arms and was not used to select or remove anything from the primary result. The arms are gated at non-equivalent bars because direct events cite no frozen text, so this is not a clean paired comparison.

Label/time scoring under parity reproduces observation-audit.json exactly (direct TP2/FP8/FN8 microF1 0.20; transcript TP3/FP4/FN7 microF1 0.35294), independently confirming the parity implementation. Primary paired_metrics in report.json are untouched and unrestated.

The one entailed transcript event, window1 two_point_miss at228.2s, is also the clearest evidence that the axes are independent: the015 contact sheet shows that window is a free-throw setup narrated as a shot near the three-point line, so it is a faithful extraction from a false narration. Entailed by the transcript does not mean visually correct. Of18 observation rows,6 are marked visibility=clear while the text hedges. Every unsupported transcript event carries confidence1.0 and every unsupported direct event0.8; reported confidence tracks neither entailment nor correctness.

Validation:363 passed,4 skipped,1 final_holdout test deselected, up from355 by8 new tests; git diff --check clean. The parity guard was verified red on reverting the transcript-side bounds, not merely assumed.

Decision unchanged and better evidenced: do not adopt this MiniCPM narration/extraction combination as a detector. The015 numerical lift remains real as a label/time measurement and remains recorded, but no part of it is evidentially grounded. Any larger frozen comparison should apply the parity policy and record entailment from the outset rather than as a post-hoc audit, and should treat observation accuracy, entailment and label/time matching as three separate measured axes. No inference was started, no architecture changed, no rendering or upload performed.

---

Earlier checkpoints below are historical.

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

Latest user direction: **analysis/proposal only; no detector implementation or new inference.** Deep analysis delivered in user outputs/hypereel-architecture-analysis.md. Read latest notes for evidence, architecture options and predeclared decision checks. Earlier next-action suggestions below do not authorize immediate execution.

Latest status (2026-09-12,after Nebius012): **Matched comparison:MiniCPM detects more but remains unreliable.**

Matched Nebius MiniCPM comparison completed both broad configurations with byte-identical JPEGs and prompt text against frozen local snapshots. Fourframes:TP4/FP32/FN10,P=.1111,R=.2857,microF1=.16,macroF1=.05979. Sixframes:TP5/FP49/FN9,P=.09259,R=.35714,microF1=.14706,macroF1=.09615. Qwen bothTP0/FP0/FN14,F1=0. These are provisional label/time matches,not independently visually confirmed detections; same14labels/12types,not fullgames. MiniCPM is more willing to emit events but has severe overprediction and weak evidence. Raw examples infer repeated scores from unchanged scoreboard and label being positioned for a rebound as completed control. Both violate prompt intent. Sixframes adds one turnover match but21moreFP than fourframes and lower microF1. No steals,assists,blocks,offensive rebounds,free throws,or three-point events matched. Do not call MiniCPM reliable or promote sixframes/YOLO based on this.

Explanation comparison against011 stopped on its first response:HTTP/completion finished successfully,141outputtokens (not truncation),but only1observation for6images. Strict parser correctly rejected it;0of2explanationwindows valid,second unattempted. Do not report zero-error18/18 or score rejected event. Total17paid requests,16schema-valid event outputs,1schema failure,no provider failure,no retries,56.57s batch elapsed. Conservative historical10/30 USD per million ledger estimateincrement$0.41311,total$2.94338 below$5;not confirmed invoice pricing. User explicitly authorized this hosted comparison; no ongoing general cloud fallback introduced. Third dataset untouched. Recordvalidation-audit.json preserves exactcause separate from genericValueError history. No model/label/prompt changes after seeing results. Nextpriority remains visual timing audit and bounding event outcomes to observable evidence; apples-to-apples evidence now available before an architectural choice.

Older statuses below are historical.

Latest status (2026-09-12,after011): **All-event recognition still fails.** 009–011 completed:18/18 provider calls successful,no crash/timeout/schema failure,23.85min total measured batch runtime,peak sampled llama RSS6.400GiB.0094frames and0106frames each TP0/FP0/FN14,macro/microF1=0 across12types.011observations on two-window subset TP0/FP0/FN6,macroF1=0 across6supportedtypes. Zero event-recognition gain; do not adopt6frames as a quality win.011 improved failure visibility only: repeated generic possession descriptions despite distinct images and visible motion in both games. Inference descriptions are not trusted ground truth. Model unloaded after completion. Offline suite345passed,4skipped,1final_holdout test deselected. Holdout untouched.

Implemented additive all-event detector/scorer with paired outputs,raw-output checkpoints,12-category macro and per-type metrics; production highlight path remains single-label. Source exports720p,actualimages768x431/432. References remain provisional clip timestamps and windows label-informed; neither high nor low diagnostic scores establish exact action localization or full-game generalization. Do not silently repair timestamps from uncertain contact sheets. Next concrete experiment proposed after user's YOLO/RF-DETR question: freeze development source intervals,annotate visible-ball/player boxes and audit event timing,benchmark small YOLO+tracking,then compare detector-assisted crops/track evidence+Qwen with Qwen-only on identical intervals. RF-DETR alternative if measured detection failures warrant comparison. No detector installed/benchmarked yet. Run stages serially,cachetracks,measurememory; no assumption of automatic quality gain. Preserve new all-events-history.jsonl alongside legacyhistory. No further prompt-only batch or fullgame/holdout run started.

Earlier status entries below are historical.

Current all-event run (2026-09-12):009 complete,010 running. New multi-event detector/scorer covers all12 categories before highlight selection.009:8 calls,524.24s,TP0/FP0/FN14,macroF1=0,peak sampled llama RSS5.294GiB,no provider failure.010 changes only4→6 frames on same8 diagnostic windows;720p exports resized768x431/432. Timing provisional; no release pass.344 tests passed,4 skipped,final holdout test deselected. See new iterations/all-events-history.jsonl and latest implementation notes.

# Evaluation status

Last updated: 2026-09-12

For the dated, append-only implementation narrative and ordered next steps, see [`IMPLEMENTATION_NOTES.md`](IMPLEMENTATION_NOTES.md).

## Current decision

Latest source checkpoint (2026-09-12T17:18:58.740967+05:30): **Both720p-class owner exports verified and cached; download blocker resolved.** Game1 1280x718/30fps;game2 1280x720/25fps. Four sampled timing checks per game match zero offset. See studio-source-game1.json and studio-source-game2.json. No new inference. Next: all-event multi-output detector/scorer and timing audit, then frozen broad development evaluation. Keep resize/provenance explicit; third dataset sealed. Older statuses below are historical.

Latest source checkpoint (2026-09-12T17:10:04.600810+05:30): **game1 owner export acquired at1280x718/30fps; game2 browser export blocked**. Four sampled game1 alignment checks match zero time offset. New cache downloads/KBETdDRM70Q.studio-720p.mp4; baseline preserved. Game2 Studio Options→Download left open for owner manual click after ERR_BLOCKED_BY_CLIENT. No new inference; all-event detector/scorer remains pending. Third dataset sealed.

Latest owner scope correction (2026-09-12T17:02:18.680880+05:30): **All462 development labels are in scope; historical highlight-only scope is superseded.** Additive all-events-v2 reference ledger/manifest prepared with12 event/outcome categories and4 passing coverage tests. Broad evaluation NOT run; multi-event detector/scorer and timing audit still required. Owner confirmed uploader ownership; visible Google YouTube sign-in awaiting user. No inference running. Read latest notes before continuing; third dataset sealed.

Latest completed matrix (2026-09-12T16:55:40.791209+05:30): **007 and008 completed both development slices; quality still fails**. Retaining640x360 and then increasing3→5 central frames both yieldedTP0/FP0/FN2 per game. All22 provider calls succeeded, no observed crash/timeout; peak sampled model RSS5.613GiB. HD browser playback verified, no usable localHD export yet; uploader ownership clarification pending. Reference timing audit is now a priority alongside HD acquisition. Model unloaded; no inference running. Read newest implementation notes and preserved007/008 reports. Older statuses below are historical.

Current source-quality work (2026-09-12T16:42:38.357437+05:30): HD playback verified for both development games, but no local HD file acquired.007 game1 completed at native360p/3frames:TP0/FP0/FN2,6 successful calls,261.06s,peak sampled model RSS4.685GiB.007 game2 is running with the same configuration.008 planned5 central frames/context8192 at native360p. Source download route pending uploader-account clarification. Older entries below are historical; the holdout remains sealed.

Latest006 completed batch (2026-09-12T16:20:40.181919+05:30): **both local development slices completed despite memory warnings; recognition gate fails**.11/11 requests succeeded (7 vision,4 judge); no crashes/timeouts/provider errors. Total pipeline324.76s, peak sampled llama-server RSS4.69GiB. Both gamesTP0/FP0/FN2; recall0, precision/F1 undefined.007 may test denser core frames as a separately declared experiment; no full-game/holdout run. Warning-only aborts are superseded by the owner. Read006 full reports and latest implementation notes; older statuses below are historical.

Latest006 continuation (2026-09-12T16:17:46.446164+05:30): **game1 completed under memory warnings; game2 running**. Owner explicitly superseded warning-only aborts. Game1 completed six calls in194.70s without provider errors; TP0/FP0/FN2, recall0, precision/F1 undefined. Peak sampled llama-server RSS4.61GiB. This demonstrates a completed bounded run despite warnings; quality gate still fails. Previous002–005 aborts were monitor-policy outcomes, not observed crashes.

Latest refinement (2026-09-12T15:50:14.353575+05:30): **per-call checkpoints implemented;005 stopped during model loading, no observed crash**. Three-frame/context4096/batch128 probe stopped on memory pressure at24.58s; highest sampled llama-server RSS2.99GiB (not total physical peak). Journal preserved one started call and interruption; no returned tokens or completed classification. Sustained viability remains unproven;006/game2 not started. Read latest IMPLEMENTATION_NOTES and005 loading evidence. Existing quality baseline remains001.

Latest session (2026-09-12T14:17:14.239217+05:30): **003 and 004 stopped for memory pressure; no new completed accuracy results**. The unchanged game1 baseline stopped after 35.41s. A separately declared prompt-batch128 experiment stopped after 110.67s and is not a proven remedy. Model unloaded; game2 inference not started. Per-attempt execution JSON records and append-only notes/history preserve both failures. Offline verification: 326 passed, 4 skipped, 1 holdout test deselected. Next live run requires a revised memory plan and should retain per-call results before interruption. Third dataset remains sealed. Earlier status entries below are historical.

Latest continuation (2026-09-12T14:04:22.349901+05:30): **baseline 002 stopped for memory pressure; no new accuracy result**. Game1 vision inference was interrupted at macOS pressure level 2; model unloaded, pressure still elevated. Game2 is cached and preflighted but not evaluated. Attempt and limitations preserved in `iterations/ollama-development-002-game1.aborted.json`. Development recipe paths and generator relocation fixed, labels unchanged. Restore normal memory pressure before fresh serial baseline runs. Holdout remains sealed.

Latest update (2026-09-12 13:42 IST): **local execution works; basketball quality does not yet pass**. Ollama 0.33.3 and `qwen3-vl:4b-instruct` passed text/image smoke tests and completed four real development windows in 321.2 seconds. All four classifications were null: TP=0, FP=0, FN=2; recall=0%, temporal recall@0.30=0%, precision/F1 undefined under the current evaluator. Schema pass=100%, vision-provider error rate=0%. Candidate coverage@0.30=100% did not translate to event recognition. See the [preserved full report](iterations/ollama-development-001.report.json).

The local-only app is available while its process runs at `http://127.0.0.1:8502`; restart instructions are in [local setup](../docs/OLLAMA.md). No full-game rendering or holdout evaluation ran. Local API cost was $0; cumulative estimated cloud spend remains $2.53027.

Two earlier smoke tests with generic `qwen3-vl:4b` failed by output truncation; that tag selects the thinking variant. Their records remain alongside the successful explicit-Instruct smoke test. The evaluation's second text-judge attempt hit the five-call cap and the pre-existing graph fallback returned “accept.” This was not a quality pass; the deterministic metrics above remain the release criterion. A subsequent offline-tested fix makes local text errors propagate into the graph's “judge unavailable” feedback rather than silently returning empty text.

The Nebius account lists `Qwen/Qwen3.5-397B-A17B`, but direct tests returned HTTP 400 for both image and video input. See the [capability test record](iterations/qwen-nebius-capability-20260912.json). Brev/Cosmos remains deferred because credits are unavailable.

The development release gate is **not yet met**, so neither the full first-video run nor the sealed holdout has been executed.

The best tuned development slice was iteration 18:

| Metric | Result | Gate |
|---|---:|---:|
| Candidate recall at IoU 0.30 | 1.000 | 0.800 |
| Selected-event precision | 0.667 | 0.700 |
| Selected-event recall | 1.000 | 0.700 |
| Selection F1 | 0.800 | 0.700 |
| Selected-event recall at IoU 0.30 | 1.000 | 0.700 |
| Schema pass rate | 1.000 | 1.000 |

The clean independent slice from a different game was iteration 20:

| Metric | Result | Gate |
|---|---:|---:|
| Candidate recall at IoU 0.30 | 1.000 | 0.800 |
| Selected-event precision | 1.000 | 0.700 |
| Selected-event recall | 0.500 | 0.700 |
| Selection F1 | 0.667 | 0.700 |
| Selected-event recall at IoU 0.30 | 0.500 | 0.700 |
| Negative-window specificity | 1.000 | monitored |
| Schema pass rate | 1.000 | 1.000 |

The independent slice therefore fails the recall, F1, and temporal-recall gates. Iteration 21 tested an alternative-label verifier, regressed to zero recall, and was rejected; its behavior was reverted while its result remains in the audit trail.

## Cost status

- Cumulative estimated Nebius spend: **$2.53027**
- Hard cap: **$5.00**
- Remaining headroom: **$2.46973**

The cumulative source of truth is [`iterations/spend-ledger.json`](iterations/spend-ledger.json). It is never cleared between iterations.

## What has been accepted

- One-to-one, label-aware temporal matching.
- Candidate and selected-event recall at IoU 0.10, 0.30, and 0.50.
- Precision, recall, micro/macro F1, confusion matrices, balanced accuracy, specificity, average precision, calibration error, and threshold sweeps.
- Proposal-to-classification-to-selection funnel metrics.
- Centered clip shaping for long evidence windows.
- Dense action-frame sampling with explicit before/after context.
- Contrastive verification against rebounds, misses, and unforced turnovers.
- A recipe-level two-second separation between selected highlight fragments.
- Append-only iteration results with change notes, dataset hashes, code revision, provider usage, and cumulative spend.

## Current limitation

The evaluated Nebius vision model is `openbmb/MiniCPM-V-4_5`; this is not a claim that it is the account's only listed model. It has changed semantic verdicts across temperature-zero runs and has confused or rejected steals, rebounds, and made baskets. The present single-label clip schema also cannot represent two different events occurring inside one candidate window.

More prompt tuning against known timestamps risks overfitting. The immediate experiment is local Qwen3-VL Instruct using ordered frames. Native-video and multi-label temporal detection remain separate future work, not implemented capabilities of this adapter.

## Audit trail

- Human-readable cumulative table and decisions: [`iterations/iteration-log.md`](iterations/iteration-log.md)
- Append-only complete run records: [`iterations/history.jsonl`](iterations/history.jsonl)
- Cumulative provider cost: [`iterations/spend-ledger.json`](iterations/spend-ledger.json)
- Metric definitions and release gates: [`iterations/README.md`](iterations/README.md)
- Development golden datasets: [`golden/cases/development.pipeline.jsonl`](golden/cases/development.pipeline.jsonl)
- Sealed holdout dataset: [`holdout/`](holdout/)

## Next action

Executable continuation plan for another agent: [`AGENT_HANDOFF.md`](AGENT_HANDOFF.md).
It covers the 21 historical iterations, local baseline, both development datasets,
preflight checks, controlled experiments, metrics, and stop conditions.

Inspect whether ordered frames capture the full action, then compare a predeclared temporal-sampling configuration on fixed development slices with a sufficient (still bounded) text-judge call allowance. Do not tune to exact reference timestamps or treat the small null-output run as proof that all Qwen configurations fail. Record latency as well as accuracy: observed vision calls took 59–95 seconds each. Multi-label temporal detection remains unimplemented. Do not run full games until development gates pass. Keep the original $5 cloud ceiling with no cloud fallback; the holdout remains sealed.
