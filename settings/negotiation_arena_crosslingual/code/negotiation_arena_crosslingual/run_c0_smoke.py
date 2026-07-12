#!/usr/bin/env python3
"""Run the first real C0 EN buy/sell smoke episode when gates are satisfied."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import traceback
import types
import urllib.error
import urllib.request
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = ROOT / "external" / "NegotiationArena"
sys.path.insert(0, str(ROOT / "code" / "negotiation_arena_crosslingual"))
sys.path.insert(0, str(UPSTREAM))

from local_model_adapter import LocalModelError, load_adapter_config, make_local_chat  # noqa: E402
from language_channels import channel_compliance, output_channel_instruction  # noqa: E402
from offer_parser import offer_parse_rate, parse_offer  # noqa: E402
from process_metrics import episode_payoff_asymmetry, first_offer_anchoring  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def append_event(kind: str, status: str, message: str) -> None:
    path = ROOT / "plan" / "events.jsonl"
    record = {"ts": utc_now(), "kind": kind, "status": status, "message": message}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_json(relative_path: str, payload: dict[str, Any]) -> Path:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_plan() -> dict[str, Any]:
    return json.loads((ROOT / "config" / "smoke_plan.json").read_text(encoding="utf-8"))


def load_smoke_model_config() -> dict[str, Any] | None:
    path = ROOT / "config" / "smoke_model.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_benchmark_model_config() -> dict[str, Any] | None:
    path = ROOT / "config" / "benchmark_model.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def smoke_openai_allowed(config: dict[str, Any] | None) -> bool:
    if not config:
        return False
    policy = config.get("policy", {})
    return (
        config.get("provider") == "openai"
        and bool(policy.get("benchmark_smoke_may_use_openai_key"))
        and not bool(policy.get("codex_auth_uses_openai_key"))
    )


def benchmark_openai_allowed(config: dict[str, Any] | None) -> bool:
    if not config:
        return False
    policy = config.get("policy", {})
    return (
        config.get("provider") == "openai"
        and bool(policy.get("benchmark_execution_may_use_openai_key"))
        and bool(policy.get("openai_allowed_by_user"))
        and bool(policy.get("must_label_artifacts_as_openai_evidence"))
        and not bool(policy.get("codex_auth_uses_openai_key"))
    )


def read_api_key(config: dict[str, Any]) -> tuple[str | None, str | None]:
    env_key = str(config.get("env_key", "OPENAI_API_KEY"))
    env_value = os.environ.get(env_key)
    if env_value:
        return env_value.strip(), f"env:{env_key}"

    for candidate in config.get("api_key_file_candidates", []):
        path = (ROOT / str(candidate)).resolve()
        if path.exists():
            value = path.read_text(encoding="utf-8").strip()
            if value:
                return value, f"file:{candidate}"
    return None, None


class OpenAIConfiguredError(RuntimeError):
    """Raised when an explicitly allowed OpenAI benchmark/smoke client cannot respond."""


class OpenAIExternalRequestNeeded(RuntimeError):
    """Raised when the shell bridge must send the next OpenAI request."""

    def __init__(self, request_path: Path) -> None:
        super().__init__(f"OpenAI shell bridge request is ready: {request_path}")
        self.request_path = request_path


class OpenAIConfiguredChat:
    def __init__(self, config: dict[str, Any], *, purpose: str, env_model_default: str) -> None:
        self.config = config
        self.purpose = purpose
        self.model = os.environ.get(
            str(config.get("env_model", env_model_default)),
            str(config.get("default_model", "gpt-5.4-mini-2026-03-17")),
        )
        self.base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.endpoint = f"{self.base_url}/chat/completions"
        self.api_key, self.api_key_source = read_api_key(config)
        if not self.api_key:
            raise OpenAIConfiguredError(
                f"OpenAI {self.purpose} override is configured, but no API key was found in "
                f"{config.get('env_key', 'OPENAI_API_KEY')} or configured api_key_file_candidates."
            )

    def complete(self, messages: list[dict[str, str]], **overrides: Any) -> str:
        payload = self._build_payload(messages, **overrides)
        return self._complete_with_urllib(payload)

    def _build_payload(self, messages: list[dict[str, str]], **overrides: Any) -> dict[str, Any]:
        max_tokens = overrides.pop("max_tokens", None)
        max_completion_tokens = overrides.pop("max_completion_tokens", None)
        if max_completion_tokens is None:
            max_completion_tokens = max_tokens if max_tokens is not None else 400

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0,
            self._token_limit_field(): max_completion_tokens,
        }
        payload.update({key: value for key, value in overrides.items() if value is not None})
        return payload

    def _token_limit_field(self) -> str:
        configured = self.config.get("chat_completion_token_field")
        if configured in {"max_tokens", "max_completion_tokens"}:
            return str(configured)
        model = self.model.lower()
        if model.startswith(("gpt-5", "o1", "o3", "o4")):
            return "max_completion_tokens"
        return "max_tokens"

    def _extract_content(self, body: str) -> str:
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as exc:
            raise OpenAIConfiguredError(f"OpenAI {self.purpose} endpoint returned non-JSON response") from exc
        choices = parsed.get("choices")
        if not isinstance(choices, list) or not choices:
            raise OpenAIConfiguredError(f"OpenAI {self.purpose} endpoint response has no choices")
        message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise OpenAIConfiguredError(f"OpenAI {self.purpose} endpoint response content is empty")
        return content

    def _complete_with_urllib(self, payload: dict[str, Any]) -> str:
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise OpenAIConfiguredError(f"OpenAI {self.purpose} request failed: HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            if self._should_try_curl(exc):
                return self._complete_with_curl(payload, f"urllib failed: {exc}")
            raise OpenAIConfiguredError(f"OpenAI {self.purpose} request failed: {exc}") from exc

        return self._extract_content(body)

    def _should_try_curl(self, exc: urllib.error.URLError) -> bool:
        reason = str(getattr(exc, "reason", exc)).lower()
        return (
            "certificate" in reason
            or "ssl" in reason
            or "nodename nor servname" in reason
            or "name or service not known" in reason
            or "temporary failure in name resolution" in reason
        )

    def _complete_with_curl(self, payload: dict[str, Any], previous_error: str) -> str:
        curl = shutil.which("curl")
        if not curl:
            raise OpenAIConfiguredError(
                f"OpenAI {self.purpose} request failed: {previous_error}; curl fallback unavailable"
            )

        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=True) as payload_file:
            json.dump(payload, payload_file)
            payload_file.flush()
            config = "\n".join(
                [
                    f'url = "{self.endpoint}"',
                    'request = "POST"',
                    'header = "Content-Type: application/json"',
                    f'header = "Authorization: Bearer {self.api_key}"',
                    f'data-binary = "@{payload_file.name}"',
                    f"max-time = {int(max(1, float(self.config.get('timeout_seconds', 120))))}",
                    "silent",
                    "show-error",
                    "location",
                    "fail-with-body",
                    "",
                ]
            )
            completed = subprocess.run(
                [curl, "--config", "-"],
                input=config,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

        if completed.returncode != 0:
            stderr_detail = completed.stderr.strip()
            stdout_detail = completed.stdout.strip()
            detail_parts = []
            if stderr_detail:
                detail_parts.append(f"stderr={stderr_detail}")
            if stdout_detail:
                detail_parts.append(f"body={stdout_detail}")
            detail = "; ".join(detail_parts)
            raise OpenAIConfiguredError(
                f"OpenAI {self.purpose} request failed: "
                f"{previous_error}; curl fallback exit {completed.returncode}: {detail[:500]}"
            )
        return self._extract_content(completed.stdout)


class OpenAISmokeChat(OpenAIConfiguredChat):
    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config, purpose="smoke", env_model_default="OPENAI_SMOKE_MODEL")


class OpenAIBenchmarkChat(OpenAIConfiguredChat):
    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config, purpose="benchmark", env_model_default="OPENAI_BENCHMARK_MODEL")


_BRIDGE_CURSOR = 0


class OpenAIBenchmarkShellBridgeChat(OpenAIConfiguredChat):
    """Replay prior responses and externalize the next request for shell curl."""

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config, purpose="benchmark", env_model_default="OPENAI_BENCHMARK_MODEL")
        self.state_path = Path(
            os.environ.get(
                "NEGOTIATION_OPENAI_BRIDGE_STATE",
                str(ROOT / "artifacts" / "tmp" / "c1_openai_bridge_state.json"),
            )
        )
        self.request_path = Path(
            os.environ.get(
                "NEGOTIATION_OPENAI_BRIDGE_REQUEST",
                str(ROOT / "artifacts" / "tmp" / "c1_openai_bridge_request.json"),
            )
        )
        self.payload_path = Path(
            os.environ.get(
                "NEGOTIATION_OPENAI_BRIDGE_PAYLOAD",
                str(ROOT / "artifacts" / "tmp" / "c1_openai_bridge_payload.json"),
            )
        )

    def _load_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {"responses": []}
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def complete(self, messages: list[dict[str, str]], **overrides: Any) -> str:
        global _BRIDGE_CURSOR
        payload = self._build_payload(messages, **overrides)
        state = self._load_state()
        responses = state.get("responses", [])
        if _BRIDGE_CURSOR < len(responses):
            response = responses[_BRIDGE_CURSOR]
            _BRIDGE_CURSOR += 1
            return str(response["text"])

        self.request_path.parent.mkdir(parents=True, exist_ok=True)
        self.payload_path.parent.mkdir(parents=True, exist_ok=True)
        self.payload_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        request = {
            "checked_at": utc_now(),
            "status": "NEEDS_OPENAI_RESPONSE",
            "provider": "openai_benchmark_shell_bridge",
            "model": self.model,
            "endpoint": self.endpoint,
            "api_key_source": self.api_key_source,
            "request_index": _BRIDGE_CURSOR,
            "payload_path": str(self.payload_path),
            "state_path": str(self.state_path),
            "evidence_scope": "OpenAI benchmark override evidence; not Qwen3-1.7B evidence",
            "message": "Send payload_path to endpoint with the configured OpenAI key, append the response text to state_path, then rerun the Python runner.",
        }
        self.request_path.write_text(json.dumps(request, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        raise OpenAIExternalRequestNeeded(self.request_path)


def install_optional_upstream_import_shims() -> None:
    """Let unused upstream optional agent modules import without their SDKs."""
    if "openai" not in sys.modules:
        openai_module = types.ModuleType("openai")

        class _UnavailableOpenAI:
            def __init__(self, *_args: Any, **_kwargs: Any) -> None:
                raise RuntimeError("OpenAI SDK shim is import-only for this smoke runner")

        openai_module.OpenAI = _UnavailableOpenAI  # type: ignore[attr-defined]
        sys.modules["openai"] = openai_module

    if "anthropic" not in sys.modules:
        anthropic_module = types.ModuleType("anthropic")

        class _UnavailableAnthropic:
            def __init__(self, *_args: Any, **_kwargs: Any) -> None:
                raise RuntimeError("Anthropic SDK shim is import-only for this smoke runner")

        anthropic_module.Anthropic = _UnavailableAnthropic  # type: ignore[attr-defined]
        anthropic_module.HUMAN_PROMPT = "\n\nHuman:"
        anthropic_module.AI_PROMPT = "\n\nAssistant:"
        sys.modules["anthropic"] = anthropic_module


def selected_provider() -> str:
    override = os.environ.get("NEGOTIATION_SMOKE_PROVIDER")
    if override:
        return override
    benchmark_config = load_benchmark_model_config()
    if benchmark_openai_allowed(benchmark_config):
        return "openai_benchmark"
    smoke_config = load_smoke_model_config()
    return "openai_smoke" if smoke_openai_allowed(smoke_config) else "local_qwen"


def make_chat_client(provider: str) -> tuple[Any, dict[str, Any]]:
    if provider == "openai_smoke":
        config = load_smoke_model_config()
        if not smoke_openai_allowed(config):
            raise OpenAIConfiguredError(
                "OpenAI smoke provider was requested but is not allowed by config/smoke_model.json"
            )
        client = OpenAISmokeChat(config or {})
        return client, {
            "provider": "openai_smoke",
            "model": client.model,
            "endpoint": client.endpoint,
            "api_key_source": client.api_key_source,
            "evidence_scope": "runner bring-up only; not Qwen3-1.7B research-matrix evidence",
        }

    if provider == "openai_benchmark":
        config = load_benchmark_model_config()
        if not benchmark_openai_allowed(config):
            raise OpenAIConfiguredError(
                "OpenAI benchmark provider was requested but is not allowed by config/benchmark_model.json"
            )
        client = OpenAIBenchmarkChat(config or {})
        return client, {
            "provider": "openai_benchmark",
            "model": client.model,
            "endpoint": client.endpoint,
            "api_key_source": client.api_key_source,
            "evidence_scope": "OpenAI benchmark override evidence; not Qwen3-1.7B evidence",
        }

    if provider == "openai_benchmark_shell_bridge":
        config = load_benchmark_model_config()
        if not benchmark_openai_allowed(config):
            raise OpenAIConfiguredError(
                "OpenAI benchmark shell bridge was requested but is not allowed by config/benchmark_model.json"
            )
        client = OpenAIBenchmarkShellBridgeChat(config or {})
        return client, {
            "provider": "openai_benchmark_shell_bridge",
            "model": client.model,
            "endpoint": client.endpoint,
            "api_key_source": client.api_key_source,
            "evidence_scope": "OpenAI benchmark override evidence; not Qwen3-1.7B evidence",
        }

    config = load_adapter_config()
    return make_local_chat(config), {
        "provider": config.provider,
        "model": config.model,
        "endpoint": config.endpoint,
        "evidence_scope": "Qwen/local model run",
    }


def run_endpoint_probe(provider: str, failed_command: str | None = None) -> dict[str, Any]:
    if provider == "openai_benchmark_shell_bridge":
        try:
            _client, metadata = make_chat_client(provider)
        except OpenAIConfiguredError as exc:
            probe = {
                "checked_at": utc_now(),
                "status": "BLOCKED",
                "provider": provider,
                "failed_command": failed_command,
                "error": str(exc),
                "message": "OpenAI benchmark shell bridge is configured but not usable.",
                "next_action": (
                    "Provide an OpenAI API key via the configured api_key_file_candidates or environment key, "
                    f"then rerun {failed_command or 'bash scripts/run_c1_openai_bridge_baseline.sh'}."
                ),
            }
            artifact = write_json("artifacts/results/benchmark_model_probe.json", probe)
            append_event("benchmark_model", "BLOCKED", f"OpenAI benchmark shell bridge failed; artifact={artifact.relative_to(ROOT)}")
            raise SystemExit(2) from exc

        probe = {
            "checked_at": utc_now(),
            "status": "BRIDGE_READY",
            **metadata,
            "failed_command": None,
            "message": "OpenAI benchmark shell bridge is ready; endpoint calls are made by the surrounding shell curl driver.",
        }
        artifact = write_json("artifacts/results/benchmark_model_probe.json", probe)
        append_event("benchmark_model", "OK", f"OpenAI benchmark shell bridge ready; artifact={artifact.relative_to(ROOT)}")
        return metadata

    if provider in {"openai_smoke", "openai_benchmark"}:
        is_benchmark = provider == "openai_benchmark"
        artifact_path = (
            "artifacts/results/benchmark_model_probe.json"
            if is_benchmark
            else "artifacts/results/smoke_model_probe.json"
        )
        event_kind = "benchmark_model" if is_benchmark else "smoke_model"
        failed_command = failed_command or (
            "NEGOTIATION_SMOKE_PROVIDER=openai_benchmark python3 scripts/run_c0_smoke.py"
            if is_benchmark
            else "NEGOTIATION_SMOKE_PROVIDER=openai_smoke python3 scripts/run_c0_smoke.py"
        )
        purpose = "benchmark" if is_benchmark else "smoke"
        try:
            client, metadata = make_chat_client(provider)
        except OpenAIConfiguredError as exc:
            probe = {
                "checked_at": utc_now(),
                "status": "BLOCKED",
                "provider": provider,
                "failed_command": failed_command,
                "error": str(exc),
                "message": f"OpenAI {purpose} override is configured but not usable.",
                "next_action": (
                    "Provide an OpenAI API key via the configured api_key_file_candidates or environment key, "
                    f"then rerun {failed_command}."
                ),
            }
            artifact = write_json(artifact_path, probe)
            append_event(event_kind, "BLOCKED", f"OpenAI {purpose} model probe failed; artifact={artifact.relative_to(ROOT)}")
            raise SystemExit(2) from exc

        probe = {
            "checked_at": utc_now(),
            "status": "OK",
            **metadata,
            "failed_command": None,
            "message": f"OpenAI {purpose} endpoint responded to a tiny chat-completions probe.",
        }
        try:
            text = client.complete(
                [
                    {"role": "system", "content": "You are a concise endpoint probe."},
                    {"role": "user", "content": "Reply with OK."},
                ],
                max_tokens=8,
                temperature=0,
            )
        except OpenAIConfiguredError as exc:
            probe.update(
                {
                    "status": "BLOCKED",
                    "failed_command": failed_command,
                    "error": str(exc),
                    "message": f"OpenAI {purpose} endpoint is not reachable from this session.",
                    "next_action": (
                        f"Fix network/API-key access for the configured OpenAI {purpose} model, "
                        f"then rerun {failed_command}."
                    ),
                }
            )
            artifact = write_json(artifact_path, probe)
            append_event(event_kind, "BLOCKED", f"OpenAI {purpose} model probe failed; artifact={artifact.relative_to(ROOT)}")
            raise SystemExit(2) from exc

        probe["response_preview"] = text[:200]
        artifact = write_json(artifact_path, probe)
        append_event(event_kind, "OK", f"OpenAI {purpose} model probe passed; artifact={artifact.relative_to(ROOT)}")
        return metadata

    config = load_adapter_config()
    probe = {
        "checked_at": utc_now(),
        "status": "OK",
        "provider": config.provider,
        "model": config.model,
        "endpoint": config.endpoint,
        "failed_command": None,
        "message": "Local Qwen provider responded to a tiny generation probe.",
    }
    try:
        text = make_local_chat(config).complete(
            [
                {"role": "system", "content": "You are a concise endpoint probe."},
                {"role": "user", "content": "Reply with OK."},
            ],
            max_tokens=8,
            temperature=0,
        )
    except LocalModelError as exc:
        probe.update(
            {
                "status": "BLOCKED",
                "failed_command": "python3 scripts/local_model_adapter.py --live-probe",
                "error": str(exc),
                "message": "Local Qwen provider is not usable from this session.",
                "next_action": (
                    "For local_transformers, ensure Qwen/Qwen3-1.7B is present in the "
                    "Hugging Face cache with torch/transformers installed. For local_vllm, "
                    "start a local OpenAI-compatible Qwen3-1.7B chat-completions server "
                    "or set LOCAL_QWEN_BASE_URL. Then rerun ./harness.sh run-smoke for "
                    "smoke or bash scripts/run_c0_baseline.sh for the C0 baseline."
                ),
            }
        )
        artifact = write_json("artifacts/results/model_endpoint_probe.json", probe)
        append_event(
            "model_endpoint",
            "BLOCKED",
            f"Local Qwen provider probe failed; artifact={artifact.relative_to(ROOT)}; "
            "failed_command=python3 scripts/local_model_adapter.py --live-probe",
        )
        raise SystemExit(2) from exc

    probe["response_preview"] = text[:200]
    artifact = write_json("artifacts/results/model_endpoint_probe.json", probe)
    append_event("model_endpoint", "OK", f"Local Qwen provider probe passed; artifact={artifact.relative_to(ROOT)}")
    return {
        "provider": config.provider,
        "model": config.model,
        "endpoint": config.endpoint,
        "evidence_scope": "Qwen/local model run",
    }


def upstream_commit() -> dict[str, str | None]:
    def git_value(*args: str) -> str | None:
        try:
            completed = subprocess.run(
                ["git", "-C", str(UPSTREAM), *args],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError):
            return None
        return completed.stdout.strip() or None

    return {
        "path": str(UPSTREAM),
        "branch": git_value("branch", "--show-current"),
        "commit": git_value("rev-parse", "HEAD"),
        "remote": git_value("remote", "get-url", "origin"),
    }


def trade_price(trade: Any) -> int | float | None:
    if trade in {None, "NONE"}:
        return None
    for attr in ("resources_from_first_agent", "resources_from_second_agent"):
        resources = getattr(trade, attr, None)
        resource_dict = getattr(resources, "resource_dict", {})
        if "ZUP" in resource_dict:
            return resource_dict["ZUP"]
    return None


def structured_line(state: dict[str, Any], last_offer_price: int | float | None) -> tuple[str, int | float | None]:
    public = state.get("player_public_info_dict", {})
    answer = str(public.get("player answer", "")).strip().upper()
    proposed_trade = public.get("newly proposed trade")
    offered_price = trade_price(proposed_trade)

    if answer == "REJECT":
        return "REJECT:", last_offer_price
    if answer == "ACCEPT":
        price = last_offer_price if last_offer_price is not None else offered_price
        return f"ACCEPT: price={price}" if price is not None else "ACCEPT:", last_offer_price
    if offered_price is not None:
        return f"OFFER: price={offered_price}", offered_price
    return "REJECT:", last_offer_price


BUY_SELL_TAGS = (
    "proposal count",
    "my resources",
    "my goals",
    "reason",
    "player answer",
    "newly proposed trade",
    "other player proposed trade",
    "message",
)


def canonicalize_xml_tags(text: str) -> str:
    normalized = text.strip()
    if normalized.startswith("```"):
        normalized = re.sub(r"^```[a-zA-Z]*\s*", "", normalized)
        normalized = re.sub(r"\s*```$", "", normalized).strip()
    for tag in BUY_SELL_TAGS:
        pattern = re.compile(rf"<\s*(/?)\s*{re.escape(tag)}\s*>", re.IGNORECASE)
        normalized = pattern.sub(lambda match, t=tag: f"</{t}>" if match.group(1) else f"<{t}>", normalized)
    return normalized


def tag_value(text: str, tag: str) -> str | None:
    match = re.search(rf"<{re.escape(tag)}>(.*?)</{re.escape(tag)}>", text, flags=re.DOTALL)
    if not match:
        return None
    return match.group(1).strip()


def replace_or_append_tag(text: str, tag: str, value: str) -> str:
    replacement = f"<{tag}>{value}</{tag}>"
    pattern = re.compile(rf"<{re.escape(tag)}>.*?</{re.escape(tag)}>", flags=re.DOTALL)
    if pattern.search(text):
        return pattern.sub(replacement, text, count=1)
    return f"{text.rstrip()}\n{replacement}"


def normalize_buy_sell_response(text: str) -> str:
    normalized = canonicalize_xml_tags(text)
    lower = normalized.lower()
    answer = (tag_value(normalized, "player answer") or "").strip().upper()

    accepts_prior_offer = "accept this trade" in lower or "i accept" in lower
    rejects_prior_offer = "reject" in lower and "accept" not in lower
    if accepts_prior_offer:
        normalized = replace_or_append_tag(normalized, "player answer", "ACCEPT")
        prior_trade = tag_value(normalized, "other player proposed trade")
        if prior_trade and not tag_value(normalized, "newly proposed trade"):
            normalized = replace_or_append_tag(normalized, "newly proposed trade", prior_trade)
    elif rejects_prior_offer and answer not in {"PROPOSAL", "ACCEPT"}:
        normalized = replace_or_append_tag(normalized, "player answer", "REJECT")
        if not tag_value(normalized, "newly proposed trade"):
            normalized = replace_or_append_tag(normalized, "newly proposed trade", "NONE")

    proposed_trade = tag_value(normalized, "newly proposed trade")
    if proposed_trade:
        clipped = re.split(r"</(?:message|other player proposed trade|player answer)>", proposed_trade, maxsplit=1)[0].strip()
        normalized = replace_or_append_tag(normalized, "newly proposed trade", clipped)
    return normalized


_PROMPT_TRANSLATIONS: dict[str, Any] | None = None


def prompt_translations() -> dict[str, Any]:
    global _PROMPT_TRANSLATIONS
    if _PROMPT_TRANSLATIONS is None:
        _PROMPT_TRANSLATIONS = json.loads((ROOT / "config" / "prompt_translations.json").read_text(encoding="utf-8"))
    return _PROMPT_TRANSLATIONS


def prompt_unit(context: str, unit_id: str) -> dict[str, Any]:
    translations = prompt_translations()
    if context == "global":
        units = translations.get("global_prompt_units", [])
    else:
        games = {game.get("game_id"): game for game in translations.get("games", [])}
        units = games.get(context, {}).get("prompt_units", [])
    for unit in units:
        if unit.get("id") == unit_id:
            return unit
    raise KeyError(f"Missing translation prompt unit: {context}/{unit_id}")


def prompt_text(context: str, unit_id: str, language: str, **values: str) -> str:
    unit = prompt_unit(context, unit_id)
    source_key = "id_translation" if language.upper() == "ID" else "en"
    text = str(unit[source_key])
    return text.format(**values) if values else text


def language_policy_unit(condition: str, language: str) -> str:
    normalized_condition = condition.upper()
    normalized_language = language.upper()
    if normalized_condition == "C3":
        return "language_policy_c3_free_choice"
    if normalized_condition == "C2":
        return "language_policy_c2_forced_mixed"
    if normalized_language == "ID":
        return "language_policy_c1_id"
    return "language_policy_c0_en"


def buy_sell_private_prompt_unit(role_name: str, language: str) -> tuple[str, dict[str, str]]:
    id_language = language.upper() == "ID"
    if role_name == "seller":
        return (
            "buy_sell_seller_private_prompt",
            {
                "seller_cost": "40 ZUP",
                "seller_outside_option": "mempertahankan barang" if id_language else "keeping the item",
            },
        )
    return (
        "buy_sell_buyer_private_prompt",
        {
            "buyer_value": "100 ZUP",
            "buyer_outside_option": "tidak membeli barang" if id_language else "not buying the item",
        },
    )


def language_runtime_instruction(language: str, role_name: str, condition: str) -> str:
    private_unit, private_values = buy_sell_private_prompt_unit(role_name, language)
    parts = [
        prompt_text("global", "system_negotiator", language),
        output_channel_instruction(language, condition),
        prompt_text("buy_sell", "buy_sell_public_rules", language),
        prompt_text("buy_sell", private_unit, language, **private_values),
        prompt_text("buy_sell", "buy_sell_upstream_xml_response_format", language),
    ]
    return "\n\n" + " ".join(parts)


def build_episode(game: Any, plan: dict[str, Any]) -> dict[str, Any]:
    episode = plan["episode"]
    role_by_turn = {0: "seller", 1: "buyer"}
    messages = []
    last_offer_price: int | float | None = None

    for state in game.game_state[1:]:
        if state.get("current_iteration") == "END":
            continue
        role = role_by_turn.get(state.get("turn"), str(state.get("turn")))
        line, last_offer_price = structured_line(state, last_offer_price)
        public = state.get("player_public_info_dict", {})
        player_message = public.get("message", "")
        raw = state.get("player_complete_answer", "")
        messages.append(
            {
                "turn_index": state.get("current_iteration"),
                "role": role,
                "language": episode["role_languages"][role],
                "text": f"{line}\n{player_message}\n\nRAW_UPSTREAM_RESPONSE:\n{raw}".strip(),
                "upstream_public": {key: str(value) for key, value in public.items()},
            }
        )

    summary = {}
    if game.game_state and game.game_state[-1].get("current_iteration") == "END":
        summary = game.game_state[-1].get("summary", {})

    final_response = str(summary.get("final_response", "NONE")).upper()
    deal = final_response == "ACCEPT"
    final_price = trade_price(summary.get("proposed_trade")) if deal else None
    outcomes = summary.get("player_outcome", [None, None])
    payoffs = {"seller": outcomes[0], "buyer": outcomes[1]} if len(outcomes) == 2 else {}

    return {
        "episode_id": episode["episode_id"],
        "condition": episode["condition"],
        "game_id": episode["game_id"],
        "language_pair": episode["language_pair"],
        "role_languages": episode["role_languages"],
        "model": episode["model"],
        "seed": episode["seed"],
        "upstream": upstream_commit(),
        "deal": deal,
        "final_terms": {"price": final_price} if final_price is not None else {},
        "payoffs": payoffs,
        "messages": messages,
    }


def run_episode(plan: dict[str, Any], provider: str, model_metadata: dict[str, Any]) -> dict[str, Any]:
    install_optional_upstream_import_shims()

    from games.buy_sell_game.game import BuySellGame
    from ratbench.agents.agents import Agent
    from ratbench.constants import AGENT_ONE, AGENT_TWO, MONEY_TOKEN
    from ratbench.game_objects.goal import BuyerGoal, SellerGoal
    from ratbench.game_objects.resource import Resources
    from ratbench.game_objects.valuation import Valuation

    class AgentImpl(Agent):
        def __init__(self, agent_name: str, role_name: str, language: str, condition: str, model_label: str) -> None:
            super().__init__(agent_name=agent_name)
            self.role_name = role_name
            self.language = language
            self.condition = condition
            self.model = model_label
            self.prompt_entity_initializer = "system"
            self.client, _metadata = make_chat_client(provider)
            self.conversation: list[dict[str, str]] = []
            self.run_epoch_time_ms = None

        def chat(self) -> str:
            return normalize_buy_sell_response(self.client.complete(self.conversation))

        def update_conversation_tracking(self, entity: str, message: Any) -> None:
            role = entity if entity in {"system", "user", "assistant"} else "user"
            content = str(message)
            if role == "system":
                content += language_runtime_instruction(self.language, self.role_name, self.condition)
            self.conversation.append({"role": role, "content": content})

        def get_state(self) -> dict[str, Any]:
            return {
                "class": self.__class__.__name__,
                "agent_name": self.agent_name,
                "model": self.model,
                "language": self.language,
                "conversation": list(self.conversation),
                "run_epoch_time_ms": self.run_epoch_time_ms,
            }

    episode = plan["episode"]
    role_languages = episode["role_languages"]
    log_dir = ROOT / "artifacts" / "upstream_logs" / episode["episode_id"]
    log_dir.mkdir(parents=True, exist_ok=True)
    seller = AgentImpl(AGENT_ONE, "seller", role_languages["seller"], episode["condition"], episode["model"])
    buyer = AgentImpl(AGENT_TWO, "buyer", role_languages["buyer"], episode["condition"], episode["model"])
    seller_role_prompt = (
        f"You are {AGENT_ONE}. You are the seller."
        if role_languages["seller"].upper() != "ID"
        else f"Anda adalah {AGENT_ONE}. Anda adalah penjual."
    )
    buyer_role_prompt = (
        f"You are {AGENT_TWO}. You are the buyer."
        if role_languages["buyer"].upper() != "ID"
        else f"Anda adalah {AGENT_TWO}. Anda adalah pembeli."
    )
    game = BuySellGame(
        players=[seller, buyer],
        iterations=int(episode["turn_limit"]),
        resources_support_set=Resources({"X": 0}),
        player_goals=[
            SellerGoal(cost_of_production=Valuation({"X": 40})),
            BuyerGoal(willingness_to_pay=Valuation({"X": 100})),
        ],
        player_initial_resources=[
            Resources({"X": 1}),
            Resources({MONEY_TOKEN: 1000}),
        ],
        player_roles=[
            seller_role_prompt,
            buyer_role_prompt,
        ],
        player_social_behaviour=["", ""],
        log_dir=str(log_dir),
    )
    game.run()
    built = build_episode(game, plan)
    built["model"] = model_metadata["model"]
    built["model_plan"] = {
        "planned_default_model": episode["model"],
        "execution_provider": model_metadata["provider"],
        "execution_model": model_metadata["model"],
        "evidence_scope": model_metadata["evidence_scope"],
    }
    return built


def write_metrics(episode: dict[str, Any], metrics_path: str) -> Path:
    messages = episode.get("messages", [])
    parse_results = [parse_offer(episode["game_id"], message.get("text", "")) for message in messages]
    metrics = first_offer_anchoring(episode["game_id"], messages, episode.get("final_terms"))
    metrics["offer_parse_rate"] = offer_parse_rate(parse_results)
    metrics["parsed_actions"] = [result.to_dict() for result in parse_results]
    metrics["payoff_asymmetry"] = episode_payoff_asymmetry(episode["game_id"], episode, messages)
    metrics["channel_compliance"] = channel_compliance(
        messages,
        episode.get("role_languages", {}),
        episode.get("language_pair"),
    )
    metrics["deal_rate"] = 1.0 if episode.get("deal") else 0.0
    metrics["turns_to_deal"] = len(messages) if episode.get("deal") else None
    return write_json(metrics_path, metrics)


def main() -> int:
    plan = load_plan()
    artifacts = plan["expected_artifacts"]
    provider = selected_provider()
    failed_command = "bash scripts/run_smoke.sh"
    try:
        model_metadata = run_endpoint_probe(provider, failed_command=failed_command)
    except SystemExit as exc:
        benchmark_config = load_benchmark_model_config() or {}
        smoke_config = load_smoke_model_config() or {}
        active_config = benchmark_config if provider == "openai_benchmark" else smoke_config
        probe_artifact = (
            "artifacts/results/benchmark_model_probe.json"
            if provider == "openai_benchmark"
            else "artifacts/results/smoke_model_probe.json"
            if provider == "openai_smoke"
            else "artifacts/results/model_endpoint_probe.json"
        )
        artifact = write_json(
            "artifacts/results/smoke_c0_buy_sell_en_001.blocked.json",
            {
                "checked_at": utc_now(),
                "status": "BLOCKED",
                "blocker": "model_provider_unavailable",
                "failed_command": failed_command,
                "condition": plan.get("episode", {}).get("condition"),
                "game_id": plan.get("episode", {}).get("game_id"),
                "language_pair": plan.get("episode", {}).get("language_pair"),
                "role_languages": plan.get("episode", {}).get("role_languages", {}),
                "active_provider": provider,
                "active_model": active_config.get("default_model", plan.get("episode", {}).get("model")),
                "provider_probe_artifact": probe_artifact,
                "message": "C0 smoke is ready but the selected model provider probe failed before any transcript was created.",
                "next_action": f"Fix the selected provider, then rerun {failed_command}.",
                "evidence_scope": "No smoke empirical evidence produced by this attempt; this is a provider blocker artifact only.",
            },
        )
        append_event(
            "smoke",
            "BLOCKED",
            f"C0 smoke blocked on provider {provider}; artifact={artifact.relative_to(ROOT)}; "
            f"failed_command={failed_command}",
        )
        return int(exc.code) if isinstance(exc.code, int) else 2

    try:
        episode = run_episode(plan, provider, model_metadata)
    except Exception as exc:
        artifact = write_json(
            "artifacts/results/smoke_c0_buy_sell_en_001.error.json",
            {
                "checked_at": utc_now(),
                "status": "ERROR",
                "failed_command": "python3 scripts/run_c0_smoke.py",
                "error_type": type(exc).__name__,
                "error": str(exc),
                "traceback": traceback.format_exc(),
                "upstream": upstream_commit(),
            },
        )
        append_event("smoke", "ERROR", f"C0 smoke episode failed; artifact={artifact.relative_to(ROOT)}")
        raise

    transcript_path = write_json(artifacts["transcript"], episode)
    metrics_path = write_metrics(episode, artifacts["metrics"])
    append_event(
        "smoke",
        "OK",
        f"C0 buy_sell smoke completed; transcript={transcript_path.relative_to(ROOT)}; metrics={metrics_path.relative_to(ROOT)}",
    )
    print(json.dumps({"transcript": str(transcript_path), "metrics": str(metrics_path)}, indent=2))
    return 0


if __name__ == "__main__":
    os.chdir(ROOT)
    sys.exit(main())
