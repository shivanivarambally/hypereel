# Iterations018–019: corrected rules and richer visual evidence

Updated 2026-09-12T21:37:57.009084+05:30. User authorized these next steps. Existing017 and earlier reports remain intact. No third-dataset access, no commits, no production application integration.

The corrected state rules and richer-input tests are complete. No reliable event-recognition improvement was demonstrated. Both runs completed with invalid windows, not machine crashes. Results below preserve missing coverage rather than treating invalid windows as event-free successes.

## Changes implemented before inference

Added versioned src/hypereel/evaluation/ball_state_v2.py, leaving017's module/snapshots intact. Explicit shot_release and pass_release replace ambiguous airborne-purpose inference. release_zone belongs to the shooter at release and cannot be overwritten by the ball's airborne position. A steal requires an explicit predicted interception and known prior opposing possession; an unexplained or unseen change is insufficient. An explicit missed state permits airball misses/rebounds without requiring rim contact; rim contact alone no longer proves a miss. Unknown gaps reset dependent state. Assist linkage requires an explicit pass, distinct known player identities and a made outcome within a declared8second heuristic; it is not official assist adjudication. Non-steal turnovers/violations are not fully covered by this contract. All12golden categories remain in scoring; unsupported capabilities are not removed from denominators.

A deterministic derivation is only as factual as its predicted states. Its confidence=1.0 is a legacy deterministic-rule marker, not a calibrated probability. No claim that a closed vocabulary prevents invented states or scoreboard influence is justified. Current release-zone perception is still model supplied; court homography was not implemented. Correcting the semantic meaning of zone is not the same as obtaining accurate geometry.

Ten new regression tests cover unknown gaps, explicit interception after passes, airballs, rim contact versus made outcome, zone retention, known-player assist linkage, context boundaries, timestamp validation, predeclared alternate serialization and chronological batch concatenation. Full suite388passed,4skipped,1final_holdout test deselected.

## Source inspection and input preparation

Used the three frozen development windows1,2,6 from both games:10HoopIQ reference events across9supported types. Core intervals remain223–231,756–764,1316–1324seconds; each has2seconds surrounding context. Source hashes unchanged. Extracted12second continuous clips at native resolution plus49timestamped frames per window at4fps (0.25second gaps; actual decoded frame times recorded). Agent inspected source-derived chronological sheets and native rim crops; this is not an independent human annotation of every source frame. No invented HD detail or source upscaling.

Wide images remain768pixels long-edge. Native320×320rim candidate crops use video-only manually selected backboard templates, multiscale template matching and a0.60threshold. Candidate counts before QA:46/49,2/49,49/49. Visual inspection found the early20Campus candidates matched advertising, not a backboard; those were rejected before any inference and preserved as rejected_crop records. This is a manually calibrated diagnostic cropper, not a validated deployable detector. Actual surviving crops:46,2,29. Native free-throw sequence shows ball flight and basket passage much more clearly; the decisive sample is around228.25seconds. Model matching to the HoopIQ point reference remains the original5second tolerance. No labels or target event times selected crop coordinates.

##018: separate wide/crop attachments

Fresh corrected-contract baseline:6wide frames across12seconds. Rich arm:49timestamps at4fps, batches of up to3timestamps, up to6attachments with same-time crops. The event deriver receives the concatenated chronological states across batches. No semantic state summary or extra model is used. Max54calls; no retries; two consecutive invalid batches stop that window; transport/budget errors stop the run.

Actual31calls,44.57seconds,$0.47711estimated.25valid and6invalid response batches. All3baseline windows completed withTP0/FP0/FN10. All3rich windows invalidated by at least one batch, so no paired complete-window comparison and no rich event score. Main failure: model returned separate state rows for wide and crop views at the same timestamp. Another failure assigned release_zone to a held row. Raw invalid output retained; no post-hoc repair.

##019: predeclared compatibility correction

One image per instant:1088×432canvas with768wide view left and optional320native rim crop right. Baseline uses exactly the same canvas with blank right side. Both arms batch up to3timestamps per request; state contract and derivation/scorer identical. This changes presentation and batching relative to018, so compare019arms directly, not as a pure crop-only ablation against018. Internal model resizing remains unknown.

