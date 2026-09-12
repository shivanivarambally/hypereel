"""Offline contract tests: local inference must never become cloud/mock inference."""

import base64
import io
import json
from pathlib import Path
import runpy
import sys
import urllib.error
import urllib.request

import pytest
from PIL import Image

from hypereel.config import Settings
from hypereel.observability import provider_budget_scope
from hypereel.providers.factory import get_llm_provider, get_vision_provider
from hypereel.providers.ollama import OllamaLLMProvider, OllamaVisionProvider


@pytest.fixture
def frames(tmp_path):
    result = []
    for index, color in enumerate(("red", "blue")):
        path = tmp_path / f"frame-{index}.png"
        Image.new("RGB", (32, 32), color).save(path)
        result.append(str(path))
    return result


@pytest.fixture
def requests(monkeypatch):
    captured = []

    def fake_open(self, request, *args, **kwargs):
        captured.append(request)
        return io.BytesIO(json.dumps({
            "message": {"role": "assistant", "content": json.dumps({
                "moment_type": "made_basket", "subject_present": True,
                "confidence": 0.8, "reason": "ball goes through the rim",
            })},
            "done": True, "prompt_eval_count": 120, "eval_count": 30,
        }).encode())

    monkeypatch.setattr(urllib.request.OpenerDirector, "open", fake_open)
    return captured


def test_factory_ollama_needs_no_api_key():
    settings = Settings(vision_provider="ollama", llm_provider="ollama")
    assert isinstance(get_vision_provider(settings), OllamaVisionProvider)
    assert isinstance(get_llm_provider(settings), OllamaLLMProvider)


@pytest.mark.parametrize("url", [
    "https://ollama.com", "http://192.168.1.2:11434", "http://example.com",
    "http://user:pass@127.0.0.1:11434", "http://localhost:11434/api",
    "http://localhost:11434?remote=1", "http://localhost:11434#remote",
])
def test_factory_rejects_nonlocal_or_ambiguous_url_without_mock_fallback(url):
    settings = Settings(vision_provider="ollama", llm_provider="ollama", ollama_base_url=url)
    with pytest.raises(ValueError):
        get_vision_provider(settings)
    with pytest.raises(ValueError):
        get_llm_provider(settings)


@pytest.mark.parametrize("url", ["http://127.0.0.1:11434", "http://localhost:11434", "http://[::1]:11434"])
def test_loopback_urls_accepted(url):
    assert isinstance(OllamaVisionProvider(Settings(ollama_base_url=url)), OllamaVisionProvider)


def test_cloud_model_rejected():
    with pytest.raises(ValueError):
        OllamaVisionProvider(Settings(ollama_model="qwen3-vl:235b-cloud"))


def test_vision_posts_ordered_images_with_bounded_generation(frames, requests, basketball_recipe):
    settings = Settings(ollama_num_ctx=4096, ollama_num_predict=128)
    result = OllamaVisionProvider(settings).classify_window(frames, basketball_recipe)
    assert result.moment_type == "made_basket"
    assert len(requests) == 1
    assert requests[0].full_url == "http://127.0.0.1:11434/api/chat"
    payload = json.loads(requests[0].data)
    assert payload["model"] == "qwen3-vl:4b-instruct"
    assert payload["stream"] is False
    assert payload["truncate"] is False
    assert payload["shift"] is False
    assert payload["options"]["num_predict"] == 128
    assert payload["options"]["num_ctx"] == 4096
    assert payload["options"]["temperature"] == 0
    encoded = [image for message in payload["messages"] for image in message.get("images", [])]
    assert len(encoded) == 2
    pixels = [Image.open(io.BytesIO(base64.b64decode(image))).convert("RGB").getpixel((0, 0)) for image in encoded]
    assert pixels[0][0] > pixels[0][2]  # first frame remains red
    assert pixels[1][2] > pixels[1][0]  # second frame remains blue
    assert not requests[0].has_header("Authorization")


def test_llm_respects_smaller_requested_output_limit(requests):
    OllamaLLMProvider(Settings(ollama_num_predict=128)).generate("summarize", max_tokens=32)
    assert json.loads(requests[0].data)["options"]["num_predict"] == 32


