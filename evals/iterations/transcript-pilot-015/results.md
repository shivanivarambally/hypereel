# Transcript pilot015 — results and observations

Transcript pilot015 completed at 2026-09-12T19:47:12.041385+05:30; final audit recorded 2026-09-12T19:50:21.866669+05:30.

User identifies HoopIQ as the specialist source of the supplied golden labels. No replacement specialist or new user annotation was required. Tested fresh direct detection against observation-only visual narration followed by text-only event extraction, using the same Nebius MiniCPM-V-4_5 for all stages. Three frozen development windows [1,2,6],10 references across9 supported types, all12 event definitions available. Identical6frame JPEG sequences per visual arm,768pixel wide,2.4second gaps across12seconds including2seconds context either side. This isolates representation change on sparse evidence; it is not continuous-video transcription or speech recognition. No references entered model prompts. Third dataset untouched.

Nine of nine provider calls returned completed output in 20.26s; no provider crash, timeout or retry. All3 narrations parsed, all3 direct results parsed,2of3 extraction outputs passed the original strict core-time validation. Window1 emitted an event at233s outside223–231, so that whole transcript result was excluded from primary paired metrics. All raw outputs, input hashes, prompts, observation IDs, per-call timestamps, latencies, usage and memory/pressure checkpoints are preserved. Per-call raw text and parsed window outputs were appended to IMPLEMENTATION_NOTES during execution.

Primary matched coverage: windows2and6,9 references across8 supported types. Direct TP2/FP6/FN7,precision25%,recall22.22%,microF1 23.53%,macroF1 10%. Transcript TP3/FP3/FN6,precision50%,recall33.33%,microF1 40%,macroF1 25%. Unmeasured categories must not be described as passing. Available-only full direct metrics use3windows and cannot be directly compared with2window transcript metrics.

Audit identified asymmetric boundary handling: direct accepted observed context then filtered; extraction required core bounds. Retained original report unchanged. A separately labeled post-hoc offline sensitivity applies direct's context/filter policy to retained extraction outputs acrossall3windows: direct TP2/FP8/FN8,P20%,R20%,F1 20%;transcript TP3/FP4/FN7,P42.86%,R30%,F1 35.29%. No fresh inference or reference changes. Future paired runner must apply identical boundary policy from the outset.

The numerical lift is not established semantic improvement. All6 accepted transcript events cite observations that do not establish their claimed miss or possession outcome. All3 matches are in campus window6. All6 accepted events haveconfidence1.0. All18 narrator rows say visibility=clear despite several descriptions explicitly stating uncertainty. Contact-sheet inspection found clear visual errors: free-throw setup mislabeled as a shot near the three-point line; midcourt ball handling narrated as a shot towards the basket. Full qualitative audit is in observation-audit.json. This audit is agent inspection, not independent human reannotation; original HoopIQ labels/times remain unchanged.

Implementation: added evaluation/transcript.py for timestamp-anchored observations, text-only extraction and valid observation-ID checks; scripts/run_transcript_pilot.py for bounded paired inference and live notes; scripts/audit_transcript_pilot.py for reproducible offline sensitivity. Citation validation establishes ID existence, not factual entailment. No semantic filter was retroactively used to boost scores. Production application architecture unchanged.

Tests:355 passed,4 skipped,1 final_holdout test deselected; no holdout evaluation. Three new tests cover time anchoring/order, paired events, invented citations and empty-transcript evidence. Spend estimateincrement$0.18957,ledger cumulative$4.33608 against$5 ceiling; historical conservative estimates,not invoice prices. No inference remains running.

Decision: retain the transcript and evidence-link format as a diagnostic tool; do not adopt this MiniCPM narration/extraction combination as a reliable detector. Both visual narration and text-to-event reasoning failed. Next refinement should first enforce common boundary handling and evaluate extraction entailment on these frozen transcripts, then test visual narration with genuinely richer temporal evidence or a better visual model under a separately frozen comparison. Treat observation accuracy and event matching separately; do not equate a valid citation or high model confidence with correctness. No new architecture switch or paid run was started after this audit.

## Per-type primary paired metrics

TP / FP / FN (support). Zero support means recall unmeasured.

