"""Two-call local capability check; not a basketball quality evaluation."""
import argparse
import base64
from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path

import cv2
import numpy as np

from hypereel.config import get_settings
from hypereel.observability import provider_budget_scope
from hypereel.providers.ollama import _OllamaClient


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output must not already exist; previous results are preserved")
    settings = replace(get_settings(), vision_provider="ollama", llm_provider="ollama",
                       tracing_enabled=False, max_provider_calls=2)
    client = _OllamaClient(settings)
    result = {"created_at": datetime.now(timezone.utc).isoformat(),
              "model": settings.ollama_model, "provider": "ollama",
              "scope": "synthetic capability check; not quality evidence"}
    with provider_budget_scope(settings) as budget:
        try:
            result["text_response"] = client.chat(
                [{"role": "user", "content": "Reply with exactly LOCAL_OK"}],
                operation="text_smoke", max_tokens=256)
            frame = np.zeros((128, 128, 3), dtype=np.uint8)
            frame[:, :, 2] = 255
            ok, encoded = cv2.imencode(".png", frame)
            assert ok
            result["vision_response"] = client.chat(
                [{"role": "user", "content": 'What is the dominant color? Return JSON {"color":"name"}.',
                  "images": [base64.b64encode(encoded.tobytes()).decode()]}],
                operation="vision_smoke", json_mode=True, max_tokens=256)
            result["passed"] = (
                result["text_response"].strip() == "LOCAL_OK"
                and json.loads(result["vision_response"]).get("color", "").lower() == "red")
        except Exception as exc:
            result.update(passed=False, error=f"{type(exc).__name__}: {exc}")
        result["provider_usage"] = budget
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