Actual50calls,67.32seconds,$0.82196estimated.44valid and6invalid response batches. Model still occasionally returned wrong row counts; required release-zone placement also failed in one window. Baseline windows1and2completed; Campus baseline invalid. Dense window2completed; free-throw andCampus dense windows invalid. Only window2 is fully paired:4references (assist,steal,turnover,two-point make). Both armsTP0/FP0/FN4,recall0,microF1=0; precision undefined because there were no predictions. Do not call this full10reference or all12type coverage.

## Perception audit and interpretation

Retained valid rows inside invalid windows are diagnostic observations, not scored completed sequences.019's dense free-throw row at227.5s says shot_release,beyond_arc although the native crop shows the ball already airborne and source setup is a free throw. At228.25s the crop shows basket passage, but output is in_flight. At759s the model correctly reports held by black; at761s it calls blue ball handling a shot release despite the midcourt context. Broader native-context inspection corroborates ongoing visual errors. Exact shot-release timing and identities are not newly reannotated or substituted into HoopIQ references.

The017 statement that its through_net@229.4 was a correct observation also needs qualification: inspecting its actual supplied w1-dense4.jpg shows players handling the ball below the basket, not a supported visible through-net observation. A model state claim is not direct visual measurement. Preserve017's scored result; this is a later evidence audit, not a retroactive label change.

There is useful progress in failure isolation: the deriver no longer makes the reproduced logical mistakes; richer crops expose usable visual detail; separate-view formatting failure is reproducible; MiniCPM still misreads the action and cannot reliably satisfy this state contract even with one image per instant. The result does not prove all vision models or all tracking systems fail. It provides no basis to claim recognition improved or to scale this configuration to full games.

## Operations and next decision

Total81fresh provider requests across both iterations, no automatic retries, no provider crashes/timeouts;12invalid response batches. Incremental conservative estimated spend$1.29907; cumulative$6.36119 of authorized$8. Per-call sampled local client peak about0.0943GiB; hosted model memory is unknown. Preparation peak was not measured. No inference remains running or scheduled.

Recommendation: stop further MiniCPM prompt/format tuning for this configuration. Retain corrected rules, source crops, frozen references and evidence catalogue. The next useful comparison is a different perception component tested on these same retained visible sequences, with primitive correctness and schema reliability measured before event integration. A sports-trained detector/tracker or another video model needs a separately frozen capability comparison; neither was silently substituted here. Full court calibration and reliable release-zone assignment remain unresolved. No additional implementation or paid run beyond019 is scheduled.

## Reproducibility

Plans, preparation manifests, raw completions, checkpoints, source hashes, timestamps, usage, memory/pressure samples and executed code snapshots: evals/iterations/evidence-state-018/ and evidence-state-019/. New scripts: prepare_state_evidence.py, prepare_rim_crops.py, run_state_evidence.py, prepare_state_composites.py, run_state_composites.py. New tests: tests/test_ball_state_v2.py. Raw output from every call is appended to IMPLEMENTATION_NOTES.md. Historical data is not overwritten.

## 019 per-type metrics on the common completed window

| Type | Support | Sparse TP/FP/FN | Dense TP/FP/FN |
|---|---:|---:|---:|
| assist | 1 | 0/0/1 | 0/0/1 |
| block | 0 | 0/0/0 | 0/0/0 |
| defensive_rebound | 0 | 0/0/0 | 0/0/0 |
| free_throw_made | 0 | 0/0/0 | 0/0/0 |
| free_throw_miss | 0 | 0/0/0 | 0/0/0 |
| offensive_rebound | 0 | 0/0/0 | 0/0/0 |
| steal | 1 | 0/0/1 | 0/0/1 |
| three_point_made | 0 | 0/0/0 | 0/0/0 |
| three_point_miss | 0 | 0/0/0 | 0/0/0 |
| turnover | 1 | 0/0/1 | 0/0/1 |
| two_point_made | 1 | 0/0/1 | 0/0/1 |
| two_point_miss | 0 | 0/0/0 | 0/0/0 |

Zero-support types are unmeasured in this paired subset, not passing.

## 018 call catalogue

