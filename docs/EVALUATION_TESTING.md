# Evaluation testing and continuation

**Current checkpoint — 16 September 2026:** Iteration 055 tested 100 contiguous windows over 10:00–26:40 of game 1, discovery-only at 8 fps: TP41/FP89/FN57, precision .315, recall .418, F1 .360 against 98 externally labeled events. This is window-label matching on one development segment, not exact timestamp or full-game accuracy. The 462-row golden set covers both development games; the older six-label tests were a limited adjudicated subset. Third-game holdout remains sealed. [Current status](../evals/STATUS.md) and [publication review](REVIEW_2026-09-16.md) supersede older continuation instructions below.

Reproduce the broader result offline (use a new output filename; existing reports are not overwritten):

```sh
.venv/bin/python scripts/score_against_golden.py \
  --report evals/iterations/proposer-sweep-055/report.json \
  --boundary half-open --out my-055-replay.json
```

Half-open `[start, end)` windows prevent duplicate reference counts at tile boundaries. Explicit game IDs avoid interpreting sweep window numbers as legacy W1–W7 cases. The saved publication replay is `evals/iterations/publication-audit-056.json`; no provider calls are needed. Source labels and later human adjudications are distinct evidence tracks: do not silently replace either or compare their metrics without stating the reference policy.


Start with `../evals/AGENT_HANDOFF.md`. Timestamped observations are in
`../evals/IMPLEMENTATION_NOTES.md`; `../evals/iterations/CATALOGUE.md` indexes runs.

## Offline regression validation

From the repository root with the development environment installed:

```sh
.venv/bin/pytest -o addopts='' -q -k 'not final_holdout'
git diff --check
```

The final-holdout test is deliberately excluded. Do not inspect or evaluate the
third golden dataset. The new Gemini retry-policy cases verify that a daily-quota
error is terminal even when RetryInfo suggests a short delay; minute-level rate
limits and transient503errors permit bounded backoff. The Gemini diagnostic
adapters use standard-library HTTP, not the legacy production Gemini SDK.

## Historical partial live evidence (superseded)

Gemini023confirmation was interrupted by503capacity failures.024and027provide
strict-valid direct-video outputs for development windows0–5. Their immutable
source reports are combined in
`../evals/iterations/gemini-development-summary/report.json`.
This is partial:8references across8supported categories,not the full14references
and12categories. GeminiTP3/FP4/FN5,F1.40; historical MiniCPM on that same subset
TP1/FP25/FN7,F1.05882. Do not compare these directly to the earlier three-window
47.1%F1 or call incomplete windows false negatives.

The next video windows are6and7; missing image confirmation windows are2and6.
026records the planned image recovery.025contains the planned generated-transcript
comparison, with no inference run. Its runner requires a complete8-window control.

## Live continuation requirements

The recorded project/model free-tier dailyquota20was exhausted. Restore API quota
before any further inference. Do not create new keys to evade project quotas or
retry the short RetryInfo on a daily limit. Authentication alone does not establish
available generation quota. Keep credentials only in the local ignored `.env`.

Keep the cumulative$8ceiling and existing ledger. Reserve cost before every request,
including a retry; unknown usage retains its reservation. Never run two spend-ledger
writers concurrently. Freeze model, input hashes, prompts, settings and selected
windows in a new iteration plan before inference. Preserve stopped and original
strict reports. Any consolidation must identify source reports and hashes.

The diagnostic runner accepts `--output-name`, `--indices` and `--arms` for explicit
recovery; create its new output directory and plan first. Do not reuse an existing
report path. The transcript runner accepts `GEMINI_CONTROL_REPORT` pointing to a
complete consolidated control report. Its planned16calls and any transient retry
must still pass the shared budget check. Prepared code is not a measured result.

## Repository artifacts

Code, tests, notes, development references, plans, hashes, raw model responses,
checkpoints and compact audit images are versioned. Downloaded videos, extracted
frame directories, detector weights, environments, credentials and `work/` scratch
remain local. Live reproduction requires the original two downloaded development
videos and prepared media; the saved hashes identify them. Offline regression tests
do not require uploading media or consuming API quota. No holdout run or model
quality certification is implied by passing unit tests.

## Commit validation checkpoint

393tests passed,4skipped,1holdout-test deselected in4.24seconds. One legacyGoogleSDKdeprecation warning. Staged credential scan passed. Raw console-log whitespace is preserved through a log-only .gitattributes rule; source/document whitespace checks remain active. No live inference was executed for commit validation.


## Latest checkpoint — Demo 029 ready — 2026-09-12T23:43:06.544495+05:30

Live app now uses opt-in Gemini native video with a prefilled real 40-second East Bay excerpt. Production graph generated and verified a real 11.5-second MP4, score 0.66. Dedicated recipe retains minimum score 0.50. This known-action demo is not a new benchmark result; no holdout, YOLO or transcript used. 405 tests passed, 4 skipped, 1 holdout deselected; additional UI smoke passed and live form verified. Ledger $7.428182; funded usage $0.235887/$2. See evals/iterations/demo-integration-029/results.md and latest IMPLEMENTATION_NOTES for evidence and runtime requirements. App running at http://127.0.0.1:8501/?demo=ready; no automated evaluation scheduled.

