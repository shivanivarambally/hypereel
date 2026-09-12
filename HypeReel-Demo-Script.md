# HypeReel — Demo Script (target under four minutes)

**[SCREEN]** indicates what to show. Plain paragraphs in the five numbered beats are the spoken track, identical to HypeReel-Demo-Teleprompter.md. Market wording is preserved as requested.

## Timing plan

Approximately **467 spoken words**, about 3.11 minutes at 150 words/minute before pauses and playback. The windows below are rehearsal targets, not a guaranteed runtime.

| Beat | Target window | Screen |
| --- | --- | --- |
| 1 · Problem | 0:00–0:45 | Tournament footage → app |
| 2 · Architecture | 0:45–1:40 | Both-teams recipe → pipeline diagram |
| 3 · Workflow | 1:40–2:50 | Actual run → clip review → render → final player |
| 4 · Evaluation | 2:50–3:40 | Eight-window comparison |
| 5 · Close | 3:40–3:55 | Finished reel |

## Recording plan

Record one actual run and compress its waiting periods with an explicit “elapsed time compressed” caption. Do not start a new run then silently substitute another run’s ending. If a separate recorded run or saved artifact is shown, identify it. The verified ten-minute run took 7m49s; no 60-minute-game runtime is established by that result.

**Budget:** the current recorded ledger leaves about $0.205 under the existing cap, below the approximately $0.53 required for a comparable new full run. Use footage already recorded, or resolve the budget before another paid run. Do not reset the ledger. No model run is required to read this script.

**App:** http://127.0.0.1:8501/?demo=full-flow

**Form:** basketball_both_teams_live.yaml; source downloads/east-bay-demo-750-1350.mp4; both light-blue and black teams; max duration 0 (recipe budget 90 seconds); audience recipe default; candidate cap 80. The verified source generated 51 candidates, so that cap did not truncate it. Keep the actual source range visible: original 12:30–22:30, continuous footage.

---

## 1 · 0:00 — Problem
**[SCREEN: packed tournament footage, then the app. Do not portray its ten-minute excerpt as an entire 60-minute game.]**

Walk into a Jam On It tournament in Vegas or Reno and you'll see fifty courts running at once. One weekend is around two thousand games — I verified that against a real event: 421 teams on 36 courts over three days. Behind every game is a parent or coach who wants a highlight reel, and each reel is three to four hours of scrubbing a 60-minute recording. That's roughly seven thousand hours of manual editing in a single weekend — and these tournaments run all season, across the country, a thousand-plus weekends a year.

HypeReel is a prototype for turning game recordings into reviewed highlight reels. Today I’ll show a live workflow on a ten-minute excerpt.

## 2 · 0:45 — Architecture
**[SCREEN: recipes/basketball_both_teams_live.yaml, then the actual pipeline diagram. The scoreboard node is a pass-through for this recipe.]**

The recipe is a YAML policy: event definitions, selection budget, and exclusions. These settings are configurable; domain-specific perception code still exists. Other domains need their own validation.

The pipeline is a LangGraph state machine. Local audio and motion signals propose candidates. An optional scoreboard stage precedes vision classification; it is inactive in this demo. Gemini examines video segments, and deterministic code selects clips within the duration budget.

A text-model judge checks the proposed clips’ metadata and can request one bounded re-selection. It does not watch the finished video. Two human gates pause the graph: before final rendering and before delivery approval. Downloads, previews, and logs are created automatically. External uploading is not implemented.

## 3 · 1:40 — Workflow
**[SCREEN: source/recipe/brief → Find highlights → real stage updates. Compress waiting transparently. At Judge, describe the decision actually shown. Gate 1: play clips, demonstrate Keep controls → Approve & Render → wait for stitching → Gate 2: player/download. External upload is not demonstrated.]**

Here I’m using the both-teams recipe on a continuous ten-minute East Bay excerpt. The source, subject, and budget are visible in the form.

Find highlights starts fresh Gemini analysis. The diagram tracks the real graph stages. I’ve compressed the waiting time in this recording.

The judge can accept or request a revision; our verified run accepted. Now I watch each proposed clip and uncheck anything I don’t want. Approve and Render stitches the kept clips, generates a summary, and pauses at the second gate. I can watch and download the reel here.

Our verified run produced six distinct clips totaling 87 seconds in seven minutes forty-nine seconds. These are model suggestions for human review, not audited event labels.

## 4 · 2:50 — Evaluation
**[SCREEN: the eight-window comparison; keep the fourteen-reference scope and provisional event-time matcher visible.]**

The evaluation uses external labels from two development games; a third game remains sealed for final testing. We keep the highlight-selection scorecard separate from the all-events comparison.