def test_llm_never_sends_unlimited_output_request(requests):
    with pytest.raises(ValueError, match="max_tokens must be positive"):
        OllamaLLMProvider(Settings()).generate("summarize", max_tokens=-1)
    assert not requests or json.loads(requests[0].data)["options"]["num_predict"] >= 1


def test_local_llm_call_cap_raises_instead_of_empty_judge_success(requests):
    from hypereel.observability import ProviderBudgetExceeded

    settings = Settings(max_provider_calls=1, provider_spend_ledger_path="")
    provider = OllamaLLMProvider(settings)
    with provider_budget_scope(settings):
        assert provider.generate("first request")
        with pytest.raises(ProviderBudgetExceeded, match="request cap"):
            provider.generate("second request")
    assert len(requests) == 1


@pytest.mark.parametrize("setting,value", [
    ("ollama_num_predict", -1), ("ollama_num_predict", 100000),
    ("ollama_num_ctx", 100000), ("ollama_timeout_seconds", 0),
    ("ollama_image_max_edge", 10000),
])
def test_unbounded_resource_settings_rejected(setting, value):
    with pytest.raises(ValueError):
        OllamaVisionProvider(Settings(**{setting: value}))


def test_redirects_to_remote_endpoints_are_rejected():
    from hypereel.providers.ollama import _NoRedirect
    handler = _NoRedirect()
    request = urllib.request.Request("http://127.0.0.1:11434/api/chat")
    with pytest.raises(ValueError):
        handler.redirect_request(request, None, 302, "redirect", {}, "https://example.com/api/chat")


def test_large_images_are_resized_before_request(tmp_path, requests, basketball_recipe):
    path = tmp_path / "large.png"
    Image.new("RGB", (1280, 720), "red").save(path)
    OllamaVisionProvider(Settings(ollama_image_max_edge=448)).classify_window([str(path)], basketball_recipe)
    encoded = json.loads(requests[0].data)["messages"][0]["images"][0]
    image = Image.open(io.BytesIO(base64.b64decode(encoded)))
    assert max(image.size) == 448


def test_missing_frame_does_not_call_server(requests, basketball_recipe):
    result = OllamaVisionProvider(Settings()).classify_window([], basketball_recipe)
    assert result.confidence == 0
    assert not requests


def test_too_many_frames_rejected_before_http(frames, requests, basketball_recipe):
    result = OllamaVisionProvider(Settings()).classify_window(frames * 9, basketball_recipe)
    assert result.confidence == 0
    assert not requests


def test_output_limit_truncation_is_failure_even_with_parseable_content(monkeypatch, frames, basketball_recipe):
    def truncated(self, request, *args, **kwargs):
        return io.BytesIO(json.dumps({
            "message": {"content": '{"moment_type":"block","subject_present":true,"confidence":0.9,"reason":"block"}'},
            "done": True, "done_reason": "length", "prompt_eval_count": 120, "eval_count": 128,
        }).encode())
    monkeypatch.setattr(urllib.request.OpenerDirector, "open", truncated)
    result = OllamaVisionProvider(Settings()).classify_window(frames, basketball_recipe)
    assert result.moment_type is None
    assert result.confidence == 0


def test_local_usage_preserves_cloud_ledger_and_enforces_call_cap(tmp_path, frames, requests, basketball_recipe):
    ledger = tmp_path / "cloud-spend.json"
    original = '{"estimated_spend_usd":5.0}\n'
    ledger.write_text(original)
    settings = Settings(max_provider_calls=1, max_provider_spend_usd=5,
                        provider_spend_ledger_path=str(ledger))
    provider = OllamaVisionProvider(settings)
    with provider_budget_scope(settings) as state:
        first = provider.classify_window(frames, basketball_recipe)
        second = provider.classify_window(frames, basketball_recipe)
    assert first.moment_type == "made_basket"
    assert second.moment_type is None
    assert second.confidence == 0
    assert len(requests) == 1
    assert state["attempted_calls"] == 1
    assert state["estimated_spend_usd"] == 0
    assert state["calls"][0]["prompt_tokens"] == 120
    assert state["calls"][0]["completion_tokens"] == 30
    assert state["calls"][0]["estimated_cost_usd"] == 0
    assert ledger.read_text() == original


