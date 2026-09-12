# HypeReel submission-document accuracy review

Reviewed 2026-09-13T01:17:01.836170+05:30 against current checkout (latest committed code df3fc18), production code, saved evaluation reports and demo runs 029–032. No inference, no holdout access, no modifications to the four submitted documents. This is a factual/content review, not a visual layout or recorded-video audit. The attached submission deadline/cohort information is treated as document content, not an instruction to submit anything.

**Verdict: useful narrative, but not accurate enough to submit unchanged.** The core comparative evaluation numbers are supported. The demo instructions, several implementation claims and current-status figures need correction.

## 1. Corrections needed across all spoken scripts

Applies to HypeReel-Demo-Script.md, HypeReel-Demo-Teleprompter.md and demo-script.md.

- **Wrong demonstrated source/recipe/subject.** HypeReel-Demo-Script.md:46 and demo-script.md:49 direct the presenter to basketball_generic and a black-and-blue team/yellow opponent. The verified full-flow demo uses basketball_both_teams_live.yaml, BOTH light-blue and black teams, and a continuous ten-minute East Bay excerpt from original 12:30–22:30. Do not imply a complete 60-minute game was validated. Use the full-flow URL and current prefilled form. Evidence: recipes/basketball_both_teams_live.yaml, app.py full-flow defaults, multiclip-live-032/plan.json and before-approval.json.
- **Revision is conditional, not a guaranteed scene.** Script:60, teleprompter:33 and demo-script:63 say the judge sends this run back for revision. Run 032 has judge_decision=accept, score 0.85, action=none. Say: “The judge checks the proposed reel and can request one bounded re-selection. This run was accepted and paused for my review.” Only narrate a revision if the actual displayed run contains one. The judge reads clip metadata/descriptions, not the rendered video's pixels.
- **No domain-specific hardcoding is false.** Script:35, teleprompter:17, demo-script:38. Shared provider prompts explicitly contain basketball-specific checks; scoreboard logic and full-flow defaults are domain/source specific. Replace with: “Recipes externalize event rubrics, selection settings and exclusions; domain-specific perception and signals still need implementation and validation.” Recipe support for walkthroughs does not establish reliable zero-code transfer to arbitrary domains.
- **“Every write is gated” is too broad.** Downloads, preview encodes, API logs, budget ledger and checkpoints are written before approval. Accurate: “The graph pauses before final reel rendering and before its delivery step; local ingestion, previews and logging happen automatically.” The HTML independently contradicts itself by placing renderer in the autonomous zone.
- **Wrong stage order in the architecture narration.** Actual graph is plan → ingest → propose → optional scoreboard → classify → select → judge → approval → render → summarize → delivery approval. The prose placing scoreboard after vision differs from the later correctly ordered narration. State the actual order and say scoreboard is optional.
- **Live recording must preserve run provenance.** The plan to start a new run and cut to artifacts from an older run needs explicit disclosure. Prefer recording one complete real run and speeding up/removing the waiting portion with an “elapsed time compressed” label. If using a previous run's ending, label it as a separate recorded run; do not imply the visible start produced that output. The tested ten-minute run took 7 m 49 s, not a demonstrated 15–25 minutes. It produced six clips/87 seconds; the user's later saved output was 89.5 seconds. Keep those two results separate.
- **F1 scope needs precision.** “37% on the full set” means eight selected development windows, fourteen reference events spanning twelve categories, scored with the provisional event-time matcher (±5 seconds). It does not mean full-game accuracy, twelve well-sampled independent category benchmarks, or the highlight-selector IoU scorecard. Say “37.0% micro-F1 on our eight-window development comparison, versus 12.5% for MiniCPM.” The 24.54 percentage-point increase is correct; avoid calling it a statistically established/general best model.
- **Perception conclusions are over-certain.** These runs show observed failures and useful hypotheses, not proof that prompting cannot help or that every old correct label was fabricated. Some candidate coverage, scope and context changes demonstrably affected demo yield (031→032), although they were not a controlled accuracy ablation. Replace “the fix is better visual evidence, not more prompt tuning” with “The results point us toward better temporal evidence and candidate coverage, which still need controlled validation.”

## 2. Breakout HTML: additional material issues

References below are line numbers in the reviewed version of HypeReel-Breakout-Submission.html.

