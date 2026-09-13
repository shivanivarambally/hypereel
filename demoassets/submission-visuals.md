# Submission illustrations

Six main sections of HypeReel-Breakout-Submission.html have responsive, accessible whiteboard illustrations. Five user-supplied boards are reused unchanged; the team board is newly generated. Captions distinguish schematic UI and product vision from measured results. Existing submission prose and market claims were preserved byte-for-byte.

## Sources
- Section 1: `submission-team.png` — Shivani builds and evaluates HypeReel, with parents and coaches as intended users.
- Section 2: `Codex Image Sep 13, 2026, 01_48_55 AM.png` — From tournament footage and hours of manual editing to human-reviewed basketball highlights.
- Section 3: `Codex Image Sep 13, 2026, 01_49_28 AM.png` — Recipe-led workflow from ingestion and Gemini classification through selection, human review and rendering.
- Section 4: `Codex Image Sep 13, 2026, 01_49_13 AM.png` — Illustrated live flow: configure the brief, review proposed clips, then render a reel.
- Section 5: `Codex Image Sep 13, 2026, 01_49_22 AM.png` — Development evaluation compares MiniCPM, Gemini and Gemini with generated transcript while preserving the holdout.
- Section 6: `Codex Image Sep 13, 2026, 01_49_03 AM.png` — Current review-and-render workflow and future improvements to temporal evidence and event coverage.

## Team illustration generation

Mode: built-in image generation with the supplied system-design board as a style reference, followed by a targeted edit. No Google API inference.

Prompt: Create a rich wide 16:9 Excalidraw-style illustrated whiteboard for the Who is on this team section. White paper, charcoal wobbly outlines, readable handwritten type, lavender header cards, orange highlights, soft green accents and warm basketball sketches. Title: HypeReel — The people behind the project. Left: illustrated female builder at laptop, YAML notebook, basketball, testing checklist and film strip, labeled Shivani and Builder / point person. Right: parent watching footage and coach reviewing a clip, labeled People we design for, Parents, Coaches; user roles, not teammates. Bottom: Build → Evaluate → Human review. Do not invent surnames, emails, cities, teammates, real likeness, numerical results or upload functionality.

Correction prompt: Replace the checklist text Fine-tune with Iterate. Preserve all other artwork, wording, composition, colors and dimensions. This project did not fine-tune a model.

The final generated PNG is copied into this repository as submission-team.png. A standalone shareable HTML version embeds all six PNGs. No external image service is required to open it.

## Actual product screenshot

Section 4 also includes submission-product.png, copied unchanged from the user screenshot dated 2026-09-13 09:51:35. It shows the actual configuration and pipeline after rendering, awaiting the second approval gate. This is distinct from the illustrated workflow board.

## Team revision

Replaced submission-team.png using built-in image editing. Final edit prompt: Replace the left heading and builder/point-person subtitle with Our team and equal-weight name labels Shivani and Satya Parimi. Preserve all other artwork and wording. Updated submission table, caption and alt text; removed solo and point-person designations. Earlier generation prompts above are historical provenance.

## Team illustration withdrawn

The user requested removal of the team visual. The submission now uses only the team table for section 1. submission-team.png is retained as unused history; five other illustrations and the product screenshot remain embedded.