---

## Approval preview completion — 2026-09-12T23:45:39.646237+05:30

User identified that text-only approval was unusable and requested the gap be filled. Gate 1 now plays each proposed segment from the actual local source beside its Keep control, retaining event label, exact timestamps, score and model reason. Player bounds round outward to whole seconds (Streamlit precision), providing up to one second of extra context per edge; the renderer still uses exact clip boundaries. No additional inference or intermediate video encoding is required. Missing source blocks approval; deselecting every clip disables rendering. Gate 2 plays the rendered reel and offers an MP4 download before sharing; missing render disables sharing. Completed reels remain playable on the Done screen. Previews do not imply human verification of AI descriptions.

Validation: 38 focused approval/UI tests passed, including player bounds, deselection, missing source, final player/download and missing output. Whitespace check passed. No paid API calls, no new evaluation, and no holdout access. Existing Streamlit server stays running; refresh/rerun the page to load the new approval UI without restarting the process. Actual media was already rendered and probed in iteration 029.

## Demo recovery after empty live run — 2026-09-12T23:53:02.562026+05:30

User screenshot again showed 10 classified, zero subject-positive, zero clips. Raw 23:49–23:50 Gemini records confirm the generic recipe, candidate windows extending beyond 60 seconds (therefore not the verified 40-second demo source), and null classifications. The saved form settings did not match the validated demo. Prior readiness claims were too broad: a successful bounded graph run and UI component tests did not ensure the user's existing form used the same configuration. Do not interpret subject_present=false as proven absence of the team; responses also conflate no completed event with absence.

Added explicit recorded-run replay at ?demo=verified and the user's existing ?demo=recording URL. It bypasses provider preflight/inference and stale form inputs, reads the actual 029 render-verification record, shows source clip playback and Keep control, then the previously rendered reel and download on approval. Clearly labelled recorded Gemini result throughout; never presented as fresh inference, new rendering or a fix to full-game recognition. Live form remains available at ?demo=live with an obvious replay link. No external sharing.

Actual-media Streamlit smoke passed: source player, approval click, finished player, download, and deselection blocking. No model calls in replay. Existing app process remains running. This addresses recording reliability; live empty-result diagnosis and broader candidate coverage remain unresolved beyond the observed settings mismatch.

## Live HITL demo 030 — 2026-09-12T23:59:15.148085+05:30

User rejected replay as insufficient and authorized fixing the live demo. Added a dedicated live entry point at /?demo=live-demo (also default root). Fixed inputs use the real East Bay 40-second excerpt, demo recipe, 30-second reel budget and 8-candidate cap. No saved classifications are loaded: Analyze game excerpt invokes the production graph and fresh Gemini calls. Existing generic form remains at ?demo=live. This isolates the demo from stale generic recipe/source/override widget values. Current process must have Gemini native video enabled and tracing disabled; otherwise demo blocks visibly.

Executed actual Streamlit AppTest with live Gemini (not mocked): clicked Analyze game excerpt; verified gate1, a nonempty selection, source video player, and no rendered output before approval. Test then clicked Approve & Render under user authorization to complete verification; confirmed gate2, finished video player, download button and real MP4 via ffprobe. It did not click sharing. Fresh analysis and render took 31.99 seconds and cost an estimated $0.02388375. Ledger now $7.512800625; funded use $0.32050575/$2, no reset. Raw API records continue in demo-integration-029 because adapter logging currently uses that directory; 030 contains before/after state, verification and console log.

Fresh selected clips: [{"start": 9.0, "end": 20.5, "moment_type": "layup_or_dunk", "score": 0.66, "reason": "Light blue player steals/recovers the ball and scores a fastbreak layup", "subject_present": true}]

This is a live bounded demo, not a claim that arbitrary full-game inputs are reliable. Previously failed runs used generic recipe and first windows extending beyond 60 seconds, incompatible with the 40-second verified source. Early motion/audio candidates can omit decisive plays; model output also conflates no qualifying event with subject absence. Removed misleading diagnosis that automatically blamed jersey description/HD or promised audience override disables the filter. Revised test asserts uncertainty and sampling coverage. No holdout was accessed.

38 focused UI tests passed after updating the outdated diagnosis assertion. Actual live UI test is separate and paid; it is not included in routine pytest. Existing server remains running. Browser opened to the new live entry point. Human can start a fresh run, inspect and uncheck clips, approve rendering, and download final output. Results from repeated cloud calls can still vary; this end-to-end run establishes a working bounded path, not a guarantee for any footage.

## Multi-clip live workflow 032 completed — 2026-09-13T00:24:02.826138+05:30