def test_server_failure_is_error_not_mock(monkeypatch, frames, basketball_recipe):
    def fail(self, request, *args, **kwargs):
        raise urllib.error.URLError("connection refused")
    monkeypatch.setattr(urllib.request.OpenerDirector, "open", fail)
    result = OllamaVisionProvider(Settings()).classify_window(frames, basketball_recipe)
    assert result.moment_type is None
    assert result.confidence == 0
    assert "error" in result.reason.lower()


def test_invalid_json_is_not_a_successful_classification(monkeypatch, frames, basketball_recipe):
    def garbage(self, request, *args, **kwargs):
        return io.BytesIO(b'{"message":{"content":"not valid classification JSON"},"done":true}')
    monkeypatch.setattr(urllib.request.OpenerDirector, "open", garbage)
    result = OllamaVisionProvider(Settings()).classify_window(frames, basketball_recipe)
    assert result.moment_type is None
    assert result.confidence == 0


@pytest.mark.parametrize("vision_reply,expected", [(' {"color":"red"} ', True), ('{"color":"blue"}', False)])
def test_probe_records_real_response_outcome_without_quality_claim(monkeypatch, tmp_path, vision_reply, expected):
    from hypereel.providers.ollama import _OllamaClient
    calls = []
    def chat(self, messages, **kwargs):
        calls.append((messages, kwargs))
        return "LOCAL_OK" if len(calls) == 1 else vision_reply
    monkeypatch.setattr(_OllamaClient, "chat", chat)
    output = tmp_path / "probe.json"
    monkeypatch.setattr(sys, "argv", ["probe_ollama.py", "--output", str(output)])
    script = Path(__file__).resolve().parents[1] / "scripts" / "probe_ollama.py"
    entry = runpy.run_path(str(script))
    assert entry["main"]() == (0 if expected else 1)
    report = json.loads(output.read_text())
    assert report["passed"] is expected
    assert "not quality evidence" in report["scope"]
    assert report["provider_usage"]["max_calls"] == 2
    assert len(calls) == 2
    assert calls[1][0][0]["images"]


def test_probe_preserves_existing_report(monkeypatch, tmp_path):
    from hypereel.providers.ollama import _OllamaClient
    def forbidden(*args, **kwargs):
        pytest.fail("existing output must be rejected before inference")
    monkeypatch.setattr(_OllamaClient, "chat", forbidden)
    output = tmp_path / "probe.json"
    output.write_text("existing report")
    monkeypatch.setattr(sys, "argv", ["probe_ollama.py", "--output", str(output)])
    script = Path(__file__).resolve().parents[1] / "scripts" / "probe_ollama.py"
    entry = runpy.run_path(str(script))
    with pytest.raises(SystemExit) as error:
        entry["main"]()
    assert error.value.code == 2
    assert output.read_text() == "existing report"


@pytest.mark.parametrize("batch", [0, 128])
def test_optional_batch_size_preserves_default_and_records_override(batch, requests):
    from hypereel.config import get_settings
    from hypereel.evaluation.pipeline import inference_configuration

    settings = Settings(ollama_num_batch=batch, llm_provider="ollama")
    OllamaLLMProvider(settings).generate("batch test")
    options = json.loads(requests[0].data)["options"]
    if batch:
        assert options["num_batch"] == batch
    else:
        assert "num_batch" not in options
    assert inference_configuration(settings)["ollama"]["num_batch"] == (batch or None)


@pytest.mark.parametrize("batch", [-1, 513])
def test_invalid_batch_size_rejected_before_request(batch, requests):
    with pytest.raises(ValueError, match="OLLAMA_NUM_BATCH"):
        OllamaLLMProvider(Settings(ollama_num_batch=batch))
    assert not requests


def test_batch_size_environment(monkeypatch):
    from hypereel.config import get_settings
    monkeypatch.setenv("OLLAMA_NUM_BATCH", "128")
    assert get_settings().ollama_num_batch == 128
