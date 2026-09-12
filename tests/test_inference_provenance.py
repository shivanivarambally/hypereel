import json

from hypereel.config import Settings
from hypereel.evaluation.report import append_iteration_history
from hypereel.evaluation.pipeline import (
    classification_provider_error_rate,
    inference_configuration,
)
from hypereel.models import Classification


def test_local_inference_configuration_is_safe_and_specific():
    settings = Settings(vision_provider="ollama", ollama_model="qwen3-vl:4b-instruct",
                        ollama_num_ctx=2048, ollama_num_predict=128,
                        ollama_image_max_edge=336, frames_per_candidate=5,
                        nebius_api_key="do-not-log", ollama_base_url="http://localhost:11434")
    configuration = inference_configuration(settings)
    assert configuration["ollama"]["model"] == "qwen3-vl:4b-instruct"
    assert configuration["ollama"]["num_ctx"] == 2048
    assert configuration["ollama"]["image_max_edge"] == 336
    assert configuration["frames_per_candidate"] == 5
    assert configuration["ollama"]["frame_timestamps_supplied"] is False
    assert "do-not-log" not in str(configuration)
    assert "localhost" not in str(configuration)
    assert "ollama" not in inference_configuration(Settings())


def test_provider_error_rate_separates_failures_from_valid_negative_decisions():
    def classification(reason):
        return Classification(moment_type=None, confidence=0, subject_present=False, reason=reason)
    values = [classification("ollama error: timeout"), classification("no visible event")]
    assert classification_provider_error_rate(values, "ollama") == 0.5
    assert classification_provider_error_rate([], "ollama") is None
    assert classification_provider_error_rate(
        [classification("nebius verification error: timeout")], "nebius"
    ) == 1.0


def test_cumulative_history_preserves_configuration_usage_and_prior_iterations(tmp_path):
    configuration = inference_configuration(Settings(
        vision_provider="ollama", llm_provider="ollama", ollama_num_ctx=8192,
        frames_per_candidate=5, classification_context_seconds=6,
    ))
    usage = {"calls": [{"provider": "ollama", "model": "qwen3-vl:4b-instruct",
                        "status": "success", "prompt_tokens": 900,
                        "completion_tokens": 100, "estimated_cost_usd": 0}],
             "attempted_calls": 1, "estimated_spend_usd": 0}
    report = {
        "evaluation_run_id": "local-first", "created_at": "2026-09-12T00:00:00Z",
        "mode": "pipeline", "dataset_sha256": "fixture-dataset",
        "code_revision": "fixture-revision", "working_tree_dirty": True,
        "metric_version": "fixture-version",
        "cases": [{"case_id": "development-only", "status": "success",
                   "metrics": {"precision": 0.5, "recall": 1.0},
                   "inference_configuration": configuration, "provider_usage": usage,
                   "provider_attempted_calls": 1, "estimated_provider_spend_usd": 0,
                   "estimated_provider_cumulative_spend_usd": 2.53027}],
    }
    path = tmp_path / "history.jsonl"
    append_iteration_history(report, path, "first local baseline")
    first_bytes = path.read_bytes()
    report["evaluation_run_id"] = "local-second"
    report["cases"][0]["metrics"] = {"precision": 1.0, "recall": 0.5}
    append_iteration_history(report, path, "second diagnostic")
    assert path.read_bytes().startswith(first_bytes)
    first, second = [json.loads(line) for line in path.read_text().splitlines()]
    assert first["cases"][0]["inference_configuration"] == configuration
    assert first["cases"][0]["provider_usage"] == usage
    assert first["cases"][0]["metrics"]["precision"] == 0.5
    assert second["cases"][0]["metrics"]["precision"] == 1.0
    assert second["change_note"] == "second diagnostic"
    assert first["cases"][0]["estimated_provider_cumulative_spend_usd"] == 2.53027