| Event | Direct | Transcript |
|---|---:|---:|
| assist | 0 / 0 / 1 (1) | 0 / 0 / 1 (1) |
| block | 0 / 0 / 0 (0) | 0 / 0 / 0 (0) |
| defensive rebound | 1 / 3 / 0 (1) | 1 / 1 / 0 (1) |
| free throw made | 0 / 0 / 0 (0) | 0 / 0 / 0 (0) |
| free throw miss | 0 / 0 / 0 (0) | 0 / 0 / 0 (0) |
| offensive rebound | 0 / 0 / 1 (1) | 1 / 1 / 0 (1) |
| steal | 0 / 0 / 1 (1) | 0 / 0 / 1 (1) |
| three point made | 0 / 0 / 0 (0) | 0 / 0 / 0 (0) |
| three point miss | 0 / 0 / 1 (1) | 0 / 0 / 1 (1) |
| turnover | 0 / 0 / 2 (2) | 0 / 0 / 2 (2) |
| two point made | 1 / 3 / 0 (1) | 0 / 0 / 1 (1) |
| two point miss | 0 / 0 / 1 (1) | 1 / 1 / 0 (1) |

## Qualitative audit

All18 transcript rows use visibility=clear, including text saying possibly or uncertain. Metadata does not reliably represent uncertainty.

Window1 narrative describes black-team shooting near the three-point line; supplied images show a blue-uniform player at the free-throw line. Free-throw setup recognition is wrong. Sparse frames do not independently settle every shot outcome.

Window2 at758.8s shows a black-uniform ball handler near midcourt with blue defenders; narration calls this a shot towards the basket. At763.6s black players remain visible although narration says the black player is no longer in frame. This establishes visual-description errors without altering reference times.

Window6 narration repeats ball-in-air descriptions across most frames instead of distinguishing the changing action. Initial claim of white control is questionable: first image shows ball near a yellow-uniform player. Exact full action sequence is not reannotated from these sparse samples.

All6 accepted transcript-branch events have citations that do not establish their claimed outcome/control: ball-in-air is used for misses and rebounds; one uncertain-outcome row becomes an offensive rebound. All6 events have confidence1.0.

All3 transcript label/time matches occur in window6. None of their cited observations establishes the event. Better reference matching here does not establish better grounded recognition.

Window1 extraction includes233s outside core223–231; original parser rejects whole extraction. Direct parser accepts observed-context times then filters to core. This asymmetric boundary handling is a pilot limitation, not a model recognition failure alone.

## Timestamped visual transcripts and extraction outputs

### Window 1: east-bay-elite-vs-spartans 223–231 seconds

- **221.0s (o1, clear):** A player in black holds the ball near the three-point line, preparing to shoot. The ball is not visible yet.
- **223.4s (o2, clear):** The player in black releases the ball towards the basket. The ball is in mid-air, heading towards the rim.
- **225.8s (o3, clear):** The ball is still in the air, approaching the basket. The players in blue are positioned to defend.
- **228.2s (o4, clear):** The ball makes contact with the rim, bouncing off. Players in blue and black are reacting to the shot.
- **230.6s (o5, clear):** The ball is in the air again, possibly after a rebound. Players in blue and black are moving towards the ball.
- **233.0s (o6, clear):** A player in blue is seen with the ball, possibly after a rebound. The ball is in the player's hands.

Extraction status: invalid. Unknown label or event outside observed interval

```json
{"events": [{"label": "two_point_miss", "time_seconds": 228.2, "confidence": 1, "evidence": "The ball makes contact with the rim, bouncing off.", "observation_ids": ["o4"]}, {"label": "offensive_rebound", "time_seconds": 233.0, "confidence": 1, "evidence": "A player in blue is seen with the ball, possibly after a rebound.", "observation_ids": ["o6"]}]}
```

### Window 2: east-bay-elite-vs-spartans 756–764 seconds

- **754.0s (o1, clear):** Players are positioned on the court. A player in black is holding the ball, preparing to make a play. The ball is in the player's hand.
- **756.4s (o2, clear):** The player in black is dribbling the ball towards the basket. The ball is in the player's hand, and the player is moving forward.
- **758.8s (o3, clear):** The player in black is attempting a shot. The ball is in the air, heading towards the basket. The player in blue is near the basket, possibly defending.
- **761.2s (o4, clear):** The ball is in the air, close to the basket. The player in black is still in the frame, and the player in blue is near the basket. The outcome of the shot is uncertain.
- **763.6s (o5, clear):** The ball is in the air, and the players are moving around the court. The player in black is no longer in the frame, and the player in blue is still near the basket. The ball's trajectory is uncertain.
- **766.0s (o6, clear):** The ball is in the air, and the players are moving around the court. The player in black is no longer in the frame, and the player in blue is still near the basket. The ball's trajectory is uncertain.

