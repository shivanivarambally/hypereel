"""Local inference telemetry must never consume hosted-provider credit."""

from types import SimpleNamespace

import pytest

from hypereel.config import Settings
from hypereel.observability import (
    ProviderBudgetExceeded,
    authorize_provider_call,
    provider_budget_scope,
    record_local_provider_failure,
    record_local_provider_usage,
    record_provider_usage,
)


def settings_for(tmp_path, **overrides):
    return Settings(**{
        "provider_spend_ledger_path": str(tmp_path / "ledger.json"),
        "max_provider_calls": 2,
        "max_provider_spend_usd": 5,
        **overrides,
    })


def authorize_local():
    authorize_provider_call(provider="ollama", model="qwen3-vl:4b", operation="vision", local=True)


def test_local_works_with_exhausted_cloud_budget_without_rewriting_ledger(tmp_path):
    ledger = tmp_path / "ledger.json"
    original = '{"estimated_spend_usd": 5, "audit": "preserve"}\n'
    ledger.write_text(original)
    with provider_budget_scope(settings_for(tmp_path)) as state:
        authorize_local()
        record_local_provider_usage({
            "prompt_eval_count": 120,
            "eval_count": 12,
            "total_duration": 2_000_000_000,
            "load_duration": 500_000_000,
        }, elapsed_seconds=2.2)
        assert state["estimated_spend_usd"] == 0
        assert state["estimated_spend_before_run_usd"] == 5
        assert state["calls"][0] == {
            "provider": "ollama", "model": "qwen3-vl:4b", "operation": "vision",
            "status": "success", "local": True, "reserved_cost_usd": 0,
            "prompt_tokens": 120, "completion_tokens": 12, "total_tokens": 132,
            "estimated_cost_usd": 0, "latency_seconds": 2.2,
            "total_duration_ns": 2_000_000_000, "load_duration_ns": 500_000_000,
            "server_duration_seconds": 2,
        }
        with pytest.raises(ProviderBudgetExceeded, match="spend cap"):
            authorize_provider_call(provider="nebius", model="m", operation="vision")
    assert ledger.read_text() == original


def test_local_call_cap_and_failures_are_recorded_without_secrets(tmp_path):
    with provider_budget_scope(settings_for(tmp_path, max_provider_calls=1)) as state:
        authorize_local()
        record_local_provider_failure(TimeoutError("secret-url"), elapsed_seconds=3)
        with pytest.raises(ProviderBudgetExceeded, match="request cap"):
            authorize_local()
        assert state["attempted_calls"] == 1
        call = state["calls"][0]
        assert call["status"] == "error"
        assert call["error_type"] == "TimeoutError"
        assert call["estimated_cost_usd"] == 0
        assert "secret-url" not in str(state)
        # A subsequent failure must not overwrite the completed record.
        record_local_provider_failure(ValueError("different"), elapsed_seconds=4)
        assert call["error_type"] == "TimeoutError"
    assert not (tmp_path / "ledger.json").exists()


def test_cloud_and_local_share_call_cap_but_only_cloud_costs_are_charged(tmp_path):
    with provider_budget_scope(settings_for(tmp_path)) as state:
        authorize_provider_call(provider="nebius", model="m", operation="vision")
        record_provider_usage(SimpleNamespace(usage=SimpleNamespace(prompt_tokens=100, completion_tokens=10)))
        cloud_spend = state["estimated_spend_usd"]
        ledger_before = (tmp_path / "ledger.json").read_bytes()
        authorize_local()
        record_local_provider_usage({}, elapsed_seconds=1)
        assert state["calls"][-1]["total_tokens"] is None
        assert state["estimated_spend_usd"] == cloud_spend == pytest.approx(.0013)
        assert (tmp_path / "ledger.json").read_bytes() == ledger_before
        with pytest.raises(ProviderBudgetExceeded, match="request cap"):
            authorize_local()


def test_wrong_usage_recorder_cannot_charge_local_request(tmp_path):
    with provider_budget_scope(settings_for(tmp_path)) as state:
        authorize_local()
        with pytest.raises(ValueError, match="Local usage"):
            record_provider_usage(SimpleNamespace(usage=SimpleNamespace(prompt_tokens=100, completion_tokens=10)))
        assert state["estimated_spend_usd"] == 0
    assert not (tmp_path / "ledger.json").exists()


def test_local_recorders_are_noop_outside_scope():
    authorize_local()
    record_local_provider_usage({}, elapsed_seconds=1)
    record_local_provider_failure(ValueError("test"), elapsed_seconds=1)
