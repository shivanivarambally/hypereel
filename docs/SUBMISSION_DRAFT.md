# HypeReel — breakout submission and demo draft

> **Archived draft — superseded 13 September 2026.** Use the [current single-file submission](../HypeReel-Breakout-Submission-under-10MB.html) for team details, personal icebreakers, both demo recordings and submission date. The date warnings, missing-details checklist and proposed answers below are historical drafting notes, not current submission guidance.

Prepared September 12, 2026. Draft for owner review; nothing submitted or uploaded.

## Source requirements and items to confirm

[Assignment handout](https://docs.google.com/document/u/0/d/1rcRRpxQLgxcqvpqomzPnFACA-OX1eo8U2UzpKjEFmaY/mobilebasic)
and its [linked submission form](https://docs.google.com/forms/d/e/1FAIpQLSef8V_S-a8ymHtTlBWu7diapKcQ5ngKGSOm0Vp7lBzsDMW59g/viewform).

The handout asks for team names/emails and a point person, followed by three topics:
use case; knowledge/tools and where RAG fits; autonomy/workflow and evaluation.
It requests an architecture pitch, with a prototype optional. Fine-tuning and AI
security are not required. Team coordination over three weeks is also requested.

The linked form requires submission email, team number, member names, an uploaded
breakout document, GitHub URL and a Drive demo-video URL. It says one submission
per team and one person can submit the recording.

**Confirm destination and dates before submission:** the handout title refers to
August 2026 and its deadline says September 12, 11:59 pm PT; its footer mentions
July 12–13 demo days, while the linked form is titled May 2026 Cohort. These are
inconsistent. Do not infer a required recording length: none was visible here.

Missing owner details: team number, confirmed member names/emails, point person,
meeting plan, and final approved video link. Do not infer the team roster from git
contributors or an authenticated browser account. Existing README demo link is a
candidate only; its contents and current submission suitability have not been verified.

## Q1 — Use case (draft answer)

HypeReel helps basketball players, parents and coaches find relevant plays in long
game recordings and turn them into a reviewable highlight reel. Manually finding
each play and choosing useful clip boundaries is repetitive and time-consuming.
The user supplies a recording, a description of the team or player, and the desired
reel length. The system proposes moments, classifies the action, selects clips and
asks the user to approve them before rendering and delivery.

Our initial focus is basketball footage with varying lighting and camera quality.
The intended benefit is reduced manual review effort, not autonomous publication
or a claim that every play is already detected accurately. Time savings and user
approval rates remain outcomes to measure, not established project results.

## Q2 — Knowledge, RAG and tools (draft answer)

The system needs to know the requested subject, event definitions, inclusion and
exclusion rules, duration constraints and what constitutes a complete action.
The current prototype provides these through structured YAML recipes and the
user's brief. It uses video evidence to judge events rather than treating a
scoreboard update as sufficient proof of a basket.

Its tools perform distinct jobs: yt-dlp resolves video sources; OpenCV and local
signals propose windows and sample frames; a vision model classifies evidence;
deterministic selection code manages timing and duration; a text-model critic
reviews clip metadata; and ffmpeg/media tooling supports clip rendering. A
Streamlit interface exposes the workflow, with LangGraph coordinating state and
human approval points. Provider adapters support hosted models and local Ollama
with Qwen3-VL Instruct. Ordered images are not the same as native full-video input.

RAG is a potential knowledge layer, not an implemented claim in this prototype.
It could retrieve approved basketball event definitions, team rosters and
user-approved editing preferences when those collections grow. Retrieved material
would supply definitions and identity context, not substitute for visual proof
that a play happened. For a small fixed rubric, explicit recipes are simpler and
more auditable than adding a vector database. JSON preference storage and graph
checkpoints should not be described as a full RAG pipeline. Golden event labels
belong only in evaluation and must never be retrieved into inference prompts.

Recent experimental scripts also test visual transcripts and YOLO/ByteTrack
observations. These are diagnostic research branches, not a production-integrated
tracking or possession-understanding feature.

## Q3 — Autonomy, workflow and evaluation (draft answer)

We use bounded autonomy inside a structured workflow. Models interpret visual
evidence and provide advisory criticism; code controls source handling, schemas,
clip selection, duration constraints and the bounded revision loop. The user
approves the clip list before rendering and approves delivery afterward. This
keeps creative judgments separate from actions with external effects. A fallback
that lets the graph reach human review is not proof that the model approved a
good reel.

Evaluation goes beyond human approval. We maintain externally labeled reference
events from two development games, plus a separate third game reserved for final
validation. We compare predictions to references with one-to-one, label-aware
matching and explicit time rules. Metrics include precision, recall, TP/FP/FN,
per-event and aggregate F1, temporal quality, false positives on negative footage,
and the proposal-to-classification-to-selection funnel. Operational checks cover
schema failures, invalid boundaries, duplicate/overlapping clips, latency, model
calls, token usage and cumulative estimated cost. Human review separately assesses
visual correctness, action completeness and whether the final reel is watchable.

Every iteration preserves its configuration, dataset version, predictions,
metrics and change note. Development comparisons hold inputs and matching rules
fixed, record unsuccessful attempts and do not tune against the third game.
Legacy highlight tests use IoU-aware action matching; newer all-event pilots use
their own declared event-time matcher. We do not pool incompatible scorecards.
Provisional action boundaries and imperfect external labels require audit.

The original highlight gates require candidate recall at IoU .30 of at least .80;
selected precision, recall and F1 each at least .70; temporal recall at .30 of at
least .70; valid schemas and no invalid or overlapping selected intervals.
These are targets, not achieved results. All-event experimental results require
separate interpretation against their declared ontology and matcher.

## Evidence-backed current status

Use the latest repository evidence, not just the older local smoke-test result:

- **Working:** local text/image inference and the orchestrated prototype workflow;
  reference datasets, cumulative evaluations and controlled comparisons.
- **Local historical baseline:** Qwen3-VL Instruct completed four windows in
  321 seconds but missed both reference steals. This proves execution, not quality.
- **Latest recorded pilot020:** three paired development windows, ten reference
  events across nine supported types. Adding YOLO/ByteTrack observations to shared
  visual transcripts plus MiniCPM changed TP/FP/FN from 3/6/7 to 3/4/7. Precision
  rose from 33.33% to 42.86%, recall stayed 30%, and micro F1 rose from 31.58% to
  35.29%. This pilot used hosted MiniCPM, not local Qwen.
- **Important limitation:** observed ball tracks occurred in only 8 of 1,023
  frames. All true-positive matches were in the Campus window where no ball track
  was available. The numerical lift therefore does not establish successful
  track-based recognition or visually grounded event correctness.
- **Latest recorded verification:** 388 tests passed, four skipped, one final
  holdout test deselected. This was recorded by the continuation work, not rerun
  while drafting this submission.
- **Latest ledger:** $6.64630 estimated cumulative provider spend. Current notes
  record an $8 ceiling superseding the earlier $5 limit. These are accounting
  estimates, not provider invoice totals. No calls were made for this draft.
- **Not established:** production-ready basketball accuracy, sustained possession
  tracking, full-game quality gates or final holdout success.

Evidence: [current status](../evals/STATUS.md),
[pilot020 results](../evals/iterations/track-transcript-020/results.md),
[implementation history](../evals/IMPLEMENTATION_NOTES.md), and
[local baseline](../evals/iterations/ollama-development-001.report.json).

## Suggested demo narrative (approximately four minutes; our proposal)

1. **Problem and user — 30 seconds:** explain the repetitive work and show the
   source/subject/duration inputs. Avoid unmeasured time-saving claims.
2. **Architecture — 45 seconds:** show proposal, visual classification, selection,
   bounded critique and human gates. Identify model decisions versus fixed code.
3. **Workflow — 60 seconds:** show a verified small run or clearly labeled recorded
   result. Show the selected clips and review gate if a suitable real result is
   available. Do not portray fixtures, mocks or manually chosen clips as detections.
   Do not launch a long live inference run just for recording.
4. **Evaluation — 75 seconds:** show external reference events, one missed or
   unsupported prediction, and a paired before/after scorecard. Explain why a
   successful request or human approval is insufficient.
5. **Learning and next step — 30 seconds:** explain the perception bottleneck,
   why more prompt tuning alone is insufficient, and the sealed holdout plan.

Strong closing: “We built a testable agent workflow and used objective evaluation
to expose its limits. The prototype runs, but reliable basketball recognition
remains unresolved. Our next milestone is better visual evidence, followed by
development validation and an untouched final test.”

## Submission checklist

- Confirm the cohort/form and deadline with the organizer.
- Confirm team details and review the answers above.
- Choose and verify the exact demo footage; do not claim unrecorded rendering.
- Refresh status immediately before recording if another agent continues experiments.
- Prepare the required uploaded document after owner review of this draft.
- Commit/push the intended implementation and evidence so the GitHub link is reproducible;
  exclude secrets, local video/model weights and unrelated work.
- Record the demo, obtain its Drive link, and check reviewer access.
- Submit once through the confirmed form only after owner authorization.
