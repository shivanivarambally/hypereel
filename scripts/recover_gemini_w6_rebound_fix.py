"""Recover the completed 035 model response after its strict time-basis parse stopped."""
from __future__ import annotations

import json
from pathlib import Path

from run_gemini_w6_rebound_fix import OUT, ROOT, evaluate, parse


def main() -> None:
    candidates = []
    for path in (ROOT / "evals/iterations/demo-integration-029").glob("*.json"):
        record = json.loads(path.read_text())
        if record.get("metadata", {}).get("iteration") == "035" and record.get("status") == "completed":
            candidates.append((path, record))
    if len(candidates) != 1:
        raise RuntimeError(f"expected exactly one completed 035 provider record, got {len(candidates)}")
    provider_path, provider = candidates[0]
    parts = provider["raw_response"]["candidates"][0]["content"]["parts"]
    raw = "".join(part.get("text", "") for part in parts if not part.get("thought"))
    events = parse(raw)
    original = json.loads((OUT / "report.json").read_text())
    recovered = dict(original)
    recovered.update(
        status="completed_after_time_basis_normalization",
        raw_text=raw,
        events=events,
        evaluation=evaluate(events),
        recovered_from=str(provider_path.relative_to(ROOT)),
        recovery_note="No second provider call; the completed 035 response was reparsed after normalizing clip-relative timestamps.",
    )
    target = OUT / "recovered-report.json"
    if target.exists():
        raise FileExistsError("refusing to overwrite recovered report")
    target.write_text(json.dumps(recovered, indent=2))
    print(json.dumps(recovered["evaluation"], indent=2))


if __name__ == "__main__":
    main()
