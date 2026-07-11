#!/usr/bin/env python3
"""Write setting-local evidence for Qwen/vLLM endpoint reachability."""

from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from local_model_adapter import DEFAULT_BASE_URL, DEFAULT_MODEL


SCHEMA_VERSION = "govsim-qwen-endpoint-probe-v1"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _output_tail(text: str, limit: int = 2000) -> str:
    return text[-limit:]


def _curl_probe(models_url: str, api_key: str | None, timeout_s: float) -> dict[str, Any]:
    command = [
        "curl",
        "-sS",
        "--connect-timeout",
        str(timeout_s),
        "-m",
        str(timeout_s),
        "-o",
        "-",
        "-w",
        "\nHTTP_STATUS:%{http_code}\n",
    ]
    redacted_command = list(command)
    if api_key:
        command.extend(["-H", f"Authorization: Bearer {api_key}"])
        redacted_command.extend(["-H", "Authorization: Bearer <redacted>"])
    command.append(models_url)
    redacted_command.append(models_url)

    try:
        proc = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=max(timeout_s + 1.0, 2.0),
        )
        output = proc.stdout
        return {
            "name": "curl_models",
            "command": redacted_command,
            "returncode": proc.returncode,
            "timed_out": False,
            "output_tail": _output_tail(output),
            "reachable": proc.returncode == 0 and "HTTP_STATUS:000" not in output,
        }
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") + (exc.stderr or "")
        return {
            "name": "curl_models",
            "command": redacted_command,
            "returncode": 124,
            "timed_out": True,
            "output_tail": _output_tail(output),
            "reachable": False,
        }
    except FileNotFoundError as exc:
        return {
            "name": "curl_models",
            "command": redacted_command,
            "returncode": None,
            "timed_out": False,
            "output_tail": "",
            "reachable": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }


def _urllib_probe(models_url: str, api_key: str | None, timeout_s: float) -> dict[str, Any]:
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(models_url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(request, timeout=timeout_s) as response:
            body = response.read().decode("utf-8", errors="replace")
            return {
                "name": "urllib_models",
                "status": "OK",
                "http_status": response.status,
                "output_tail": _output_tail(body),
                "reachable": True,
            }
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return {
            "name": "urllib_models",
            "status": "HTTP_ERROR",
            "http_status": exc.code,
            "output_tail": _output_tail(body),
            "reachable": exc.code in {401, 403},
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
    except Exception as exc:  # noqa: BLE001 - probe artifacts should capture exact local failure.
        return {
            "name": "urllib_models",
            "status": "ERROR",
            "reachable": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }


def probe_endpoint(
    root: Path,
    *,
    base_url: str | None = None,
    model: str | None = None,
    timeout_s: float = 2.0,
    api_key: str | None = None,
    out_dir: Path | None = None,
) -> tuple[dict[str, Any], Path]:
    """Probe `/models` and write a JSON artifact.

    A 401/403 response is treated as endpoint-reachable because it proves a
    server answered, even though the benchmark run may still need credentials.
    """

    root = root.resolve()
    base = (base_url or os.environ.get("GOVSIM_MODEL_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
    model_name = model or os.environ.get("GOVSIM_MODEL_NAME") or DEFAULT_MODEL
    key = api_key if api_key is not None else os.environ.get("GOVSIM_MODEL_API_KEY")
    models_url = f"{base}/models"
    chat_url = f"{base}/chat/completions"
    artifact_dir = out_dir or (root / "artifacts" / "logs")
    artifact_dir.mkdir(parents=True, exist_ok=True)

    checks = [
        _curl_probe(models_url, key, timeout_s),
        _urllib_probe(models_url, key, timeout_s),
    ]
    endpoint_reachable = any(bool(check.get("reachable")) for check in checks)
    blockers: list[str] = []
    if not endpoint_reachable:
        blockers.append(f"no reachable Qwen/vLLM OpenAI-compatible endpoint at {models_url}")

    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "timestamp_utc": utc_now(),
        "empirical_episode_ran": False,
        "model_provider": "local-vllm-compatible",
        "model": model_name,
        "base_url": base,
        "models_url": models_url,
        "chat_url": chat_url,
        "api_key_present": bool(key),
        "checks": checks,
        "endpoint_reachable": endpoint_reachable,
        "blockers": blockers,
        "next_command_once_unblocked": (
            "GOVSIM_MODEL_BASE_URL=http://127.0.0.1:8000/v1 "
            "GOVSIM_MODEL_NAME=Qwen3-1.7B ./scripts/run_qwen_c0_baseline.sh"
        ),
    }

    path = artifact_dir / f"qwen_endpoint_probe_{stamp()}.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result, path
