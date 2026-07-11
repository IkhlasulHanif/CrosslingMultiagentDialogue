#!/usr/bin/env python3
"""JSONL transcript logging for GovSim benchmark runs."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from local_model_adapter import ModelResponse, strip_think_blocks


SCHEMA_VERSION = "govsim-transcript-v1"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def stable_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class TranscriptContext:
    """Run-level metadata repeated on every transcript event."""

    run_id: str
    condition: str
    language_pair: str = "EN-ID"
    episode_id: str | None = None
    seed: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_record(self) -> dict[str, Any]:
        record: dict[str, Any] = {
            "run_id": self.run_id,
            "condition": self.condition,
            "language_pair": self.language_pair,
        }
        if self.episode_id is not None:
            record["episode_id"] = self.episode_id
        if self.seed is not None:
            record["seed"] = self.seed
        if self.metadata:
            record["metadata"] = self.metadata
        return record


class TranscriptWriter:
    """Append-only JSONL writer for model-visible and hidden transcript fields."""

    def __init__(self, path: Path, context: TranscriptContext) -> None:
        self.path = path
        self.context = context
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def for_run(cls, root: Path, context: TranscriptContext) -> "TranscriptWriter":
        safe_run_id = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in context.run_id)
        return cls(root / "artifacts" / "transcripts" / f"{safe_run_id}.jsonl", context)

    def append_event(self, event: dict[str, Any]) -> dict[str, Any]:
        record = {
            "schema_version": SCHEMA_VERSION,
            "ts": utc_now(),
            **self.context.as_record(),
            **event,
        }
        record["event_hash"] = sha256_text(stable_json({k: v for k, v in record.items() if k != "event_hash"}))
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        return record

    def log_model_response(
        self,
        *,
        round_index: int,
        phase: str,
        agent_id: str,
        role: str,
        response: ModelResponse,
        language: str | None = None,
        prompt_messages: Iterable[dict[str, str]] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.log_text(
            round_index=round_index,
            phase=phase,
            agent_id=agent_id,
            role=role,
            raw_text=response.raw_text,
            visible_text=response.visible_text,
            thinking=response.thinking,
            language=language,
            model=response.model,
            finish_reason=response.finish_reason,
            usage=response.usage,
            prompt_messages=prompt_messages,
            extra=extra,
        )

    def log_text(
        self,
        *,
        round_index: int,
        phase: str,
        agent_id: str,
        role: str,
        raw_text: str,
        visible_text: str | None = None,
        thinking: list[str] | None = None,
        language: str | None = None,
        model: str | None = None,
        finish_reason: str | None = None,
        usage: dict[str, Any] | None = None,
        prompt_messages: Iterable[dict[str, str]] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        stripped_visible, stripped_thinking = strip_think_blocks(raw_text)
        clean_visible = stripped_visible if visible_text is None else strip_think_blocks(visible_text)[0]
        hidden_thinking = thinking if thinking is not None else stripped_thinking

        event: dict[str, Any] = {
            "event_type": "model_message",
            "round_index": round_index,
            "phase": phase,
            "agent_id": agent_id,
            "role": role,
            "visible_text": clean_visible,
            "thinking": hidden_thinking,
            "raw_text_sha256": sha256_text(raw_text),
        }
        if language is not None:
            event["language"] = language
        if model is not None:
            event["model"] = model
        if finish_reason is not None:
            event["finish_reason"] = finish_reason
        if usage:
            event["usage"] = usage
        if prompt_messages is not None:
            event["prompt_messages"] = list(prompt_messages)
        if extra:
            event["extra"] = extra
        return self.append_event(event)


def read_transcript(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows
