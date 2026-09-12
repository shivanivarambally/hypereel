# Local vision inference with Ollama

Ollama is the local model runtime; Qwen3-VL is the vision model. This setup
uses `qwen3-vl:4b-instruct`, not a text-only Llama model. No provider API key or paid
inference endpoint is required. Downloading the model still requires an
internet connection, disk space, and acceptance of its applicable license.

The initial target is an Apple M1 Mac with 16 GB unified memory. The 4B
model's listed download is about 3.3 GB; that is **not** its runtime memory
requirement. Close memory-heavy applications. Start with one request at a
time, three frames, 448-pixel maximum image edge, a 4,096-token context, and
256 output tokens. Local execution can be slow, and quality must be measured.

## Install and start

```sh
brew install ollama
OLLAMA_NO_CLOUD=1 OLLAMA_HOST=127.0.0.1:11434 ollama serve
```

Leave the server running and use another terminal:

```sh
ollama pull qwen3-vl:4b-instruct
ollama list
curl http://127.0.0.1:11434/api/tags
```

Use Ollama 0.12.7 or newer for this model. If `ollama serve` reports an
address conflict, inspect the existing server before starting another one.
Keep the listener on loopback; do not expose it to the network. Download
only the initial model until feasibility is established.

Use the explicit **`4b-instruct`** tag. During initial local checks, the
stock `qwen3-vl:4b` alias used a thinking variant and exhausted the bounded
32- and 256-token generations despite `think:false`; these were failures,
not successful classifications. The failed probe reports remain preserved.
Switching to the instruct variant avoids relying on that alias's thinking
behavior; it still requires its own smoke and basketball quality tests.

The repository launcher explicitly selects local vision and local text
inference, disables tracing, and checks that the server is reachable:

```sh
bash scripts/run_local.sh app
```

This opens a separate app at `http://127.0.0.1:8502`, leaving an existing
app on port 8501 unchanged. The launcher defaults to five frames with six
seconds of before/after context, an 8,192-token context, no verifier, and an eight-request setting.
The total request-count limit is enforced inside evaluation's budget scope;
**do not treat the interactive app as having a total-run request cap**.
Per-request context, image-size, output-token, and timeout limits still apply.

## Configure HypeReel

From the repository root, using the project's existing Python environment:

```sh
export HYPEREEL_VISION_PROVIDER=ollama
export HYPEREEL_LLM_PROVIDER=ollama
export OLLAMA_BASE_URL=http://127.0.0.1:11434
export OLLAMA_MODEL=qwen3-vl:4b-instruct
export HYPEREEL_TRACING_ENABLED=false
export LANGSMITH_TRACING=false
export LANGCHAIN_TRACING_V2=false
```

Both providers must be set explicitly: a previously configured cloud LLM
must not remain enabled alongside local vision. The Ollama adapter rejects
non-loopback endpoints and cloud-model tags, disables HTTP proxies and
redirects, and does not silently substitute mock outputs on initialization
failure. An unavailable server/model is a failure, not a successful test.

This adapter sends **ordered images** to Ollama's native `/api/chat` API.
The pipeline extracts frames from short video windows. It does not send
MP4 files or establish native full-video understanding. Sampling can miss
fast actions; multi-frame inference alone does not solve temporal detection.

## Bounded development evaluation

First pass the offline contracts:

```sh
.venv/bin/python -m pytest tests/test_ollama.py tests/test_provider_budget.py
```

After a successful image smoke test, use the existing small development
slice, with four candidate windows, before considering full-video inference.
The measured local run uses `evals/experiments/game-1-ollama-local.pipeline.jsonl`
and expects the cached source at `downloads/KBETdDRM70Q.mp4`. Download it once:

```sh
.venv/bin/python -c 'from hypereel.ingest.source_resolver import resolve_source; from hypereel.config import Settings; print(resolve_source("https://www.youtube.com/watch?v=KBETdDRM70Q", Settings(download_dir="downloads"), max_height=480, max_retries=0))'
```

Then run:

The synthetic probe makes at most two local requests (text plus a red
image), preserves an existing output file, and returns a failing exit code
unless both responses match. Run it first using a new report path:

```sh
.venv/bin/python scripts/probe_ollama.py \
  --output evals/results/iterations/ollama-smoke-001.json
```

Then run the bounded basketball slice:

```sh
OLLAMA_NUM_CTX=8192 \
HYPEREEL_FRAMES_PER_CANDIDATE=5 \
HYPEREEL_CLASSIFICATION_CONTEXT_SECONDS=6 \
HYPEREEL_VERIFY_WITH_CORE_FRAMES=false \
HYPEREEL_MAX_PROVIDER_CALLS=5 \
HYPEREEL_MAX_PROVIDER_SPEND_USD=5 \
bash scripts/run_local.sh eval \
  --dataset evals/experiments/game-1-ollama-local.pipeline.jsonl \
  --output evals/results/iterations/ollama-development-002 \
  --change-note "Local Qwen3-VL 4B Instruct repeat; 5 frames; 6s context; no verifier; game 1 development slice"
```

Use a **new output directory for every run**. This case evaluates seconds
295–340 of development game 1, with reference steals at 308 and 330 seconds.
The ingest step may download the full source even though inference is
limited to the slice. Its `reference_stratified` candidate sampling is a
label-informed diagnostic, not an independent candidate-detector benchmark.
Never show reference event labels to the classifier.

Ollama 0.33.3 used at least 1,024 visual tokens per image in this test even
for a small smoke image; image resizing alone does not imply a smaller context
requirement. Five images plus the rubric required about 5,823 prompt tokens,
so the launcher uses 8,192 context tokens. Do not increase the frame count
without checking context capacity and memory. Base Settings remain at 4,096
for smaller calls; the local launcher explicitly overrides that value.

Local requests retain the request-count cap and token usage records but add
zero estimated cloud spend and must not rewrite the cloud spend ledger.
The original $5 cloud ceiling remains unchanged. Zero cloud spend does not
mean zero electricity cost or unlimited execution time.

## Reporting and stop conditions

Keep each report plus cumulative entries in `evals/iterations/history.jsonl`
and `evals/iterations/iteration-log.md`; summarize model/configuration changes
and outcomes in `evals/IMPLEMENTATION_NOTES.md` and `evals/STATUS.md`.

Record precision, recall, F1, TP/FP/FN, temporal recall, candidate coverage,
negative-window false positives, parsing/schema failures, provider failures,
runtime, model tag/digest, frame settings, and local token usage. Use the
processed-slice metrics for this limited run. Two positive events are a
feasibility check, not robust evidence of generalization. Report undefined
metrics explicitly rather than treating empty predictions as a pass.

Stop on memory pressure, persistent timeouts, missing model/server, or the
request cap. Do not turn on a cloud fallback. Compare fixed development
slices across iterations; document tradeoffs rather than tuning solely to
one event. The third game's sealed holdout is **not** for prompt/configuration
tuning. A local smoke-test success does not authorize a full-video quality
claim or imply the existing quality gates passed.

## Primary references

- [Ollama Qwen3-VL model listing](https://ollama.com/library/qwen3-vl)
- [Ollama vision API](https://docs.ollama.com/capabilities/vision)
- [Ollama hardware support](https://docs.ollama.com/gpu)

## Optional prompt batch experiment

`OLLAMA_NUM_BATCH=128` sets a smaller prompt-processing batch. Allowed values are 1–512; zero/unset omits the option and preserves server defaults. The report records the override. This may reduce peak memory, but must be measured on the local model; it does not reduce frame count or context length. Keep pressure monitoring enabled and record each experimental run separately.

## Durable per-call evaluation checkpoints

Set `HYPEREEL_PROVIDER_CHECKPOINT_DIR` to a fresh attempt directory. Each case writes a uniquely named JSONL journal with fsync after request authorization, returned usage, final window classification, and normal or interrupted scope exit. A `call_started` without a corresponding completion means usage/result are unknown. A hard kill can leave the last line incomplete; earlier complete lines survive. Journals are local evidence, not automatic resumable graph state, and never authorize replay. Journal-write failure blocks subsequent network requests. Reports/history link the journal path. No prompts, images, reference labels, or raw exception messages are journaled; final classification reasons are retained locally. The Ollama request explicitly disables input truncation/context shifting; oversized inputs must fail rather than silently discard frames.

## Current owner-directed memory policy

For continuation006 onward, the owner explicitly superseded stop-on-memory-warning guidance above. Record macOS pressure/RSS/swap without stopping for pressure alone. Preserve bounded requests, call caps, checkpoints, and actual operational-error reporting. Previous monitor interruptions are not proof of a crash or inability to complete.
