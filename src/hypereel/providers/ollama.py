"""Local-only Ollama inference over its native, non-streaming chat API.

Use an explicit instruct tag: generic Qwen tags may resolve to a thinking
variant whose hidden reasoning consumes the bounded output budget.
Ordered sampled images are not native video. No credentials, remote endpoints,
automatic model downloads, retries, or mock fallback are used here.
"""

from __future__ import annotations

import base64
import ipaddress
import json
import time
import urllib.request
from typing import Sequence
from urllib.parse import urlsplit

from ..config import Settings
from ..models import Classification, Recipe
from ..observability import (
    authorize_provider_call,
    record_local_provider_failure,
    record_local_provider_usage,
    record_provider_failure,
)
from .base import LLMProvider, VisionProvider
from ._util import (
    build_classification_prompt,
    build_verification_prompt,
    parse_classification_json,
)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Ollama redirects are disabled; use a direct loopback endpoint")


def _local_url(value: str) -> str:
    parsed = urlsplit(value)
    host = parsed.hostname or ""
    try:
        loopback = ipaddress.ip_address(host).is_loopback
    except ValueError:
        loopback = host == "localhost"
    if (parsed.scheme != "http" or not loopback or parsed.username is not None
            or parsed.password is not None or parsed.query or parsed.fragment
            or parsed.path not in {"", "/"}):
        raise ValueError("OLLAMA_BASE_URL must be an HTTP loopback origin without credentials")
    # Pin localhost to a literal rather than relying on hosts/DNS configuration.
    host = "127.0.0.1" if host == "localhost" else host
    authority = f"[{host}]" if ":" in host else host
    return f"http://{authority}:{parsed.port or 11434}/api/chat"


class _OllamaClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.url = _local_url(settings.ollama_base_url)
        self.model = settings.ollama_model.strip()
        if not self.model or "cloud" in self.model.lower():
            raise ValueError("OLLAMA_MODEL must name a local model, not a cloud model")
        if not 0 < settings.ollama_timeout_seconds <= 300:
            raise ValueError("OLLAMA_TIMEOUT_SECONDS must be between 0 and 300")
        if not 512 <= settings.ollama_num_ctx <= 8192:
            raise ValueError("OLLAMA_NUM_CTX must be between 512 and 8192")
        if not 0 <= settings.ollama_num_batch <= 512:
            raise ValueError("OLLAMA_NUM_BATCH must be zero (server default) or between 1 and 512")
        if not 1 <= settings.ollama_num_predict <= 1024:
            raise ValueError("OLLAMA_NUM_PREDICT must be between 1 and 1024")
        if not 128 <= settings.ollama_image_max_edge <= 1024:
            raise ValueError("OLLAMA_IMAGE_MAX_EDGE must be between 128 and 1024")
        self.opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}), _NoRedirect()
        )

    def chat(self, messages: list[dict], *, operation: str,
             json_mode: bool = False, max_tokens: int | None = None) -> str:
        if max_tokens is not None and max_tokens < 1:
            raise ValueError("max_tokens must be positive")
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "think": False,
            "truncate": False,
            "shift": False,
            "keep_alive": "5m",
            "options": {
                "temperature": 0,
                "seed": 0,
                "num_ctx": self.settings.ollama_num_ctx,
                "num_predict": min(max_tokens or self.settings.ollama_num_predict,
                                   self.settings.ollama_num_predict),
            },
        }
        if self.settings.ollama_num_batch:
            payload["options"]["num_batch"] = self.settings.ollama_num_batch
        if json_mode:
            payload["format"] = "json"
        request = urllib.request.Request(
            self.url, data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST",
        )
        authorize_provider_call(provider="ollama", model=self.model,
                                operation=operation, local=True)
        started = time.monotonic()
        try:
            with self.opener.open(request, timeout=self.settings.ollama_timeout_seconds) as response:
                body = json.load(response)
            if not isinstance(body, dict) or body.get("error"):
                raise ValueError("Ollama returned an error response")
            if body.get("done") is not True:
                raise ValueError("Ollama returned an incomplete response")
            if body.get("done_reason") == "length":
                record_local_provider_usage(
                    body, elapsed_seconds=time.monotonic() - started, status="truncated"
                )
                raise ValueError("Ollama output was truncated at the generation limit")
            content = body.get("message", {}).get("content")
            if not isinstance(content, str) or not content.strip():
                raise ValueError("Ollama returned empty message content")
            record_local_provider_usage(body, elapsed_seconds=time.monotonic() - started)
            return content
        except Exception as exc:
            record_local_provider_failure(exc, elapsed_seconds=time.monotonic() - started)
            raise