| Window/arm/batch | Start | End | Status |
|---|---|---|---|
| 1/sparse_wide/0 | 2026-09-12T21:32:17.761126+05:30 | 2026-09-12T21:32:21.647117+05:30 | valid |
| 1/dense_rim/0 | 2026-09-12T21:32:21.667340+05:30 | 2026-09-12T21:32:23.443216+05:30 | invalid |
| 1/dense_rim/1 | 2026-09-12T21:32:23.460997+05:30 | 2026-09-12T21:32:25.511553+05:30 | invalid |
| 2/sparse_wide/0 | 2026-09-12T21:32:25.531731+05:30 | 2026-09-12T21:32:27.310006+05:30 | valid |
| 2/dense_rim/0 | 2026-09-12T21:32:27.330845+05:30 | 2026-09-12T21:32:28.693022+05:30 | valid |
| 2/dense_rim/1 | 2026-09-12T21:32:28.709702+05:30 | 2026-09-12T21:32:29.990984+05:30 | valid |
| 2/dense_rim/2 | 2026-09-12T21:32:30.009067+05:30 | 2026-09-12T21:32:31.272136+05:30 | valid |
| 2/dense_rim/3 | 2026-09-12T21:32:31.291113+05:30 | 2026-09-12T21:32:32.440229+05:30 | valid |
| 2/dense_rim/4 | 2026-09-12T21:32:32.454728+05:30 | 2026-09-12T21:32:33.644038+05:30 | valid |
| 2/dense_rim/5 | 2026-09-12T21:32:33.660399+05:30 | 2026-09-12T21:32:34.803904+05:30 | valid |
| 2/dense_rim/6 | 2026-09-12T21:32:34.819817+05:30 | 2026-09-12T21:32:36.109012+05:30 | valid |
| 2/dense_rim/7 | 2026-09-12T21:32:36.124849+05:30 | 2026-09-12T21:32:37.302942+05:30 | valid |
| 2/dense_rim/8 | 2026-09-12T21:32:37.324267+05:30 | 2026-09-12T21:32:38.498103+05:30 | valid |
| 2/dense_rim/9 | 2026-09-12T21:32:38.515666+05:30 | 2026-09-12T21:32:39.737420+05:30 | valid |
| 2/dense_rim/10 | 2026-09-12T21:32:39.755533+05:30 | 2026-09-12T21:32:40.945476+05:30 | valid |
| 2/dense_rim/11 | 2026-09-12T21:32:40.963449+05:30 | 2026-09-12T21:32:42.167741+05:30 | valid |
| 2/dense_rim/12 | 2026-09-12T21:32:42.186980+05:30 | 2026-09-12T21:32:43.343910+05:30 | valid |
| 2/dense_rim/13 | 2026-09-12T21:32:43.363541+05:30 | 2026-09-12T21:32:44.646873+05:30 | invalid |
| 2/dense_rim/14 | 2026-09-12T21:32:44.666013+05:30 | 2026-09-12T21:32:46.007480+05:30 | valid |
| 2/dense_rim/15 | 2026-09-12T21:32:46.027039+05:30 | 2026-09-12T21:32:47.486541+05:30 | invalid |
| 2/dense_rim/16 | 2026-09-12T21:32:47.505135+05:30 | 2026-09-12T21:32:48.085860+05:30 | valid |
| 6/sparse_wide/0 | 2026-09-12T21:32:48.113243+05:30 | 2026-09-12T21:32:49.964775+05:30 | valid |
| 6/dense_rim/0 | 2026-09-12T21:32:49.991551+05:30 | 2026-09-12T21:32:51.273430+05:30 | valid |
| 6/dense_rim/1 | 2026-09-12T21:32:51.293891+05:30 | 2026-09-12T21:32:52.499523+05:30 | valid |
| 6/dense_rim/2 | 2026-09-12T21:32:52.519700+05:30 | 2026-09-12T21:32:53.929087+05:30 | valid |
| 6/dense_rim/3 | 2026-09-12T21:32:53.949112+05:30 | 2026-09-12T21:32:55.374749+05:30 | valid |
| 6/dense_rim/4 | 2026-09-12T21:32:55.397622+05:30 | 2026-09-12T21:32:56.613524+05:30 | valid |
| 6/dense_rim/5 | 2026-09-12T21:32:56.633816+05:30 | 2026-09-12T21:32:57.868110+05:30 | valid |
| 6/dense_rim/6 | 2026-09-12T21:32:57.887223+05:30 | 2026-09-12T21:32:59.134434+05:30 | valid |
| 6/dense_rim/7 | 2026-09-12T21:32:59.157541+05:30 | 2026-09-12T21:33:01.347133+05:30 | invalid |
| 6/dense_rim/8 | 2026-09-12T21:33:01.369106+05:30 | 2026-09-12T21:33:02.308197+05:30 | invalid |