Extraction status: completed.

```json
{"events": [{"label": "two_point_miss", "time_seconds": 758.8, "confidence": 1, "evidence": "The player in black is attempting a shot. The ball is in the air, heading towards the basket. The player in blue is near the basket, possibly defending.", "observation_ids": ["o3"]}, {"label": "offensive_rebound", "time_seconds": 761.2, "confidence": 1, "evidence": "The ball is in the air, close to the basket. The player in black is still in the frame, and the player in blue is near the basket. The outcome of the shot is uncertain.", "observation_ids": ["o4"]}, {"label": "defensive_rebound", "time_seconds": 763.6, "confidence": 1, "evidence": "The ball is in the air, and the players are moving around the court. The player in black is no longer in the frame, and the player in blue is still near the basket. The ball's trajectory is uncertain.", "observation_ids": ["o5", "o6"]}]}
```

### Window 6: unlimited-vs-campus 1316–1324 seconds

- **1314.0s (o1, clear):** A player in a white jersey is holding the ball near the three-point line, facing the basket. The ball is in the player's hands.
- **1316.4s (o2, clear):** The ball is in the air, moving towards the basket. Players in yellow jerseys are positioned under the basket, ready to rebound.
- **1318.8s (o3, clear):** The ball is in the air, approaching the basket. Players in yellow jerseys are under the basket, and a player in a white jersey is also near the basket.
- **1321.2s (o4, clear):** The ball is in the air, moving towards the basket. Players in yellow jerseys are under the basket, and a player in a white jersey is also near the basket.
- **1323.6s (o5, clear):** The ball is in the air, moving towards the basket. Players in yellow jerseys are under the basket, and a player in a white jersey is also near the basket.
- **1326.0s (o6, clear):** The ball is in the air, moving towards the basket. Players in yellow jerseys are under the basket, and a player in a white jersey is also near the basket.

Extraction status: completed.

```json
{"events": [{"label": "two_point_miss", "time_seconds": 1316.4, "confidence": 1, "evidence": "The ball is in the air, moving towards the basket. Players in yellow jerseys are positioned under the basket, ready to rebound.", "observation_ids": ["o2"]}, {"label": "offensive_rebound", "time_seconds": 1323.6, "confidence": 1, "evidence": "The ball is in the air, moving towards the basket. Players in yellow jerseys are under the basket, and a player in a white jersey is also near the basket.", "observation_ids": ["o5"]}, {"label": "defensive_rebound", "time_seconds": 1323.6, "confidence": 1, "evidence": "The ball is in the air, moving towards the basket. Players in yellow jerseys are under the basket, and a player in a white jersey is also near the basket.", "observation_ids": ["o5"]}]}
```

## Execution catalogue

| Window | Stage | Started | Ended | Seconds |
|---|---|---|---|---:|
| 1 | direct | 2026-09-12T19:46:51.786792+05:30 | 2026-09-12T19:46:54.884212+05:30 | 3.10 |
| 1 | narration | 2026-09-12T19:46:54.902829+05:30 | 2026-09-12T19:46:57.214411+05:30 | 2.31 |
| 1 | extraction | 2026-09-12T19:46:57.233235+05:30 | 2026-09-12T19:46:58.181415+05:30 | 0.95 |
| 2 | direct | 2026-09-12T19:46:58.203945+05:30 | 2026-09-12T19:47:00.709799+05:30 | 2.50 |
| 2 | narration | 2026-09-12T19:47:00.726195+05:30 | 2026-09-12T19:47:03.314982+05:30 | 2.59 |
| 2 | extraction | 2026-09-12T19:47:03.332000+05:30 | 2026-09-12T19:47:05.136944+05:30 | 1.80 |
| 6 | direct | 2026-09-12T19:47:05.155487+05:30 | 2026-09-12T19:47:07.253877+05:30 | 2.10 |
| 6 | narration | 2026-09-12T19:47:07.270247+05:30 | 2026-09-12T19:47:09.904059+05:30 | 2.63 |
| 6 | extraction | 2026-09-12T19:47:09.919480+05:30 | 2026-09-12T19:47:12.021344+05:30 | 2.10 |
