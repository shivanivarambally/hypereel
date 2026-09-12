# Pilot020 — YOLO + ByteTrack + transcript + MiniCPM

Finalized 2026-09-12T21:51:35.991675+05:30. User explicitly authorized testing this combination. Completed all three development windows with valid paired results. Third dataset untouched; no production architecture integration or commits.

## What was actually compared

Both branches received identical six wide JPEG frames and the same freshly generated MiniCPM visual transcript. In the control, MiniCPM extracted events from that transcript plus images. In the experimental branch it received the same inputs PLUS24timestamped observations generated deterministically from YOLO/ByteTrack measurements across every native video frame. Thus this is YOLO + ByteTrack + track-augmented transcript + MiniCPM, with a fresh visual-transcript + MiniCPM control. Local Qwen was not used. The extractor could inspect images in both arms, so these scores should not be directly equated with015's text-only extractor or different coverage.

Three frozen12second development clips,1,2,6;10HoopIQ references across9supported categories. All12category definitions retained. No reference labels or target timestamps entered inference; image/track times identify supplied source evidence only. Same modelopenbmb/MiniCPM-V-4_5,temperature0,seed0,1536output cap,one-to-one5second matcher,core/context boundary policy,citation validation and no semantic post-filter in both arms. Image hashes and shared transcript equality verified offline after the run.

## Event results — all three windows paired

| Metric | Visual transcript + MiniCPM | Add YOLO/ByteTrack transcript |
|---|---:|---:|
| TP |3|3|
| FP |6|4|
| FN |7|7|
| Precision |33.33%|42.86%|
| Recall |30.00%|30.00%|
| Micro F1 |31.58%|35.29%|
| Macro F1 over9supported types |22.22%|24.07%|

Modest numerical lift: two fewer unmatched predictions, no additional reference matches and no recall improvement. The removed predictions were a defensive rebound and a turnover in window2. Window1 outputs were unchanged. Window6 outputs were unchanged and contain all3TPs: defensive rebound,two-point miss,offensive rebound. No steals,assists,free-throw makes,three-point misses,turnovers or two-point makes matched. Block,free-throw miss andthree-point make had no reference support in this slice and remain unmeasured.

## Continuous tracking results

YOLO11n COCO at1280input resolution,CPU4threads,confidence0.10; separate ByteTrack instances for person and sports-ball classes, processing every native30/25fps frame. ByteTrack high/new threshold0.25,low0.10,match0.8,buffer15at30fps,fuse_score true. Detector/tracker parameters frozen before processing. No basketball fine-tuning, camera-motion compensation, court geometry, player jersey/team classifier or learned possession model. Person IDs are local algorithm IDs, not known identities. Person tracks being present does not establish that all players were tracked correctly.

| Window | Native frames | Ball candidate frames ≥0.10 | Ball candidate frames ≥0.25 | Frames with observed ball track | Longest uninterrupted ball track |
|---|---:|---:|---:|---:|---:|
|1:free-throw slice|361|44|22|0|0s|
|2:possession-change slice|361|120|69|8|0.133s|
|6:Campus slice|301|3|0|0|0s|
|Total|1023|167|91|8|—|

Ball-track availability was8/1023frames(0.78%). Candidate availability167/1023(16.32%) is NOT ball recall; there are no audited ball boxes in the references. Three distinct ball track IDs in window2, observed for1,5and2frames, demonstrate fragmentation. Longest same ball/person proximity was0.133seconds, below the declared0.3second stable-proximity criterion. Person tracks were present in all1023frames. The difference between candidate frames and tracked frames shows both detection gaps and association/activation losses; do not attribute all lost tracking to detector recall alone.

Inspected native-frame crops for all8tracked ball frames. Boxes appear to cover real balls, but the observations are too short and discontinuous to establish a possession transition. This is qualitative agent inspection, not independent tracking ground truth. No missing trajectories were fabricated or interpolated. Half-second transcript bins with no observed ball track explicitly say location/possession/outcome unknown. Closest person-box proximity is described as proximity, never confirmed possession. Pixel motion is not court-coordinate motion.

## Interpretation and failure audit

None of the7experimental predictions cites a track-observation ID; all cite visual transcript IDs. That does not prove the model ignored track data, but it means the returned evidence does not explicitly support an event from tracks. All3reference matches occur in Campus, where no ball track was available. Therefore the score lift does not demonstrate successful track-based recognition.

