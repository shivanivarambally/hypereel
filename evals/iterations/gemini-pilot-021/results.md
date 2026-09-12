# Gemini evaluation:021 and022
Updated 2026-09-12T22:36:14.743400+05:30.

Completed an image/video capability pilot and attempted a JSON integration confirmation. No production architecture change, YOLO or generated transcript in these Gemini arms. Third golden dataset untouched.

## Results

**021 primary strict result: six of six responses rejected because of outer Markdown JSON fences. No valid primary paired score.** A separate post-hoc formatting-only analysis removes exactly one enclosing fence symmetrically across all arms, with no event edits. Original report and its hash retained. All three windows then parse, covering10reference events across9of12types.

| Arm | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
|historical_minicpm|3|13|7|18.8%|30.0%|23.1%|
|images|2|0|8|100.0%|20.0%|33.3%|
|video|4|3|6|57.1%|40.0%|47.1%|

Gemini video improves F1 by24.0percentage points over cached MiniCPM direct013 on the same subset, with one additional match and ten fewer false positives. It misses6of10references. Image-only Gemini emits only two matched events;100% precision reflects two predictions and20% recall, not broad reliability. Compared with020 YOLO+track-transcript+MiniCPM F1.35294 on these three windows, video021 is numerically higher at.47059, but that is an architecture/prompt comparison, not a controlled model-only comparison.

## Event coverage

|Type|Support|MiniCPM TP/FP/FN|Gemini images TP/FP/FN|Gemini video TP/FP/FN|
|---|---:|---|---|---|
|assist|1|0/0/1|0/0/1|0/0/1|
|block|0|0/0/0|0/0/0|0/0/0|
|defensive_rebound|1|1/6/0|0/0/1|0/1/1|
|free_throw_made|1|0/0/1|0/0/1|0/0/1|
|free_throw_miss|0|0/0/0|0/0/0|0/1/0|
|offensive_rebound|1|0/0/1|0/0/1|1/0/0|
|steal|1|0/0/1|1/0/0|1/0/0|
|three_point_made|0|0/0/0|0/0/0|0/0/0|
|three_point_miss|1|0/0/1|0/0/1|0/0/1|
|turnover|2|0/0/2|1/0/1|1/1/1|
|two_point_made|1|1/3/0|0/0/1|0/0/1|
|two_point_miss|1|1/4/0|0/0/1|1/0/0|

## Interpretation and visual audit

Window2: both Gemini arms match the steal and turnover references. Inspected source frames759,760,761,762,763,764seconds: black controls the ball before a pass/contest; blue controls it by762 and advances. This supports a possession transition, but the image-arm758.8timestamp is early and its exact stripping explanation is not established. Five-second matching tolerance hides that timing imprecision. This is agent qualitative inspection, not a new audited annotation.

Window1: Gemini video says missed free throw plus defensive rebound, conflicting with the existing made-free-throw reference. Inspected227,227.5,228,228.25,229seconds: free-throw setup/release and ball near rim are visible, with players/ball below afterward. These sparse inspected instants do not conclusively resolve make versus miss or player24 possession. Keep original scoring and labels; do not relabel the reference or claim the model is correct to improve score.

Window6: video predicts turnover, two-point miss and offensive rebound. The latter two match the ledger; the turnover is a false positive under the unchanged matcher. Defensive rebound and three-point miss references remain missed. No independent frame audit of these new Campus predictions was performed this turn.

These three windows have no support for block, missed free throw or made three-pointer. A predicted missed FT can still be a false positive. Scores do not establish all12type performance or production readiness. Exact boundary/temporal-IoU claims remain unsupported.

## Integration fix and confirmation022

Added responseMimeType=application/json to the diagnostic adapter; semantic prompts, model, input media and other settings held constant. First image request succeeded and returned valid empty events. The next video request failed with HTTP503 UNAVAILABLE/high demand. Run stopped without retry; no paired confirmation score is available. This is a provider availability failure, not a local crash or a zero-quality result. Five planned outputs remain unconfirmed. No automatic follow-up run is scheduled.

The021 label in shared runner note headings is cosmetic:022 entries carry their022 plan and live in gemini-confirmation-022. Exact executed snapshots are saved in both iteration directories. A future run must get a new directory or explicitly preserve stopped artifacts, never overwrite them.

## Measurement and reproducibility

021:6inference calls plus6token-count preflights;85.46s elapsed; peak client RSS0.0726GiB; estimated incremental$0.047477.
022:2inference attempts plus2token-count preflights;43.39s; peak client RSS0.0586GiB; ledger increment$0.059307, including retained reservation for unknown503usage.
Combined ledger increment$0.106783; cumulative$6.753083/$8; remaining$1.246917. These are estimates/reservations, not billed charges. Hosted memory unknown; no local crash observed.

Model gemini-3.8-flash,temperature0,LOW thinking,8192output cap including thoughts,high media resolution. Gemini output cap/decoding differs from historical MiniCPM1536; model-only isolation is approximate despite exact image bytes and prompt reuse. Video uses original1280-wide muted12sec clips,explicit4fps; temporal sampling and effective resolution both change. API generation usage reported video/text tokens only; token-count preflight included an audio allowance despite muted files. Actual provider frame sampling is not independently observable.

REST adapter uses existing Python libraries; no new SDK or production provider modifications. Pricing verified from https://ai.google.dev/gemini-api/docs/pricing :$0.75/Minput,$3.75/Moutput including thinking at execution date. Input tokens counted before each call with25%input headroom plus capped output and$0.01margin reserved to shared ledger before network execution. Unknown usage retains reservation. No keys printed or saved in artifacts.

All prompts, media hashes, raw responses, model response metadata, usage and timings are in report.json and completed per-call checkpoints; original021 strict report remains intact and secondary results are in reparse.json. Full regression suite388passed,4skipped,1holdout-test deselected. Three unfencing checks passed. git diff --check clean. No commits.

## Next action

Complete a separately logged JSON-mode confirmation once provider capacity is available, retaining503artifacts and the budget reservation. If valid results retain this gain, expand the unchanged Gemini-video setup to the full eight development windows, covering all12event types. Do not switch architecture or add YOLO/transcript yet; first test whether the gain survives broader category coverage.
