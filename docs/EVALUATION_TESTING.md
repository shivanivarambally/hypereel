## Current funded checkpoint

All12category development comparison and transcript test complete. See ../evals/iterations/gemini-funded-summary/results.md. New evaluation cap$2fromfixedbaseline$7.192294875;demo reserve$3. Currentcap policy supersedes historical$8andquota-blockednotes below.400tests pass,4skipped,1holdoutexcluded.

# Evaluation testing and continuation

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

## Current live evidence

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