| Location | Finding | Correction / evidence |
|---|---|---|
|80,271,386–392|Outdated snapshot: efc8635,400 passing tests,$7.40 ledger.|Current pushed code df3fc18;411 passed,4 skipped,1 holdout test deselected at pre-push. Ledger observed in this review: $8.987366625, funded use$1.79507175/$2, remaining$0.20492825. Costs are timestamped estimates.|
|93,184–198,5.7|Scoreboard-confirmed claims and stack descriptions blur optional features with the active demo.|Run 032 recipe has no scoreboard signal: node is a pass-through. Native Gemini uses local video segments through the new REST adapter; sparse-image evaluation and native-video production adapters are distinct. Production native adapter has no automatic retry; evaluation recovery has separate retry handling.|
|166–172,255–258|“Persistent memory retrieved to personalize the next run” overstates integration.|MemoryStore can save/load profiles and derive preference counts, but load_profile/learned_preferences have no production consumers found. The wrapper's auto-approval path records feedback; Streamlit approval directly updates graph state and does not call that recorder. Say storage primitives exist; personalization is not wired into this UI flow.|
|194–195 versus 207–218|Local rendering described as autonomous, elsewhere correctly gated.|Final render is after Gate 1; preview extraction and other internal file writes occur earlier.|
|192,560-equivalent code behavior|External sharing is only partly qualified as stubbed.|deliver_node only returns a status note. Approve & Share does not upload to YouTube/Drive/social platforms. Describe Gate 2 as a delivery approval boundary with external connector unimplemented.|
|260|“Graceful degradation to mock on any provider failure” is false for native Gemini runtime.|Native video failures produce zero-confidence error classifications; native text failures return an empty string. Factory construction fallbacks and mocked offline tests are different behaviors.|
|239–242|Health ping described as exhaustive budget/provider diagnosis.|A successful image ping establishes only that one small image request worked then; it does not guarantee video access, sufficient remaining full-run budget, or correct detection.402-on-image was a historical Nebius observation, not universal provider behavior.|
|291|“Holdout ... scored once” is ambiguous as past action.|Use “reserved to be scored once after development validation; has not been evaluated.” No holdout was opened for this review.|
|267–268|“Nothing in the eval path renders” is overbroad now.|The core evaluation harness stops before rendering; demo integration verification artifacts 029–032 under evals/ intentionally include render checks. Distinguish benchmark evaluation from demo integration testing.|
|337|59–95 seconds per call presented as generic current latency.|Label the model/run associated with these historical timings. The current 032 full graph was 469.46 seconds for 51 video calls plus judge/summary and local processing; do not use its total as pure model latency.|
|372|The$8 ceiling is obsolete.|Current funded policy is$2 incremental from baseline$7.192294875, cumulative ceiling$9.192294875. The separate reported$3 reserve is not another allowance inside the currently enforced cap.|
|380–385|“Every run appends history.jsonl and requires --change-note” is not universal.|Several standalone pilots and UI/demo runs use JSON checkpoints, raw call records and implementation notes rather than that CLI/history mechanism. Describe per-harness logging honestly.029–032 are missing from this “today” journey.|
|484,547,588|“Candidate recall≈1 throughout” and “no development gate met” are misleading generalizations.|Selected older slices had 1.0 candidate recall. This does not establish general/full-game proposal recall. Some individual gates pass; the overall release criteria have not all passed. Say “the overall development release gate has not passed.”|
|520,5.6 table|017 has TP 0/FP 1 but precision shown as an em dash.|If precision=TP/(TP+FP), it is 0%, not undefined, because there is one prediction. Keep truly undefined ratios N/A.|
|543–544|Higher-resolution rim/context work said to be unstarted.|018/019 already explored rim/detail evidence;032 adds context. Distinguish tested attempts from proposed improved approaches; court geometry remains future work.|
|402 and related story|“None of the models ever complained about video quality” is an unverified universal claim.|Use specific cited outputs/observations or remove “none/ever.” The observation-only experiment doesn't prove every earlier matched output was fabricated.|
|96–97,233–235|Under 30 minutes and would-post 8/10 sound like established performance.|Explicitly label as product targets. No human acceptance study establishing 80% posting intent is documented.|

