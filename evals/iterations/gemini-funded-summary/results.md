# Funded Gemini evaluation completed
Updated 2026-09-12T23:08:05.527570+05:30.

## Budget

User added$5GoogleAPIcredit and capped further evaluations at$2,reserving$3for demo. New estimated usage$0.208809;remaining evaluation allowance$1.791191. The cap is enforced before every request and retry. Total historical ledger$7.401104,including old reservations;historicalbaseline$7.192295was not reset. Account-wide billing/balance is not read by this script; other account activity is outside this local cap. The$2is a maximum,not a spend target.

Funded calls:028two video recoveries,026two image recoveries,025sixteen narration/extraction requests. All20generation calls completed without provider/schema errors or retries. No new model/environment download. Third golden dataset untouched. No inference remains running or scheduled.

## Full eight-window comparison

All14development references across12types now have scored coverage. Two windows have no annotations and are not independently verified negatives. The control is explicitly consolidated from successful024,027,028calls with source-report hashes; no failed reports or original strict results overwritten.

|Approach|TP|FP|FN|Precision|Recall|F1|
|---|---:|---:|---:|---:|---:|---:|
|MiniCPM direct historical|3|31|11|8.8%|21.4%|12.5%|
|Gemini direct video|5|8|9|38.5%|35.7%|37.0%|
|Gemini video + transcript|4|5|10|44.4%|28.6%|34.8%|

DirectGemini gains24.5percentagepointsF1 vs historicalMiniCPM on the same8windows. The transcript increases precision6.0points but loses7.1pointsrecall,F1falls2.3points. It emits9events versus13direct,including one fewer correct match. This is a small diagnostic,not production-ready quality or a statistical superiority claim.

|Category|Support|Direct Gemini TP/FP/FN|With transcript TP/FP/FN|
|---|---:|---|---|
|assist|1|0/0/1|0/0/1|
|block|1|0/0/1|0/0/1|
|defensive_rebound|1|0/1/1|1/1/0|
|free_throw_made|1|0/1/1|0/0/1|
|free_throw_miss|1|0/1/1|0/1/1|
|offensive_rebound|1|1/1/0|0/0/1|
|steal|1|1/1/0|1/1/0|
|three_point_made|1|0/0/1|0/0/1|
|three_point_miss|1|0/0/1|0/0/1|
|turnover|2|1/1/1|1/1/1|
|two_point_made|1|0/1/1|0/1/1|
|two_point_miss|2|2/1/0|1/0/1|

Neither arm matches assist,block,made/missedFT,made/missed3PT,or made2PT references. Both match the first steal/turnover pair. Directmatches both2PTmissreferences andOR;transcriptloses one2PTmissandOR,gainsDR. Identical labels at nearby times may still have wrong supporting team/sequence explanations. Do not present model confidence as accuracy.

## Confirmation

The missing image2/6calls passed strict JSON. Together with saved023image1and corresponding video calls, all3windows have valid paired confirmation. This is a staged comparison spanning runs,not a fresh simultaneous batch.

|Arm|TP|FP|FN|F1|
|---|---:|---:|---:|---:|
|gemini_images|2|0|8|33.3%|
|gemini_video|4|5|6|42.1%|
|historical_minicpm|3|13|7|23.1%|

## Transcript observations and limits

025uses oneGemininarrationper12secvideo at4fps,max12orderedobservations,then citation-linked extraction with the samevideo for verification. Same model,temp0,LOWthinking,HIGHmediaresolution,JSONmode and8192output cap as directcontrol. Extraction instructions are more explicit than the directprompt,so this tests a complete two-stage recipe,not isolated value of prose. NoYOLOin eitherGeminiarm.

All8transcripts and8extractionsparsed without repairs. Some narrations still assert statistical labels such as steal/defensive rebound despite the observation-only instruction; the structural parser does not certify that prose is visually grounded. Inwindow1the transcript changes ORtoDR relative to direct,but the shot outcome still conflicts with the madeFTreference. Inwindow5it emits no events,losing directmodel's matched2PTmiss. InCampuswindow6team/control interpretations change and the model swapsORforDR;matched counts do not establish correctness of those narratives. These are output-content audits,not newly audited ground truth.

Inwindow2the transcript describes the pass at762.75,catch764,layup765,andrimcontact765.5,while the fixed scored core ends764. This is model-reported timing,not a new annotation. It motivates investigating whether short scored windows/approximate reference times split an event sequence. No core intervals,labels,tolerance,or scores were changed after seeing this.

## Recommendation

Keep directGemini video as the current diagnostic baseline. Do not adopt generated transcripts: on full coverage they cost more and reduce recall/F1. Do not add genericYOLO yet:020balltracks cover8/1023frames,longest0.133s,and noCampusballtracks. These measurements do not rule out a specialized sports-trained detector,but current generictracks add little reliable temporal evidence.

Next bounded improvement: investigate context and shot-outcome visibility before another architecture switch. Freeze longer surrounding clips while retaining the same core/reference/scorer,then separately compare rim-detail views if outcomes remain ambiguous. Audit timestamp/core-boundary conflicts using existing footage without requesting new annotations or silently modifying HoopIQlabels. Measure pertype results and visual support,not narrative fluency. This next experiment is recommended,not running.

## Validation and artifacts

400tests passed,4skipped,1final-holdouttest deselected,1legacyGoogleSDKwarning. Seven new budget tests cover exactcap,overshoot,accumulatedreservations,ledgerreset,negative/nonfinite input;five retry tests remain. Pricing and token-based costs are estimates rather than Google invoices. No local crash; cloud memory unavailable.

Durable artifacts:gemini-funded-budget.json;028and026plans/rawresponses/checkpoints;gemini-development-summary/full-control.json;025plan,rawtranscripts,linkedoutputs,report;gemini-funded-summary/confirmation.json. Existing historical media hashes and originalsource hashes retained. Local originals/extractedmedia remain ignored byGit.

gemini-development-recovery-028: 20.73s elapsed,peak client RSS0.0787GiB,incremental estimated$0.021130.

gemini-images-recovery-026: 10.33s elapsed,peak client RSS0.0455GiB,incremental estimated$0.011153.

gemini-transcript-025: 120.00s elapsed,peak client RSS0.0786GiB,incremental estimated$0.176525.