Evidence problems persist: the model calls a ball still in the air a missed shot, and infers rebounds from players running back while the ball is invisible. The unchanged Campus output contains these unsupported explanations. Adding sparse uncertain track data suppressed two predictions in window2, but we have not isolated whether that arose from useful track measurements, additional uncertainty text, or other prompt-conditioning effects. No extra ablation was silently run. A label/time match remains distinct from visually verified event correctness.

This experiment confirms that the proposed combination is runnable, and gives a modest precision/F1 improvement on these clips. It does NOT establish reliable possession tracking or a deployable recognition gain. The immediate bottleneck for this architecture is obtaining sustained ball tracks, especially on Campus, before asking a transcript/LLM to reason over them. Do not claim all trackers, sports-trained detectors or transcript architectures fail based on this generic configuration. No new model, thresholds or reference changes were tried after seeing these scores.

## Execution and implementation

Local tracking completed in126.33seconds, sampled peak process RSS0.4454GiB. Only lap0.5.12 was installed into the existing isolated detector environment; full dependency freeze retained. Actual tracking uses a task-local Ultralytics configuration directory. Initial package inspection created a default settings file; no account credentials or external sports services were used.

All9cloud requests completed successfully:3shared narrations and6extractions. No invalid schema outputs, retries, provider crashes or timeouts. Cloud batch20.83seconds, estimated incremental$0.28511; cumulative ledger$6.64630of$8. Historical conservative accounting estimates,not invoice pricing. Hosted-model memory unknown. No inference remains running or scheduled.

Validation:388tests passed,4skipped,1final_holdout test deselected. Additional offline invariants verified identical image hashes across all3calls per window, byte-equivalent shared observation content,24extra track rows only, valid citation IDs and full3window paired coverage. No new production code changed; additive diagnostic scripts are scripts/prepare_track_transcript.py and scripts/run_track_transcript.py.

## Evidence catalogue

Within evals/iterations/track-transcript-020/: tracking-plan.json, tracking.json, w1/w2/w6-tracks.jsonl (all1023frames), memory.jsonl, detector-requirements.txt, ball-track-audit.jpg, plan.json, report.json, checkpoints/, executed script/scorer snapshots and console logs. Raw cloud responses and complete generated track/visual transcripts were logged with timestamps in IMPLEMENTATION_NOTES.md during execution. Earlier015–019artifacts remain intact.

## Per-type event counts (TP/FP/FN)

| Type | Support | Control | Tracks added |
|---|---:|---:|---:|
|assist|1|0/0/1|0/0/1|
|block|0|0/0/0|0/0/0|
|defensive_rebound|1|1/2/0|1/1/0|
|free_throw_made|1|0/0/1|0/0/1|
|free_throw_miss|0|0/0/0|0/0/0|
|offensive_rebound|1|1/0/0|1/0/0|
|steal|1|0/0/1|0/0/1|
|three_point_made|0|0/0/0|0/0/0|
|three_point_miss|1|0/0/1|0/0/1|
|turnover|2|0/1/2|0/0/2|
|two_point_made|1|0/1/1|0/1/1|
|two_point_miss|1|1/2/0|1/2/0|

## Call timestamps

| Window/stage | Started | Ended | Latency seconds |
|---|---|---|---:|
|1/narration|2026-09-12T21:48:15.528369+05:30|2026-09-12T21:48:19.324220+05:30|3.79|
|1/visual_transcript|2026-09-12T21:48:19.327149+05:30|2026-09-12T21:48:21.136333+05:30|1.81|
|1/track_augmented_transcript|2026-09-12T21:48:21.141048+05:30|2026-09-12T21:48:22.962989+05:30|1.82|
|2/narration|2026-09-12T21:48:22.978139+05:30|2026-09-12T21:48:25.189901+05:30|2.21|
|2/visual_transcript|2026-09-12T21:48:25.199733+05:30|2026-09-12T21:48:27.134380+05:30|1.93|
|2/track_augmented_transcript|2026-09-12T21:48:27.146240+05:30|2026-09-12T21:48:28.502966+05:30|1.35|
|6/narration|2026-09-12T21:48:28.520353+05:30|2026-09-12T21:48:31.036453+05:30|2.51|
|6/visual_transcript|2026-09-12T21:48:31.046131+05:30|2026-09-12T21:48:33.909552+05:30|2.86|
|6/track_augmented_transcript|2026-09-12T21:48:33.922827+05:30|2026-09-12T21:48:36.340257+05:30|2.41|