class OllamaVisionProvider(VisionProvider):
    name = "ollama"

    def __init__(self, settings: Settings) -> None:
        self._client = _OllamaClient(settings)
        self._settings = settings

    def _images(self, frame_paths: Sequence[str]) -> list[str]:
        import cv2

        if not frame_paths:
            raise ValueError("Ollama vision requires at least one readable frame")
        if len(frame_paths) > 16:
            raise ValueError("Ollama vision accepts at most 16 ordered frames per call")
        images = []
        for path in frame_paths:
            frame = cv2.imread(str(path))
            if frame is None:
                raise ValueError("Ollama vision received an unreadable frame")
            height, width = frame.shape[:2]
            scale = min(1.0, self._settings.ollama_image_max_edge / max(height, width))
            if scale < 1:
                frame = cv2.resize(frame, (max(1, round(width * scale)),
                                          max(1, round(height * scale))),
                                   interpolation=cv2.INTER_AREA)
            ok, encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ok:
                raise ValueError("Ollama frame encoding failed")
            images.append(base64.b64encode(encoded.tobytes()).decode("ascii"))
        return images

    def _classify(self, frame_paths: Sequence[str], recipe: Recipe, prompt: str,
                  operation: str) -> Classification:
        try:
            images = self._images(frame_paths)
            prompt += (f"\nThe {len(images)} attached images are in chronological order. "
                       "Use their sequence to establish the event, not a scoreboard change.")
            text = self._client.chat(
                [{"role": "user", "content": prompt, "images": images}],
                operation=operation, json_mode=True,
            )
            return parse_classification_json(text, recipe)
        except Exception as exc:
            record_provider_failure(exc)
            return Classification(moment_type=None, subject_present=False, confidence=0.0,
                                  reason=f"ollama error: {type(exc).__name__}: {exc}")

    def classify_window(self, frame_paths: Sequence[str], recipe: Recipe,
                        window_index: int = 0) -> Classification:
        prompt = build_classification_prompt(recipe)
        if self._settings.classification_context_seconds <= 0 or len(frame_paths) < 5:
            prompt = prompt.replace(
                "The first and last images provide before/after context. The middle "
                "images densely sample the candidate action. Classify the central action; "
                "do not label an unrelated event visible only in the outer context.",
                "All images sample the candidate action; there are no separate context images.",
            )
        return self._classify(frame_paths, recipe, prompt, "vision_classification")

    def verify_window(self, frame_paths: Sequence[str], recipe: Recipe,
                      proposed: Classification, window_index: int = 0) -> Classification:
        if proposed.moment_type is None:
            return proposed
        return self._classify(frame_paths, recipe, build_verification_prompt(recipe, proposed),
                              "vision_verification")


class OllamaLLMProvider(LLMProvider):
    """Local text generation; failures raise so callers can report unavailability.

    Unlike legacy providers, an empty fallback must not become an implicit
    successful judge verdict after the local request cap is reached.
    """
    name = "ollama"

    def __init__(self, settings: Settings) -> None:
        self._client = _OllamaClient(settings)

    def generate(self, prompt: str, *, system: str = "", max_tokens: int = 800) -> str:
        try:
            messages = [{"role": "system", "content": system}] if system else []
            messages.append({"role": "user", "content": prompt})
            return self._client.chat(messages, operation="quality_judge", max_tokens=max_tokens)
        except Exception as exc:
            record_provider_failure(exc)
            raise
