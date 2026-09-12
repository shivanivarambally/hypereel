# Gemini broader development evaluation — partial
Updated 2026-09-12T22:51:12.553566+05:30.

**Blocked by the project/model daily free-tier request quota. Six of eight windows are valid in strict JSON mode; eight of twelve reference categories have support in these completed windows. Full confirmation and all12category evaluation remain unfinished.**

## Measured results on the same completed subset

|Arm|TP|FP|FN|Precision|Recall|F1|
|---|---:|---:|---:|---:|---:|---:|
|historical_minicpm|1|25|7|3.8%|12.5%|5.9%|
|gemini_video|3|4|5|42.9%|37.5%|40.0%|

This subset contains8reference events across8types, not all14references. Gemini matches a steal, turnover and two-point miss. It misses made/missed free throws, assist, made two-pointer and block references. Two unannotated windows return no events; they are not independently audited true negatives. Earlier three-window47.1%F1 is a different subset and post-hoc formatting analysis, not a trend directly comparable to this40%F1.

|Type|Reference support in completed subset|Gemini TP/FP/FN|
|---|---:|---|
|assist|1|0/0/1|
|block|1|0/0/1|
|defensive_rebound|0|0/1/0|
|free_throw_made|1|0/1/1|
|free_throw_miss|1|0/1/1|
|offensive_rebound|0|0/1/0|
|steal|1|1/0/0|
|three_point_made|0|0/0/0|
|three_point_miss|0|0/0/0|
|turnover|1|1/0/0|
|two_point_made|1|0/0/1|
|two_point_miss|1|1/0/0|

Zero reference support means unmeasured recall, not success or failure. Defensive rebound, offensive rebound, missed three-pointer and made three-pointer need the remaining windows6/7. False positive predictions of unsupported types still count.

## Execution and failures

023confirmation: first image/video window valid; next image request503twice, stopped.024broader: video0/1/2valid; video3failed503twice.027recovery: video3/4/5valid; video6failed429daily quota, including one retry under the previous generic transient policy. All failed attempts and their reservations remain recorded. No model changed to bypass this obstacle.

Returned quota ID is GenerateRequestsPerDayPerProjectPerModel-FreeTier; quotaValue20; modelgemini-3.8-flash. Despite a23-second RetryInfo, the violation is daily quota. Do not repeatedly retry after23seconds. Added a tested retry policy that stops on daily quota, honors minute-level retry delays with2secondsheadroom and caps singlewait60seconds. This change affects future diagnostic requests; past artifacts are unchanged.

Official Google documentation https://ai.google.dev/gemini-api/docs/rate-limits states daily request quotas reset at midnight Pacific time and are perproject, not perkey. For thisSep12run, next reset is Sep13at12:30PMAsia/Kolkata. Alternatively enable paid billing/quota for the same project; no billing/account purchase was performed. Changing API keys in this same project does not reset quota.

Ledger$7.192295/$8; remaining$0.807705. This turn increment$0.439212, including reservations for failed calls; not billed spend.
- 023: 4 generation attempts,2 valid outputs,78.59s elapsed,peak client RSS0.0687GiB,ledger increment$0.110581.
- 024: 6 generation attempts,3 valid outputs,182.27s elapsed,peak client RSS0.0891GiB,ledger increment$0.191299.
- 027: 5 generation attempts,3 valid outputs,63.41s elapsed,peak client RSS0.0876GiB,ledger increment$0.137331.

No local crashes; hosted-memory unknown. Sources and all eight muted720pclips hashed and probed. All completed outputs strictJSON,no formatting reparse. No production integration or holdout access.

## Recommended improvement sequence

1. Finish missing video6/7 and image2/6 under restored quota, then consolidate with provenance. Use successful023image1 and024/027video outputs for explicitly staged confirmation. Do not silently call that a fresh simultaneous paired run.
2. Run prepared025Gemini video plus generated transcript: narration of observable changes followed by citation-linked extraction that can verify the same video. Same8clips and scoring;16plannedcalls. This is worth testing because direct outputs confuse shot outcomes and team-relative rebound types. It may also compound hallucinations, so no improvement is assumed. Compare valid coverage, pertype metrics, latency and cost; do not simply report narrative detail as quality.
3. Defer genericYOLO+Gemini: prior020balltracking observed only8/1023frames,max0.133second continuity,with noCampusballtracks. This is too little evidence to justify adding that particular detector/tracker as a prerequisite. A sports-trained ball detector could still help, but first measure sustained ball detection/tracking on these source clips before anotherLLMcombination.
4. If transcript adds no reliable recall, test one evidence change: longer surrounding video context with the same scored core, to capture pass-shot-outcome and miss-control sequences across clip edges. Separately test closer rim views for unresolved shot outcomes. Keep these changes separate and freeze comparisons before calls. Do not alter HoopIQlabels or scoring to manufacture a gain.
5. Treat confidence as uncalibrated. Current wrong or reference-conflicting predictions can carry0.85–0.95confidence. Any confidence threshold requires a separately declared development analysis and broad validation, not a score-based post-hoc filter.

## Exact continuation

No inference running or scheduled. Restore same-project Gemini quota. Run gemini-images-recovery-026 plan for missing2/6images. Create a new recovery iteration for video6/7, using run_gemini_development.py --output-name <new-name> --indices6,7 --armsvideo with a saved plan. Preserve all stopped reports. Compile full eight valid video calls with exactsource hashes into a new consolidated report, then point GEMINI_CONTROL_REPORT at that report for scripts/run_gemini_transcript.py.025script is prepared but unexecuted. It refuses an incomplete control. Its plan will freeze at startup, and the spend ledger remains shared.

Tests: existing regression suite388passed before quota-handler addition. Five new regression cases verify dailyquota never retries, transient503backoff, minutequota RetryInfo,401stop and longcooldownstop. Initial test import fromscripts failed during collection; helper was moved into hypereel.evaluation and imports corrected before rerun. See027tests.log for final fullsuite.

Final validation:393passed,4skipped,1holdout-test deselected;git diff --check clean.
