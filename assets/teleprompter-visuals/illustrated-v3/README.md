# Illustrated teleprompter boards — v3

Created 2026-09-12T20:14:04.226Z using the built-in image-generation tool.

Five 16:9 PNG boards match the user's supplied hand-drawn visual reference. They replace transcript-heavy imagery with illustrated scenes and short labels. Original versions remain untouched.

Open index.html for the gallery.

1. [Tournament and editing](01-tournament-and-editing.png)
2. [Agent workflow](02-agent-workflow.png)
3. [Live review and render](03-live-review-and-render.png)
4. [Evaluation results](04-evaluation-results.png)
5. [Working today and next](05-working-today-and-next.png)

Content: HypeReel-Demo-Teleprompter.md; architecture cross-checked against src/hypereel/graph/build.py. User screenshot is a style reference only; its older product claims were not adopted.

QA: reviewed all generated boards. Corrected missing Select → Judge forward arrow, removed invented recipe duration, corrected evaluation heading from held-out test to development-window results, corrected closing player duration to 1:27, removed misleading sequence numbers and event-confidence checkmarks. Preserved 12.5%, 37.0%, 34.8% micro-F1, 8 windows, 14 events, 12 categories; sealed final test; six clips/87 seconds/7m49s demo totals.

The pictures are schematic illustrations, not actual application screenshots or evidence that specific depicted event categories were recognized in the demo. Individual thumbnail timestamps are illustrative. The market estimate is reproduced from the user's script and explicitly labelled illustrative; it was not independently re-researched in this visual task.

Exact prompts and targeted corrections: prompts.json. No evaluation run, inference API calls against the project's Google account, application changes, or holdout access.
