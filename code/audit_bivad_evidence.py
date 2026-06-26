#!/usr/bin/env python3
"""Audit BiVaD run artifacts for debate quality and evidence gaps.

The script is intentionally API-free. It reads JSON artifacts produced by a
BiVaD-style runner and emits a small evidence package. It does not infer new
model results; absent artifacts are reported as blockers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VALUE_KEYS = (
    "universalism",
    "security",
    "conformity",
    "benevolence",
    "self_direction",
    "tradition",
    "achievement",
    "power",
)

COUNTER_MARKERS = (
    "however",
    "but",
    "although",
    "whereas",
    "nevertheless",
    "still",
    "yet",
    "tetapi",
    "namun",
    "meskipun",
    "walaupun",
    "pero",
    "sin embargo",
    "aunque",
)

ADDRESS_MARKERS = (
    "strongest",
    "main point",
    "your point",
    "other agent",
    "opponent",
    "counterpoint",
    "poin lawan",
    "poin utama",
    "argumen lawan",
    "punto",
    "otro agente",
)

CHANGE_MARKERS = (
    "changed",
    "shifted",
    "softened",
    "unchanged",
    "did not change",
    "no change",
    "berubah",
    "tidak berubah",
    "mantengo",
    "cambi",
)

LANGUAGE_STOPWORDS = {
    "English": {
        "the",
        "and",
        "that",
        "with",
        "should",
        "because",
        "risk",
        "public",
        "view",
        "point",
    },
    "Indonesian": {
        "yang",
        "dan",
        "untuk",
        "dengan",
        "saya",
        "tetap",
        "melihat",
        "menimbang",
        "kebebasan",
        "risiko",
    },
    "Spanish": {
        "que",
        "con",
        "para",
        "sobre",
        "mantengo",
        "otro",
        "agente",
        "riesgo",
        "punto",
        "social",
    },
}


@dataclass(frozen=True)
class ArtifactAudit:
    path: str
    run_id: str
    condition: str
    topic: str
    seed: str | None
    agent_prior_hash: str
    transcript_turns: int
    debate_quality: dict[str, Any]
    language_compliance: dict[str, Any]
    screening: dict[str, Any]
    private_public_divergence: dict[str, Any]
    translated_relay_ready: bool
    notes: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "inputs",
        nargs="*",
        help="JSON files or directories containing BiVaD JSON run artifacts.",
    )
    parser.add_argument(
        "--glob",
        default="*.json",
        help="Glob used when an input is a directory. Default: %(default)s",
    )
    parser.add_argument(
        "--out-dir",
        default="code/bivad-evidence-audit",
        help="Directory for audit JSON and Markdown outputs.",
    )
    parser.add_argument(
        "--min-debate-quality",
        type=float,
        default=0.67,
        help="Minimum per-turn quality score considered adequate.",
    )
    parser.add_argument(
        "--divergence-threshold",
        type=float,
        default=0.5,
        help="Distance threshold for private-public divergence flags.",
    )
    return parser.parse_args()


def discover_json_files(inputs: list[str], glob_pattern: str) -> list[Path]:
    if not inputs:
        inputs = ["runs"]
    files: list[Path] = []
    for item in inputs:
        path = Path(item)
        if path.is_dir():
            files.extend(path.rglob(glob_pattern))
        elif path.is_file() and path.suffix.lower() == ".json":
            files.append(path)
    return sorted({path.resolve() for path in files})


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def normalize_language(name: str | None) -> str | None:
    if not name:
        return None
    lowered = name.strip().lower()
    aliases = {
        "en": "English",
        "eng": "English",
        "english": "English",
        "id": "Indonesian",
        "indonesian": "Indonesian",
        "bahasa indonesia": "Indonesian",
        "es": "Spanish",
        "spanish": "Spanish",
        "espanol": "Spanish",
        "español": "Spanish",
    }
    return aliases.get(lowered, name.strip())


def words(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-zÀ-ÿ']+", text.lower()))


def marker_present(text: str, markers: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in markers)


def stated_change_value(turn: dict[str, Any]) -> str:
    value = str(turn.get("stated_change", "")).strip().lower()
    if value:
        return value
    text = str(turn.get("text", ""))
    if marker_present(text, CHANGE_MARKERS):
        return "mentioned"
    return "missing"


def score_debate_quality(transcript: list[dict[str, Any]], min_quality: float) -> dict[str, Any]:
    turn_scores: list[dict[str, Any]] = []
    previous_by_speaker: dict[str, dict[str, Any]] = {}
    for index, turn in enumerate(transcript):
        text = str(turn.get("text", ""))
        speaker = str(turn.get("speaker", ""))
        has_opponent_context = any(item.get("speaker") != speaker for item in transcript[:index])
        addressed = bool(turn.get("addressed_counterpoint"))
        addressed = addressed or (has_opponent_context and marker_present(text, ADDRESS_MARKERS))
        counterarg = marker_present(text, COUNTER_MARKERS)
        if has_opponent_context and len(words(text)) >= 20:
            counterarg = counterarg or bool(previous_by_speaker)
        change_value = stated_change_value(turn)
        stated_change = change_value != "missing"
        denominator = 3 if has_opponent_context else 1
        numerator = int(stated_change)
        if has_opponent_context:
            numerator += int(addressed) + int(counterarg)
        score = numerator / denominator
        turn_scores.append(
            {
                "turn": turn.get("turn", index + 1),
                "speaker": speaker,
                "has_opponent_context": has_opponent_context,
                "addresses_opponent_point": addressed,
                "gives_counterargument": counterarg,
                "states_change_or_nonchange": stated_change,
                "stated_change": change_value,
                "score": round(score, 3),
                "adequate": score >= min_quality,
            }
        )
        previous_by_speaker[speaker] = turn

    scored_after_first = [item for item in turn_scores if item["has_opponent_context"]]
    adequate = [item for item in scored_after_first if item["adequate"]]
    rate = len(adequate) / len(scored_after_first) if scored_after_first else None
    return {
        "turn_count": len(transcript),
        "audited_response_turns": len(scored_after_first),
        "adequate_turns": len(adequate),
        "adequate_rate": None if rate is None else round(rate, 3),
        "turn_scores": turn_scores,
        "needs_human_review": [
            item for item in turn_scores if item["has_opponent_context"] and not item["adequate"]
        ],
    }


def infer_language(text: str) -> dict[str, float]:
    token_set = words(text)
    if not token_set:
        return {}
    scores: dict[str, float] = {}
    for language, stopwords in LANGUAGE_STOPWORDS.items():
        scores[language] = len(token_set & stopwords) / max(1, len(stopwords))
    return scores


def compliance_audit(data: dict[str, Any]) -> dict[str, Any]:
    agents = data.get("agents") or []
    required: dict[str, str] = {}
    for agent in agents:
        if isinstance(agent, dict):
            agent_id = str(agent.get("agent_id", ""))
            language = normalize_language(str(agent.get("language", "")))
            if agent_id and language:
                required[agent_id] = language

    turns = data.get("transcript") or []
    per_turn = []
    copied_language_events = []
    for index, turn in enumerate(turns):
        speaker = str(turn.get("speaker", ""))
        declared = normalize_language(str(turn.get("language", "")))
        expected = required.get(speaker)
        text = str(turn.get("text", ""))
        inferred_scores = infer_language(text)
        inferred = max(inferred_scores, key=inferred_scores.get) if inferred_scores else None
        wrong_declared = bool(expected and declared and declared != expected)
        wrong_inferred = bool(expected and inferred and inferred != expected and inferred_scores[inferred] > 0.2)
        prior_opponent = next(
            (
                prev
                for prev in reversed(turns[:index])
                if isinstance(prev, dict) and str(prev.get("speaker", "")) != speaker
            ),
            None,
        )
        copied = False
        if prior_opponent:
            opponent_language = normalize_language(str(prior_opponent.get("language", "")))
            copied = bool(expected and opponent_language and declared == opponent_language != expected)
        if copied:
            copied_language_events.append({"turn": turn.get("turn", index + 1), "speaker": speaker})
        per_turn.append(
            {
                "turn": turn.get("turn", index + 1),
                "speaker": speaker,
                "expected_language": expected,
                "declared_language": declared,
                "inferred_language": inferred,
                "declared_compliant": not wrong_declared,
                "inferred_warning": wrong_inferred,
                "copied_opponent_language": copied,
            }
        )

    declared_ok = [item for item in per_turn if item["declared_compliant"]]
    inferred_warn = [item for item in per_turn if item["inferred_warning"]]
    return {
        "turn_count": len(per_turn),
        "declared_compliance_rate": round(len(declared_ok) / len(per_turn), 3) if per_turn else None,
        "inferred_warning_rate": round(len(inferred_warn) / len(per_turn), 3) if per_turn else None,
        "copied_opponent_language_events": copied_language_events,
        "per_turn": per_turn,
        "language_id_note": "Heuristic only; use a real language ID model for publication-grade rates.",
    }


def vector_distance(a: dict[str, Any], b: dict[str, Any]) -> float | None:
    dims = [key for key in VALUE_KEYS if key in a and key in b]
    if not dims:
        dims = [key for key in a if key in b and isinstance(a[key], (int, float)) and isinstance(b[key], (int, float))]
    if not dims:
        return None
    return round(math.sqrt(sum((float(a[key]) - float(b[key])) ** 2 for key in dims)), 6)


def readouts_by_agent_turn(items: list[dict[str, Any]]) -> dict[tuple[str, int], dict[str, Any]]:
    result: dict[tuple[str, int], dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        agent = str(item.get("agent_id", ""))
        try:
            turn = int(item.get("turn", 0))
        except (TypeError, ValueError):
            continue
        values = item.get("values")
        if agent and isinstance(values, dict):
            result[(agent, turn)] = values
    return result


def divergence_audit(data: dict[str, Any], threshold: float) -> dict[str, Any]:
    private = readouts_by_agent_turn(data.get("private_probes") or [])
    observed = readouts_by_agent_turn(data.get("observer_readouts") or [])
    keys = sorted(set(private) & set(observed), key=lambda item: (item[1], item[0]))
    gaps = []
    for agent, turn in keys:
        distance = vector_distance(private[(agent, turn)], observed[(agent, turn)])
        if distance is None:
            continue
        gaps.append(
            {
                "agent_id": agent,
                "turn": turn,
                "private_public_distance": distance,
                "flagged": distance >= threshold,
            }
        )
    flagged = [item for item in gaps if item["flagged"]]
    by_agent: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in gaps:
        by_agent[item["agent_id"]].append(item)
    public_shift_private_stable = []
    private_shift_public_stable = []
    for agent, agent_gaps in by_agent.items():
        ordered = sorted(agent_gaps, key=lambda item: item["turn"])
        if len(ordered) < 2:
            continue
        start_key = (agent, ordered[0]["turn"])
        end_key = (agent, ordered[-1]["turn"])
        private_shift = vector_distance(private[start_key], private[end_key])
        public_shift = vector_distance(observed[start_key], observed[end_key])
        if private_shift is None or public_shift is None:
            continue
        event = {
            "agent_id": agent,
            "start_turn": ordered[0]["turn"],
            "end_turn": ordered[-1]["turn"],
            "private_shift": private_shift,
            "public_shift": public_shift,
        }
        if public_shift >= threshold and private_shift < threshold:
            public_shift_private_stable.append(event)
        if private_shift >= threshold and public_shift < threshold:
            private_shift_public_stable.append(event)
    return {
        "matched_readouts": len(gaps),
        "flagged_private_public_gaps": flagged,
        "public_shift_private_stable": public_shift_private_stable,
        "private_shift_public_stable": private_shift_public_stable,
    }


def prior_hash(data: dict[str, Any]) -> str:
    agents = data.get("agents") or []
    normalized = []
    for agent in agents:
        if isinstance(agent, dict):
            normalized.append(
                {
                    "agent_id": agent.get("agent_id"),
                    "stance": agent.get("stance"),
                    "values": agent.get("values"),
                }
            )
    payload = json.dumps(normalized, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def audit_artifact(path: Path, data: dict[str, Any], args: argparse.Namespace) -> ArtifactAudit:
    transcript = data.get("transcript") or []
    if not isinstance(transcript, list):
        transcript = []
    notes: list[str] = []
    if not transcript and data.get("condition") != "no-dialogue":
        notes.append("No transcript turns found.")
    screening = data.get("screening") if isinstance(data.get("screening"), dict) else {}
    if screening and not screening.get("retained", False):
        notes.append("Screening rejected this candidate; keep as low-disagreement control only.")
    if not data.get("private_probes"):
        notes.append("No private probe readouts found.")
    if not data.get("observer_readouts"):
        notes.append("No observer readouts found.")
    return ArtifactAudit(
        path=str(path),
        run_id=str(data.get("run_id") or path.stem),
        condition=str(data.get("condition") or "unknown"),
        topic=str(data.get("topic") or "unknown"),
        seed=None if data.get("seed") is None else str(data.get("seed")),
        agent_prior_hash=prior_hash(data),
        transcript_turns=len(transcript),
        debate_quality=score_debate_quality(transcript, args.min_debate_quality),
        language_compliance=compliance_audit(data),
        screening=screening,
        private_public_divergence=divergence_audit(data, args.divergence_threshold),
        translated_relay_ready=str(data.get("condition") or "").lower() == "translated-relay",
        notes=notes,
    )


def paired_condition_audit(audits: list[ArtifactAudit]) -> dict[str, Any]:
    groups: dict[tuple[str, str | None, str], list[ArtifactAudit]] = defaultdict(list)
    for audit in audits:
        groups[(audit.topic, audit.seed, audit.agent_prior_hash)].append(audit)

    required = {
        "mixed-language",
        "same-English",
        "same-target-language",
        "swapped-language",
        "translated-relay",
    }
    comparisons = []
    incomplete = []
    for (topic, seed, agent_hash), items in sorted(groups.items()):
        conditions = {item.condition for item in items}
        entry = {
            "topic": topic,
            "seed": seed,
            "agent_prior_hash": agent_hash,
            "conditions_present": sorted(conditions),
            "conditions_missing": sorted(required - conditions),
            "ready_for_cross_lingual_outcome_comparison": required.issubset(conditions),
        }
        if entry["ready_for_cross_lingual_outcome_comparison"]:
            comparisons.append(entry)
        else:
            incomplete.append(entry)
    return {
        "complete_paired_sets": comparisons,
        "incomplete_paired_sets": incomplete,
    }


def summarize(audits: list[ArtifactAudit], files_seen: list[Path]) -> dict[str, Any]:
    conditions = defaultdict(int)
    topics = defaultdict(int)
    retained = 0
    rejected = 0
    no_screen = 0
    for audit in audits:
        conditions[audit.condition] += 1
        topics[audit.topic] += 1
        if not audit.screening:
            no_screen += 1
        elif audit.screening.get("retained"):
            retained += 1
        else:
            rejected += 1
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "artifact_files_seen": [str(path) for path in files_seen],
        "artifact_count": len(audits),
        "conditions": dict(sorted(conditions.items())),
        "topics": dict(sorted(topics.items())),
        "screening": {
            "retained": retained,
            "rejected": rejected,
            "missing_screening_record": no_screen,
        },
        "executed_results_present": bool(audits),
        "synthetic_placeholder_warning": (
            "This audit reports only supplied artifacts. It does not convert synthetic or "
            "offline smoke artifacts into empirical findings."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# BiVaD Evidence Audit",
        "",
        f"Created at: `{summary['created_at']}`",
        "",
        "## Status",
        "",
    ]
    if not summary["artifact_count"]:
        lines.extend(
            [
                "No JSON run artifacts were found in the requested inputs.",
                "",
                "Smallest next action: run model-backed or deterministic trial artifacts through "
                "`python3 code/audit_bivad_evidence.py <artifact-dir>`.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                f"Audited `{summary['artifact_count']}` JSON artifact(s).",
                "",
                f"Conditions: `{json.dumps(summary['conditions'], sort_keys=True)}`",
                "",
                f"Screening: `{json.dumps(summary['screening'], sort_keys=True)}`",
                "",
            ]
        )

    paired = report["paired_condition_audit"]
    lines.extend(
        [
            "## Paired Conditions",
            "",
            f"Complete paired sets: `{len(paired['complete_paired_sets'])}`",
            "",
            f"Incomplete paired sets: `{len(paired['incomplete_paired_sets'])}`",
            "",
        ]
    )

    lines.extend(["## Artifact Findings", ""])
    if not report["artifacts"]:
        lines.append("No artifact-level findings.")
        lines.append("")
    for artifact in report["artifacts"]:
        dq = artifact["debate_quality"]
        compliance = artifact["language_compliance"]
        div = artifact["private_public_divergence"]
        lines.extend(
            [
                f"### `{artifact['run_id']}`",
                "",
                f"- Path: `{artifact['path']}`",
                f"- Condition: `{artifact['condition']}`",
                f"- Topic: `{artifact['topic']}`",
                f"- Debate quality adequate rate: `{dq['adequate_rate']}` over `{dq['audited_response_turns']}` response turn(s)",
                f"- Declared language compliance rate: `{compliance['declared_compliance_rate']}`",
                f"- Flagged private-public gaps: `{len(div['flagged_private_public_gaps'])}`",
                f"- Notes: `{'; '.join(artifact['notes']) if artifact['notes'] else 'none'}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Reporting Guardrail",
            "",
            summary["synthetic_placeholder_warning"],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    files = [
        path
        for path in discover_json_files(args.inputs, args.glob)
        if not path.is_relative_to(out_dir)
    ]
    audits: list[ArtifactAudit] = []
    for path in files:
        data = load_json(path)
        if data is None:
            continue
        audits.append(audit_artifact(path, data, args))

    report = {
        "summary": summarize(audits, files),
        "artifacts": [audit.__dict__ for audit in audits],
        "paired_condition_audit": paired_condition_audit(audits),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "audit.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "audit.md").write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {out_dir / 'audit.json'}")
    print(f"Wrote {out_dir / 'audit.md'}")
    if not audits:
        print("No artifacts audited; evidence package records the blocker.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