User requested at least five clips, human video review and the full agent flow. 031 longer light-blue-only run selected three clips and failed that target. 032 used the same continuous 600-second East Bay development excerpt (original 750–1350 seconds), explicitly BOTH teams, native-video context of at least 12 seconds (capped at 20), selection lead-out 5 seconds/max clip 16, 90-second reel budget, unchanged 0.50 minimum score. This changes subject scope and context together; it is a functional demo iteration, not an isolated accuracy ablation. No holdout, transcript, YOLO, label injection, duplicated source footage or saved classifications were used.

Fresh graph run processed all 51 candidates (cap 80 did not truncate), selected six non-overlapping clips, paused at approval, then rendered under user authorization for validation. Output: output/multiclip-032/reel_basketball_both_teams_live_v1.mp4. Total 87 seconds, matching the sum of six clip durations. Five model labels are steals and one is rebound; these labels are suggestions requiring review, not audited statistics. Elapsed 469.46 seconds. 53 provider requests (51 video, judge, summary), estimated cost $0.53380800. Raw files listed in call-manifest.json; raw calls remain in adapter's demo-integration-029 directory. 031's last judge call crossed the 032 plan timestamp and was assigned back to 031 by its recipe prompt rather than silently charged to 032.

Restored the complete standard app at ?demo=full-flow. Existing ?demo=live-demo and root route there, resetting the obsolete short-demo state once. Form defaults: basketball_both_teams_live.yaml; local ten-minute excerpt; both-teams description; duration 0 (recipe90 seconds); audience recipe default; candidate cap80. Full live pipeline diagram shows actual node completions/timings, judge route, human approval, render and summary. Gate1 presents six small per-clip video previews with Keep controls; gate2 plays the finished reel with download. Previews are cached local encodes keyed by source path/mtime/exact boundaries, avoiding 550MB full-game loading per player. Preview failures explicitly fall back to the source range.

Validation: 411 tests passed, 4 skipped, 1 final-holdout test deselected; legacy SDK warning. Added context-bound tests. Actual 11.5-second preview encoded/probed and cache reused. Actual 032 state was loaded into both UI gates for offline view testing: six source-clip players at gate1, one reel player/download at gate2; no new inference or approval clicks in that UI view test. Fresh inference and graph rendering were separately executed by the live verifier. ffprobe confirms 87-second stitched output and non-overlapping selection. Full form/default route and pipeline diagram verified with offline preflight. No external share action.

Restarted Streamlit PID87840 to ensure the updated imported provider code is active, not merely app.py rerun with stale module imports. The running app uses Gemini native video and tracing disabled, with the new both-teams recipe/source defaults. No inference is scheduled. Ledger at notes checkpoint $8.443255875; funded usage $1.250961/$2, remaining $0.749039, including subsequent browser preflight if already recorded. Approximately one more similar ~$0.53 live run fits the remaining cap; repeated runs are not unlimited. Reported $3 demo reserve remains protected by this conservative shared cap.

This meets a bounded live multi-clip demonstration, not reliable full-game event recognition or all-category accuracy. Both the ten-minute source range and both-teams scope must stay visible. Model mistakes should be removed through HITL. Runtime logs/pid under ignored work/demo-app; media/previews ignored, code and notes currently uncommitted.

## Approval progress verification — 2026-09-13T00:36:41.680215+05:30

User reported Approve & Render appeared inert. Screenshot showed Streamlit busy. Inspection found a newly written output/reel_basketball_both_teams_live_v1.mp4 at00:35, 68,808,852bytes; ffprobe confirms89.5seconds. No ffmpeg remained active, server logs showed no exception. Thus local render completed; user Chrome session UI was not directly accessible via connected browser inventory (in-app tab was a different, idle session). Do not claim the user’s Chrome gate2 screen was visually verified.

Root UI feedback gap: full-flow branch updated diagram near top without a local spinner beside the clicked button. Wrapped both streaming and non-streaming approval continuation in an explicit “Approval received — stitching…” spinner. No server restart, no classification rerun, no paid calls. 38 focused approval/app tests pass. Copied actual new reel to user outputs as basketball-latest-approved-reel.mp4 for immediate access.

## Commit/push checkpoint — 2026-09-13T00:56:24.665196+05:30

User authorized committing and pushing all pending project changes. Full pre-push suite:411 passed,4 skipped,1 final-holdout test deselected; one legacy Gemini SDK warning. Demo integration029, live UI030, failed three-clip031, successful six-clip032 and subsequent user render/approval feedback fixes included. User's own later render output verified89.5seconds; no claim its Chrome gate2 was visually inspected. Provider spend ledger $8.982478125; funded use $1.790183 of$2, remaining $0.209817. This is insufficient for another similar ~$0.53 full inference run within the current cap. No paid calls made for commit validation; do not reset ledger.

Code, recipes, tests, raw response/usage records and timestamped notes are included. Credentials, local source/render media, preview cache, runtime lock and working scratch remain excluded. Live server remains running; pushing does not redeploy/restart it. Existing historical “uncommitted” entries describe their original checkpoint and are superseded by this commit preparation.