On eight development windows with fourteen reference events spanning twelve categories, Gemini direct video achieved 37 percent micro-F1, versus 12.5 percent for MiniCPM. Adding a generated transcript reduced F1 to 34.8 percent. This is a small-window comparison, not full-game accuracy, and the overall release criteria remain unmet.

The experiments point toward better temporal evidence and candidate coverage, but those improvements still need controlled validation.

## 5 · 3:40 — Close
**[SCREEN: the rendered reel.]**

What works today is the live review-and-render workflow. What remains is reliable event recognition across full games. The combination of visible human review and explicit evaluation makes that distinction clear.

---

### Timing adjustments

If rehearsal runs long, shorten the architecture explanation or video playback. Leave enough time for viewers to see a clip being reviewed. Do not remove scope/recording disclosures.

### The market numbers (Beat 1) — where they come from
- **2,000 games / weekend** and **421 teams on 36 courts** — *verified* against the 2026 West Coast National Championships schedule. Say these with confidence.
- **3–4 hours per reel** — from the project's own problem statement (manual scrubbing + cutting).
- **~7,000 hours / weekend** and **1,000+ weekends / year** — defensible *estimates* that frame the scale of the manual problem. If pressed, call them estimates, not measured figures.


### Do-not-say list

- Market numbers describe the manual status quo, not measured savings achieved by HypeReel.
- Do not claim full-game accuracy, all release gates passing, or a completed holdout evaluation.
- Do not narrate a judge revision unless it occurs in the displayed run.
- Do not imply scoreboard grounding, external upload or memory-based personalization is active in this demo.
- Distinguish the six-clip/87-second verified run from the later 89.5-second user output.

## Q&A backup — not spoken

- **Architecture:** fixed graph order; model-based classification and judge decisions; at most one judge-driven re-selection. A judge revision is conditional. The production judge uses metadata, while the separate evaluation judge is advisory and does not alter benchmark scores.
- **Recipes:** configure rubrics, signals, exclusions and selection. Basketball-specific prompts and scoreboard logic remain in code. Walkthrough recipe support is not proof of reliable zero-code transfer to arbitrary domains.
- **Human review:** the user can preview and deselect clips before final rendering. Preview files, downloads, logs and checkpoints are internal writes that happen earlier. Gate 2 represents delivery approval; no external upload connector is implemented.
- **Memory and RAG:** local profile/feedback storage primitives exist; automatic personalization is not wired into this Streamlit flow. Recipes and a user brief are not a vector-retrieval RAG system.
- **Evaluation history:** selection tuning and perception pilots 001–028 are followed by demo integration 029–032. Iteration IDs include diagnostic, failed and recovery runs; do not treat their count as independent benchmark replications. Logging varies by harness; standalone/UI runs do not all use the evaluation CLI or history.jsonl.
- **Results:** direct Gemini TP5/FP8/FN9, micro-F1 .37037; historical MiniCPM TP3/FP31/FN11, .125; generated-transcript Gemini TP4/FP5/FN10, .34783. Same eight-window/14-reference comparison, provisional ±5-second event-time matcher; do not pool with the older IoU highlight-selection metrics. The 24.54-percentage-point F1 increase is numerical evidence on this small set, not a general accuracy guarantee.
- **Earlier work:** local Qwen, detector crops, transcripts, denser frames, ball-state derivation and YOLO/ByteTrack were tested. Results varied by subset; no reliable general event detector was established. Generic ball tracking was sparse (8/1,023 frames in pilot020). These findings do not prove prompting can never help or every earlier match was fabricated.
- **Recent demo:** 031 selected three clips using the light-blue-only scope. 032 changed scope to both teams and minimum native-video context to 12 seconds, selecting six non-overlapping clips and rendering 87 seconds. It took 469.46 seconds and cost an estimated $0.533808. This changes multiple factors and is not an isolated accuracy ablation. The user's later 89.5-second output is a different run.
- **Metrics:** label-aware matching, precision/recall/F1, temporal quality, schema/structural validity, latency and estimated cost. Metrics and matching rules differ between harnesses. Undefined ratios are N/A where appropriate. The lexical entailment screen is a limited diagnostic, not proof of visual grounding.
- **Current checkpoint:** code df3fc18; 411 tests passed, 4 skipped, 1 holdout test deselected at pre-push. No holdout evaluation. Some individual criteria pass; the overall release criteria do not.
- **Budget snapshot (2026-09-13):** estimated cumulative ledger $8.987366625; $1.79507175 of the incremental $2 cap used, approximately $0.20493 left. Another similar $0.53 full run does not fit the remaining cap. Do not reset the ledger or initiate a new paid run merely for recording without resolving this limit. Existing recorded footage and reels remain usable.
