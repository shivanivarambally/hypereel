# HypeReel — Teleprompter (spoken track only)

Read straight through. `//` marks a screen-change pause; do not read it aloud.
Approximately **467 words** (3.11 minutes at 150 words/minute), excluding pauses and video playback. Rehearse against the four-minute cap. Market wording is preserved as requested.

---

Walk into a Jam On It tournament in Vegas or Reno and you'll see fifty courts running at once. One weekend is around two thousand games — I verified that against a real event: 421 teams on 36 courts over three days. Behind every game is a parent or coach who wants a highlight reel, and each reel is three to four hours of scrubbing a 60-minute recording. That's roughly seven thousand hours of manual editing in a single weekend — and these tournaments run all season, across the country, a thousand-plus weekends a year.

HypeReel is a prototype for turning game recordings into reviewed highlight reels. Today I’ll show a live workflow on a ten-minute excerpt.

//

The recipe is a YAML policy: event definitions, selection budget, and exclusions. These settings are configurable; domain-specific perception code still exists. Other domains need their own validation.

The pipeline is a LangGraph state machine. Local audio and motion signals propose candidates. An optional scoreboard stage precedes vision classification; it is inactive in this demo. Gemini examines video segments, and deterministic code selects clips within the duration budget.

A text-model judge checks the proposed clips’ metadata and can request one bounded re-selection. It does not watch the finished video. Two human gates pause the graph: before final rendering and before delivery approval. Downloads, previews, and logs are created automatically. External uploading is not implemented.

//

Here I’m using the both-teams recipe on a continuous ten-minute East Bay excerpt. The source, subject, and budget are visible in the form.

Find highlights starts fresh Gemini analysis. The diagram tracks the real graph stages. I’ve compressed the waiting time in this recording.

The judge can accept or request a revision; our verified run accepted. Now I watch each proposed clip and uncheck anything I don’t want. Approve and Render stitches the kept clips, generates a summary, and pauses at the second gate. I can watch and download the reel here.

Our verified run produced six distinct clips totaling 87 seconds in seven minutes forty-nine seconds. These are model suggestions for human review, not audited event labels.

//

The evaluation uses external labels from two development games; a third game remains sealed for final testing. We keep the highlight-selection scorecard separate from the all-events comparison.

On eight development windows with fourteen reference events spanning twelve categories, Gemini direct video achieved 37 percent micro-F1, versus 12.5 percent for MiniCPM. Adding a generated transcript reduced F1 to 34.8 percent. This is a small-window comparison, not full-game accuracy, and the overall release criteria remain unmet.

The experiments point toward better temporal evidence and candidate coverage, but those improvements still need controlled validation.

//

What works today is the live review-and-render workflow. What remains is reliable event recognition across full games. The combination of visible human review and explicit evaluation makes that distinction clear.
