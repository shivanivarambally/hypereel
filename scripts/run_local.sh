#!/usr/bin/env bash
# Explicit local-only environment; never edit or expose the user's .env keys.
set -euo pipefail
cd "$(dirname "$0")/.."
export HYPEREEL_VISION_PROVIDER=ollama
export HYPEREEL_LLM_PROVIDER=ollama
export HYPEREEL_TRACING_ENABLED=false
export LANGSMITH_TRACING=false
export LANGCHAIN_TRACING_V2=false
export OLLAMA_BASE_URL=http://127.0.0.1:11434
export OLLAMA_MODEL="${OLLAMA_MODEL:-qwen3-vl:4b-instruct}"
export OLLAMA_NUM_CTX="${OLLAMA_NUM_CTX:-8192}"
export HYPEREEL_FRAMES_PER_CANDIDATE="${HYPEREEL_FRAMES_PER_CANDIDATE:-5}"
export HYPEREEL_CLASSIFICATION_CONTEXT_SECONDS="${HYPEREEL_CLASSIFICATION_CONTEXT_SECONDS:-6}"
export HYPEREEL_VERIFY_WITH_CORE_FRAMES="${HYPEREEL_VERIFY_WITH_CORE_FRAMES:-false}"
export HYPEREEL_MAX_PROVIDER_CALLS="${HYPEREEL_MAX_PROVIDER_CALLS:-8}"
if ! curl --noproxy '*' --fail --silent --max-time 3 "$OLLAMA_BASE_URL/api/tags" >/dev/null; then
  echo 'Start Ollama first: OLLAMA_NO_CLOUD=1 OLLAMA_HOST=127.0.0.1:11434 ollama serve' >&2
  exit 1
fi
mode="${1:-app}"
if [[ $# -gt 0 ]]; then shift; fi
case "$mode" in
  app) exec .venv/bin/python -m streamlit run src/hypereel/app.py --server.address 127.0.0.1 --server.port 8502 "$@" ;;
  eval) exec .venv/bin/python -m hypereel.evaluation.cli run --mode pipeline "$@" ;;
  *) echo 'Usage: bash scripts/run_local.sh app | eval --dataset FILE --output NEW_DIR --change-note NOTE' >&2; exit 2 ;;
esac
