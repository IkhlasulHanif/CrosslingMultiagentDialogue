#!/usr/bin/env python3
"""Token-probability language steering from FLORES-style parallel sentence pairs.

This module deliberately avoids prompt-level language instructions. It builds a
token bias vector from English->target parallel text, then applies that vector
as a Hugging Face `LogitsProcessor` during generation. The prompt can describe
content, but language pressure comes from generation-time probability steering.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import torch


DEFAULT_TARGETS = ("ind_Latn", "spa_Latn")
DEFAULT_PROMPTS = (
    "Public release of dual-use policy datasets should balance civic access and misuse risk.",
    "Open models can improve accountability, but deployment should account for downstream harm.",
)


@dataclass(frozen=True)
class ParallelCorpus:
    source_lang: str
    target_lang: str
    source_sentences: list[str]
    target_sentences: list[str]


class TokenBiasLogitsProcessor:
    """Add a fixed bias vector to logits at every generation step."""

    def __init__(self, bias: torch.Tensor) -> None:
        self.bias = bias

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> torch.FloatTensor:
        return scores + self.bias.to(scores.device, dtype=scores.dtype)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-id", required=True, help="Hugging Face model id or local model path.")
    parser.add_argument(
        "--flores-dir",
        required=True,
        help="Directory containing FLORES-200 sentence files, e.g. dev.eng_Latn and dev.ind_Latn.",
    )
    parser.add_argument("--source-lang", default="eng_Latn")
    parser.add_argument("--target-lang", action="append", default=[], help="Target FLORES language code. Repeatable.")
    parser.add_argument("--split", default="dev", help="FLORES split prefix to load, usually dev or devtest.")
    parser.add_argument("--max-pairs", type=int, default=512)
    parser.add_argument("--prompt", action="append", default=[], help="Content prompt. Do not include language instructions.")
    parser.add_argument("--out", default="runs/language-steering/steering_probe.json")
    parser.add_argument("--max-new-tokens", type=int, default=96)
    parser.add_argument("--bias-scale", type=float, default=3.0)
    parser.add_argument("--min-token-count", type=int, default=2)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top-p", type=float, default=0.9)
    parser.add_argument("--allow-download", action="store_true")
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    return parser.parse_args()


def choose_device(requested: str) -> torch.device:
    if requested == "cuda":
        if not torch.cuda.is_available():
            raise SystemExit("--device cuda requested but torch.cuda.is_available() is false")
        return torch.device("cuda")
    if requested == "cpu":
        return torch.device("cpu")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def candidate_flores_paths(root: Path, split: str, lang: str) -> list[Path]:
    return [
        root / f"{split}.{lang}",
        root / f"{split}.{lang}.txt",
        root / split / f"{lang}.txt",
        root / split / lang,
    ]


def read_flores_file(root: Path, split: str, lang: str) -> list[str]:
    for path in candidate_flores_paths(root, split, lang):
        if path.exists():
            return [
                line.strip()
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
    candidates = ", ".join(str(path) for path in candidate_flores_paths(root, split, lang))
    raise FileNotFoundError(f"missing FLORES file for {lang}; tried {candidates}")


def load_parallel_corpus(
    flores_dir: Path,
    split: str,
    source_lang: str,
    target_lang: str,
    max_pairs: int,
) -> ParallelCorpus:
    source = read_flores_file(flores_dir, split, source_lang)
    target = read_flores_file(flores_dir, split, target_lang)
    pair_count = min(len(source), len(target), max_pairs)
    if pair_count == 0:
        raise ValueError(f"no aligned sentence pairs for {source_lang}->{target_lang}")
    return ParallelCorpus(
        source_lang=source_lang,
        target_lang=target_lang,
        source_sentences=source[:pair_count],
        target_sentences=target[:pair_count],
    )


def token_counts(tokenizer: Any, sentences: Iterable[str]) -> Counter[int]:
    counts: Counter[int] = Counter()
    for sentence in sentences:
        ids = tokenizer(sentence, add_special_tokens=False).input_ids
        counts.update(int(token_id) for token_id in ids)
    return counts


def build_token_bias(
    tokenizer: Any,
    corpus: ParallelCorpus,
    vocab_size: int,
    *,
    bias_scale: float,
    min_token_count: int,
    device: torch.device,
) -> tuple[torch.Tensor, dict[str, Any]]:
    source_counts = token_counts(tokenizer, corpus.source_sentences)
    target_counts = token_counts(tokenizer, corpus.target_sentences)
    source_total = sum(source_counts.values()) + vocab_size
    target_total = sum(target_counts.values()) + vocab_size
    bias = torch.zeros(vocab_size, dtype=torch.float32, device=device)
    selected: list[dict[str, Any]] = []

    for token_id, target_count in target_counts.items():
        if target_count < min_token_count:
            continue
        source_count = source_counts.get(token_id, 0)
        target_logp = math.log((target_count + 1) / target_total)
        source_logp = math.log((source_count + 1) / source_total)
        delta = target_logp - source_logp
        if delta <= 0:
            continue
        value = min(delta, bias_scale)
        bias[token_id] = value
        if len(selected) < 40:
            selected.append(
                {
                    "token_id": token_id,
                    "token": tokenizer.decode([token_id]),
                    "target_count": target_count,
                    "source_count": source_count,
                    "bias": round(float(value), 6),
                }
            )

    for token_id, source_count in source_counts.items():
        if source_count < min_token_count or token_id in target_counts:
            continue
        source_logp = math.log((source_count + 1) / source_total)
        target_logp = math.log(1 / target_total)
        delta = source_logp - target_logp
        if delta > 0:
            bias[token_id] = -min(delta, bias_scale) * 0.5

    metadata = {
        "source_lang": corpus.source_lang,
        "target_lang": corpus.target_lang,
        "pair_count": len(corpus.source_sentences),
        "positive_token_biases": int((bias > 0).sum().item()),
        "negative_token_biases": int((bias < 0).sum().item()),
        "sample_positive_biases": selected,
    }
    return bias, metadata


def language_heuristic(text: str, target_lang: str) -> dict[str, Any]:
    lowered = text.lower()
    stopwords = {
        "ind_Latn": ("yang", "dan", "untuk", "dengan", "saya", "tidak", "risiko", "publik"),
        "spa_Latn": ("que", "para", "con", "una", "los", "las", "riesgo", "publico", "público"),
        "eng_Latn": ("the", "and", "with", "that", "risk", "public", "should"),
    }
    hits = [word for word in stopwords.get(target_lang, ()) if re.search(rf"\b{re.escape(word)}\b", lowered)]
    return {
        "target_lang": target_lang,
        "stopword_hits": hits,
        "stopword_hit_count": len(hits),
        "non_ascii_ratio": round(sum(ord(ch) > 127 for ch in text) / max(len(text), 1), 4),
    }


def generate(
    tokenizer: Any,
    model: Any,
    prompt: str,
    device: torch.device,
    args: argparse.Namespace,
    bias: torch.Tensor | None = None,
) -> str:
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {key: value.to(device) for key, value in inputs.items()}
    processors = None
    if bias is not None:
        from transformers import LogitsProcessorList

        processors = LogitsProcessorList([TokenBiasLogitsProcessor(bias)])
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            do_sample=args.temperature > 0,
            temperature=args.temperature if args.temperature > 0 else None,
            top_p=args.top_p if args.temperature > 0 else None,
            logits_processor=processors,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    generated = output[0][inputs["input_ids"].shape[-1] :]
    return tokenizer.decode(generated, skip_special_tokens=True).strip()


def main() -> int:
    args = parse_args()
    targets = args.target_lang or list(DEFAULT_TARGETS)
    prompts = args.prompt or list(DEFAULT_PROMPTS)
    device = choose_device(args.device)

    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(args.model_id, local_files_only=not args.allow_download)
    model = AutoModelForCausalLM.from_pretrained(args.model_id, local_files_only=not args.allow_download)
    model.to(device)
    model.eval()
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    vocab_size = int(getattr(model.config, "vocab_size", len(tokenizer)))
    rows = []
    bias_metadata = []
    for target in targets:
        corpus = load_parallel_corpus(Path(args.flores_dir), args.split, args.source_lang, target, args.max_pairs)
        bias, metadata = build_token_bias(
            tokenizer,
            corpus,
            vocab_size,
            bias_scale=args.bias_scale,
            min_token_count=args.min_token_count,
            device=device,
        )
        bias_metadata.append(metadata)
        for prompt in prompts:
            baseline = generate(tokenizer, model, prompt, device, args, bias=None)
            steered = generate(tokenizer, model, prompt, device, args, bias=bias)
            rows.append(
                {
                    "target_lang": target,
                    "prompt": prompt,
                    "baseline": baseline,
                    "steered": steered,
                    "baseline_language_heuristic": language_heuristic(baseline, target),
                    "steered_language_heuristic": language_heuristic(steered, target),
                }
            )

    report = {
        "artifact_type": "language_probability_steering_probe",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model": args.model_id,
        "device": str(device),
        "source_lang": args.source_lang,
        "targets": targets,
        "split": args.split,
        "max_pairs": args.max_pairs,
        "method": (
            "FLORES parallel sentences define target-vs-English token log-frequency deltas; "
            "deltas are applied as generation-time logit biases without language instructions in prompts."
        ),
        "bias_metadata": bias_metadata,
        "generations": rows,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
