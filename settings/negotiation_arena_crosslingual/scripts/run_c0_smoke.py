#!/usr/bin/env python3
"""Run the first real C0 EN buy/sell smoke episode when gates are satisfied."""

from __future__ import annotations

import json
import os
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


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "external" / "NegotiationArena"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(UPSTREAM))

from local_model_adapter import LocalModelError, LocalQwenChat, load_adapter_config  # noqa: E402
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


def smoke_openai_allowed(config: dict[str, Any] | None) -> bool:
    if not config:
        return False
    policy = config.get("policy", {})
    return (
        config.get("provider") == "openai"
        and bool(policy.get("benchmark_smoke_may_use_openai_key"))
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


class OpenAISmokeError(RuntimeError):
    """Raised when the explicitly allowed OpenAI smoke client cannot respond."""


class OpenAISmokeChat:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.model = os.environ.get(
            str(config.get("env_model", "OPENAI_SMOKE_MODEL")),
            str(config.get("default_model", "gpt-4.1-mini")),
        )
        self.base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.endpoint = f"{self.base_url}/chat/completions"
        self.api_key, self.api_key_source = read_api_key(config)
        if not self.api_key:
            raise OpenAISmokeError(
                "OpenAI smoke override is configured, but no API key was found in "
                "OPENAI_API_KEY or configured api_key_file_candidates."
            )

    def complete(self, messages: list[dict[str, str]], **overrides: Any) -> str:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0,
            "max_tokens": 400,
        }
        payload.update({key: value for key, value in overrides.items() if value is not None})
        return self._complete_with_urllib(payload)

    def _extract_content(self, body: str) -> str:
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as exc:
            raise OpenAISmokeError("OpenAI smoke endpoint returned non-JSON response") from exc
        choices = parsed.get("choices")
        if not isinstance(choices, list) or not choices:
            raise OpenAISmokeError("OpenAI smoke endpoint response has no choices")
        message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise OpenAISmokeError("OpenAI smoke endpoint response content is empty")
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
            raise OpenAISmokeError(f"OpenAI smoke request failed: HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            if self._should_try_curl(exc):
                return self._complete_with_curl(payload, f"urllib failed: {exc}")
            raise OpenAISmokeError(f"OpenAI smoke request failed: {exc}") from exc

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
            raise OpenAISmokeError(f"OpenAI smoke request failed: {previous_error}; curl fallback unavailable")

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
            detail = completed.stderr.strip() or completed.stdout.strip()
            raise OpenAISmokeError(
                "OpenAI smoke request failed: "
                f"{previous_error}; curl fallback exit {completed.returncode}: {detail[:500]}"
            )
        return self._extract_content(completed.stdout)


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
    smoke_config = load_smoke_model_config()
    return "openai_smoke" if smoke_openai_allowed(smoke_config) else "local_qwen"


def make_chat_client(provider: str) -> tuple[Any, dict[str, Any]]:
    if provider == "openai_smoke":
        config = load_smoke_model_config()
        if not smoke_openai_allowed(config):
            raise OpenAISmokeError("OpenAI smoke provider was requested but is not allowed by config/smoke_model.json")
        client = OpenAISmokeChat(config or {})
        return client, {
            "provider": "openai_smoke",
            "model": client.model,
            "endpoint": client.endpoint,
            "api_key_source": client.api_key_source,
            "evidence_scope": "runner bring-up only; not Qwen3-1.7B research-matrix evidence",
        }

    config = load_adapter_config()
    return LocalQwenChat(config), {
        "provider": config.provider,
        "model": config.model,
        "endpoint": config.endpoint,
        "evidence_scope": "Qwen/local model smoke",
    }


def run_endpoint_probe(provider: str) -> dict[str, Any]:
    if provider == "openai_smoke":
        try:
            client, metadata = make_chat_client(provider)
        except OpenAISmokeError as exc:
            probe = {
                "checked_at": utc_now(),
                "status": "BLOCKED",
                "provider": "openai_smoke",
                "failed_command": "NEGOTIATION_SMOKE_PROVIDER=openai_smoke python3 scripts/run_c0_smoke.py",
                "error": str(exc),
                "message": "OpenAI smoke override is configured but not usable.",
                "next_action": "Provide an OpenAI API key via config/smoke_model.json candidates or OPENAI_API_KEY, then rerun ./harness.sh run-smoke.",
            }
            artifact = write_json("artifacts/results/smoke_model_probe.json", probe)
            append_event("smoke_model", "BLOCKED", f"OpenAI smoke model probe failed; artifact={artifact.relative_to(ROOT)}")
            raise SystemExit(2) from exc

        probe = {
            "checked_at": utc_now(),
            "status": "OK",
            **metadata,
            "failed_command": None,
            "message": "OpenAI smoke endpoint responded to a tiny chat-completions probe.",
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
        except OpenAISmokeError as exc:
            probe.update(
                {
                    "status": "BLOCKED",
                    "failed_command": "NEGOTIATION_SMOKE_PROVIDER=openai_smoke python3 scripts/run_c0_smoke.py",
                    "error": str(exc),
                    "message": "OpenAI smoke endpoint is not reachable from this session.",
                    "next_action": "Fix network/API-key access for the configured OpenAI smoke model, then rerun ./harness.sh run-smoke.",
                }
            )
            artifact = write_json("artifacts/results/smoke_model_probe.json", probe)
            append_event("smoke_model", "BLOCKED", f"OpenAI smoke model probe failed; artifact={artifact.relative_to(ROOT)}")
            raise SystemExit(2) from exc

        probe["response_preview"] = text[:200]
        artifact = write_json("artifacts/results/smoke_model_probe.json", probe)
        append_event("smoke_model", "OK", f"OpenAI smoke model probe passed; artifact={artifact.relative_to(ROOT)}")
        return metadata

    config = load_adapter_config()
    probe = {
        "checked_at": utc_now(),
        "status": "OK",
        "provider": config.provider,
        "model": config.model,
        "endpoint": config.endpoint,
        "failed_command": None,
        "message": "Local model endpoint responded to a tiny chat-completions probe.",
    }
    try:
        text = LocalQwenChat(config).complete(
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
                "message": "Local Qwen/vLLM endpoint is not reachable.",
                "next_action": (
                    "Start a local OpenAI-compatible Qwen3-1.7B chat-completions "
                    "server at the configured endpoint, or set LOCAL_QWEN_BASE_URL "
                    "and rerun the failed command: ./harness.sh run-smoke for smoke "
                    "or bash scripts/run_c0_baseline.sh for the C0 baseline."
                ),
            }
        )
        artifact = write_json("artifacts/results/model_endpoint_probe.json", probe)
        append_event(
            "model_endpoint",
            "BLOCKED",
            f"Local Qwen endpoint probe failed; artifact={artifact.relative_to(ROOT)}; "
            "failed_command=python3 scripts/local_model_adapter.py --live-probe",
        )
        raise SystemExit(2) from exc

    probe["response_preview"] = text[:200]
    artifact = write_json("artifacts/results/model_endpoint_probe.json", probe)
    append_event("model_endpoint", "OK", f"Local Qwen endpoint probe passed; artifact={artifact.relative_to(ROOT)}")
    return {
        "provider": config.provider,
        "model": config.model,
        "endpoint": config.endpoint,
        "evidence_scope": "Qwen/local model smoke",
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
        def __init__(self, agent_name: str, language: str, model_label: str) -> None:
            super().__init__(agent_name=agent_name)
            self.language = language
            self.model = model_label
            self.prompt_entity_initializer = "system"
            self.client, _metadata = make_chat_client(provider)
            self.conversation: list[dict[str, str]] = []
            self.run_epoch_time_ms = None

        def chat(self) -> str:
            return self.client.complete(self.conversation)

        def update_conversation_tracking(self, entity: str, message: Any) -> None:
            role = entity if entity in {"system", "user", "assistant"} else "user"
            content = str(message)
            if role == "system":
                content += (
                    "\n\nYou must negotiate only in English. Follow the XML tag format exactly. "
                    "When proposing a trade, include one item X and a ZUP price as an integer."
                )
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
    log_dir = ROOT / "artifacts" / "upstream_logs" / episode["episode_id"]
    log_dir.mkdir(parents=True, exist_ok=True)
    seller = AgentImpl(AGENT_ONE, "EN", episode["model"])
    buyer = AgentImpl(AGENT_TWO, "EN", episode["model"])
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
            f"You are {AGENT_ONE}. You are the seller.",
            f"You are {AGENT_TWO}. You are the buyer.",
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
    metrics["deal_rate"] = 1.0 if episode.get("deal") else 0.0
    metrics["turns_to_deal"] = len(messages) if episode.get("deal") else None
    return write_json(metrics_path, metrics)


def main() -> int:
    plan = load_plan()
    artifacts = plan["expected_artifacts"]
    provider = selected_provider()
    model_metadata = run_endpoint_probe(provider)

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