## 019 call catalogue

| Window/arm/batch | Start | End | Status |
|---|---|---|---|
| 1/sparse_wide/0 | 2026-09-12T21:34:02.884964+05:30 | 2026-09-12T21:34:05.500444+05:30 | valid |
| 1/sparse_wide/1 | 2026-09-12T21:34:05.515094+05:30 | 2026-09-12T21:34:06.914385+05:30 | valid |
| 1/dense_rim/0 | 2026-09-12T21:34:06.934186+05:30 | 2026-09-12T21:34:08.311656+05:30 | valid |
| 1/dense_rim/1 | 2026-09-12T21:34:08.327697+05:30 | 2026-09-12T21:34:09.533350+05:30 | valid |
| 1/dense_rim/2 | 2026-09-12T21:34:09.554542+05:30 | 2026-09-12T21:34:10.780839+05:30 | valid |
| 1/dense_rim/3 | 2026-09-12T21:34:10.797556+05:30 | 2026-09-12T21:34:12.733730+05:30 | invalid |
| 1/dense_rim/4 | 2026-09-12T21:34:12.752337+05:30 | 2026-09-12T21:34:13.933912+05:30 | valid |
| 1/dense_rim/5 | 2026-09-12T21:34:13.951278+05:30 | 2026-09-12T21:34:15.171858+05:30 | valid |
| 1/dense_rim/6 | 2026-09-12T21:34:15.187693+05:30 | 2026-09-12T21:34:16.406847+05:30 | valid |
| 1/dense_rim/7 | 2026-09-12T21:34:16.424828+05:30 | 2026-09-12T21:34:17.653934+05:30 | valid |
| 1/dense_rim/8 | 2026-09-12T21:34:17.671404+05:30 | 2026-09-12T21:34:18.903154+05:30 | valid |
| 1/dense_rim/9 | 2026-09-12T21:34:18.921617+05:30 | 2026-09-12T21:34:20.179438+05:30 | valid |
| 1/dense_rim/10 | 2026-09-12T21:34:20.197099+05:30 | 2026-09-12T21:34:21.409766+05:30 | valid |
| 1/dense_rim/11 | 2026-09-12T21:34:21.429171+05:30 | 2026-09-12T21:34:23.419162+05:30 | invalid |
| 1/dense_rim/12 | 2026-09-12T21:34:23.439158+05:30 | 2026-09-12T21:34:24.640108+05:30 | valid |
| 1/dense_rim/13 | 2026-09-12T21:34:24.659553+05:30 | 2026-09-12T21:34:26.613893+05:30 | invalid |
| 1/dense_rim/14 | 2026-09-12T21:34:26.632893+05:30 | 2026-09-12T21:34:27.862764+05:30 | valid |
| 1/dense_rim/15 | 2026-09-12T21:34:27.883197+05:30 | 2026-09-12T21:34:29.110264+05:30 | valid |
| 1/dense_rim/16 | 2026-09-12T21:34:29.127370+05:30 | 2026-09-12T21:34:29.727654+05:30 | valid |
| 2/sparse_wide/0 | 2026-09-12T21:34:29.752113+05:30 | 2026-09-12T21:34:30.962163+05:30 | valid |
| 2/sparse_wide/1 | 2026-09-12T21:34:30.980663+05:30 | 2026-09-12T21:34:32.532489+05:30 | valid |
| 2/dense_rim/0 | 2026-09-12T21:34:32.556868+05:30 | 2026-09-12T21:34:33.763555+05:30 | valid |
| 2/dense_rim/1 | 2026-09-12T21:34:33.783059+05:30 | 2026-09-12T21:34:35.001438+05:30 | valid |
| 2/dense_rim/2 | 2026-09-12T21:34:35.020556+05:30 | 2026-09-12T21:34:36.211065+05:30 | valid |
| 2/dense_rim/3 | 2026-09-12T21:34:36.232003+05:30 | 2026-09-12T21:34:37.431487+05:30 | valid |
| 2/dense_rim/4 | 2026-09-12T21:34:37.445972+05:30 | 2026-09-12T21:34:38.652315+05:30 | valid |
| 2/dense_rim/5 | 2026-09-12T21:34:38.672970+05:30 | 2026-09-12T21:34:39.891192+05:30 | valid |
| 2/dense_rim/6 | 2026-09-12T21:34:39.910939+05:30 | 2026-09-12T21:34:41.131149+05:30 | valid |
| 2/dense_rim/7 | 2026-09-12T21:34:41.151761+05:30 | 2026-09-12T21:34:42.356637+05:30 | valid |
| 2/dense_rim/8 | 2026-09-12T21:34:42.376523+05:30 | 2026-09-12T21:34:43.588583+05:30 | valid |
| 2/dense_rim/9 | 2026-09-12T21:34:43.608647+05:30 | 2026-09-12T21:34:44.910072+05:30 | valid |
| 2/dense_rim/10 | 2026-09-12T21:34:44.931717+05:30 | 2026-09-12T21:34:46.126901+05:30 | valid |
| 2/dense_rim/11 | 2026-09-12T21:34:46.147197+05:30 | 2026-09-12T21:34:47.390630+05:30 | valid |
| 2/dense_rim/12 | 2026-09-12T21:34:47.411525+05:30 | 2026-09-12T21:34:48.621707+05:30 | valid |
| 2/dense_rim/13 | 2026-09-12T21:34:48.642258+05:30 | 2026-09-12T21:34:49.860691+05:30 | valid |
| 2/dense_rim/14 | 2026-09-12T21:34:49.880667+05:30 | 2026-09-12T21:34:51.078080+05:30 | valid |
| 2/dense_rim/15 | 2026-09-12T21:34:51.100408+05:30 | 2026-09-12T21:34:52.353005+05:30 | valid |
| 2/dense_rim/16 | 2026-09-12T21:34:52.374336+05:30 | 2026-09-12T21:34:52.973436+05:30 | valid |
| 6/sparse_wide/0 | 2026-09-12T21:34:53.001621+05:30 | 2026-09-12T21:34:54.259472+05:30 | valid |
| 6/sparse_wide/1 | 2026-09-12T21:34:54.280413+05:30 | 2026-09-12T21:34:55.481881+05:30 | invalid |
| 6/dense_rim/0 | 2026-09-12T21:34:55.511080+05:30 | 2026-09-12T21:34:56.771222+05:30 | valid |
| 6/dense_rim/1 | 2026-09-12T21:34:56.792817+05:30 | 2026-09-12T21:34:58.058245+05:30 | valid |
| 6/dense_rim/2 | 2026-09-12T21:34:58.080827+05:30 | 2026-09-12T21:34:59.545703+05:30 | valid |
| 6/dense_rim/3 | 2026-09-12T21:34:59.570388+05:30 | 2026-09-12T21:35:00.844651+05:30 | valid |
| 6/dense_rim/4 | 2026-09-12T21:35:00.867669+05:30 | 2026-09-12T21:35:02.130720+05:30 | valid |
| 6/dense_rim/5 | 2026-09-12T21:35:02.155515+05:30 | 2026-09-12T21:35:03.536131+05:30 | valid |
| 6/dense_rim/6 | 2026-09-12T21:35:03.558392+05:30 | 2026-09-12T21:35:04.787649+05:30 | valid |
| 6/dense_rim/7 | 2026-09-12T21:35:04.812906+05:30 | 2026-09-12T21:35:06.092875+05:30 | valid |
| 6/dense_rim/8 | 2026-09-12T21:35:06.119085+05:30 | 2026-09-12T21:35:08.135223+05:30 | invalid |
| 6/dense_rim/9 | 2026-09-12T21:35:08.158657+05:30 | 2026-09-12T21:35:10.170872+05:30 | invalid |