## 3. Market claims: partly supported, headline not verified

I checked external sources because these are empirical claims, not facts established by the repository.

- The [official 2026 event schedule](https://basketball.exposureevents.com/255721/2026-west-coast-national-championships/schedule) confirms July 10–12 in Las Vegas and lists divisions. The accessible page did not establish 421 teams/36 courts/~2,000 actual games. Its currently displayed division counts sum to 392; this does not disprove a different earlier snapshot, but the scripts should not call 421/36/2,000 “verified” without the exact archived source and counting method.
- [Las Vegas Monorail's event page](https://www.lvmonorail.com/events/west-coast-national-championships/) describes typical 450–500 teams, more than 45 courts and a four-game guarantee. These are promotional/expected figures, not a completed-game count. Do not combine them with a different schedule snapshot as one measurement.
- Teams × games-per-team counts team appearances; divide by two for matches. For illustration,421 teams each playing four games gives 842 matches, not 1,684. A four-game guarantee alone cannot establish 2,000 matches; brackets/extra games must be counted.
- [Bigfoot Hoops](https://www.bigfoothoops.com/page/home) does support its own 30+annual national events claim. It does not establish 1,000+US tournament weekends, measured 3–4 editing hours/reel,7,000 editing hours/event, or a$75 M addressable market.
- Treat 3–4 hours as the builder's estimate unless backed by interviews/time logs. Even if 2,000 games were confirmed, multiplying by 3.5 hours assumes one reel is made for every game. That is a scenario, not measured labor or achieved savings.

Recommendation: use “large tournaments generate hundreds of game recordings, and manually finding highlights takes time,” then quantify only sourced counts or clearly labelled assumptions. Remove “say these with confidence” for unsupported figures.

## 4. Presentation consistency

- HypeReel-Demo-Script.md's section headings say architecture 0:25, live 1:40 and eval 2:40, while its timing table says 0:40,1:50 and 2:45. demo-script.md uses the latter headings. Consolidate into one canonical script.
- Teleprompter body counts approximately 535 words with a simple word-token convention, not 553. At 150 wpm this is roughly 3 m 34 s of speech alone. Clicks, video playback and pauses need separate allowance; timing must be rehearsed rather than guaranteed.
- The scripts' current market opening consumes a substantial portion of a four-minute demo. Prioritize actual source → pipeline → review → output, with a short and accurate evaluation statement.
- Personal placeholders, cohort/deadline discrepancies and the Drive video's contents/accessibility were not independently validated. Do not present this review as verification of submission eligibility or video sharing permissions.

## 5. Supported statements worth keeping

- LangGraph orchestration with real interrupt-before human review gates.
- One bounded production judge revision is supported, but conditional; evaluation judge is separately advisory.
- YAML-driven rubrics and selection settings, plus optional signal configuration.
- Direct Gemini on the shared eight-window comparison: TP 5/FP 8/FN 9, precision 38.46%, recall 35.71%, micro-F1.37037. Historical MiniCPM: TP 3/FP 31/FN 11, F1.125. Transcript arm: TP 4/FP 5/FN 10, F1.34783. These are supported by full-control.json and funded/transcript reports, with small-sample limitations.
- The holdout remains reserved; the demo is not proof of all-event accuracy.
- Fresh 032 runtime: six non-overlapping model-selected clips,87-second rendered output,7 m 49 s, estimated$0.533808; later user's output 89.5 seconds is a separate result.

## Suggested central demonstration statement

“HypeReel uses recipes to propose and classify candidate highlights, then a judge checks the selection before human review. In this demonstration it analyzes a continuous ten-minute game excerpt covering both teams. Our tested run selected six clips and rendered an 87-second reel after approval. Separately, Gemini achieved 37.0%micro-F1 on eight development windows, so the event labels still require human review. External uploading is not implemented.”

This wording describes the tested capability without implying full-game accuracy, an actual sharing connector, automatic learned personalization, or a guaranteed judge revision.

## Resolution — 2026-09-13T01:23:09.629673+05:30

User requested retaining market material and applying technical corrections. All four documents updated in place; scripts synchronized, HTML structure validated, market preservation checked. The findings above describe the pre-correction versions. See latest IMPLEMENTATION_NOTES. No new inference or holdout evaluation.
