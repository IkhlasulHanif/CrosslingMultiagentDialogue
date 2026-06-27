#!/usr/bin/env python3
"""Activation-level language steering from language-level FLORES-200 centroids.

Computes a steering vector from separate monolingual sentence pools:
mean(target_hidden_states) - mean(source_hidden_states) at a specified transformer
layer, normalized to unit norm. The vector is injected as alpha * steering_vector
into the residual stream during generation via a forward hook registered on the
selected layer(s).

This avoids prompt-level language instructions and operates directly on internal
representations. The intended retry path is base, non-instruction-tuned models
with FLORES devtest language-level centroids and English as the anchor.
"""

from __future__ import annotations

import argparse
import json
import re
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

import torch


DEFAULT_TARGETS = ("ind_Latn", "spa_Latn")
DEFAULT_PROMPTS = (
    "Public release of dual-use policy datasets should balance civic access and misuse risk.",
    "Open models can improve accountability, but deployment should account for downstream harm.",
)


def read_flores_file(root: Path, split: str, lang: str) -> list[str]:
    candidates = [
        root / f"{split}.{lang}",
        root / f"{split}.{lang}.txt",
        root / split / f"{lang}.txt",
        root / split / lang,
    ]
    for path in candidates:
        if path.exists():
            return [
                line.strip()
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
    raise FileNotFoundError(f"Missing FLORES file for {lang}; tried {[str(c) for c in candidates]}")


def _sentence_hidden_state(
    model: Any,
    tokenizer: Any,
    sentence: str,
    layer_idx: int,
    device: torch.device,
) -> torch.Tensor:
    """Return mean-pooled hidden state of a sentence at layer_idx."""
    inputs = tokenizer(
        sentence,
        return_tensors="pt",
        truncation=True,
        max_length=128,
        padding=False,
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs, output_hidden_states=True)
    # hidden_states[0] = embedding output; hidden_states[i+1] = output of layer i
    hidden = outputs.hidden_states[layer_idx + 1]  # (1, seq_len, hidden_size)
    # Mean over token positions (attention mask not needed since we don't pad)
    return hidden[0].mean(dim=0).float().cpu()


def compute_steering_vector(
    model: Any,
    tokenizer: Any,
    source_sentences: list[str],
    target_sentences: list[str],
    layer_idx: int,
    device: torch.device,
    max_sentences: int = 0,
    mode: str = "pairs",
) -> tuple[torch.Tensor, dict[str, Any]]:
    """Return (unit-norm steering vector, metadata).

    mode='pairs': treat source/target as parallel pairs; truncate both to max_sentences;
        direction = mean(tgt_hidden_i - src_hidden_i) over pairs.
    mode='centroids': treat each language pool independently (monolingual); ignore
        max_sentences (use all loaded sentences); direction = mean(tgt_pool) - mean(src_pool).
    Due to linearity the two modes are numerically equivalent when pools have the same
    sentences, but 'centroids' deliberately uses the full monolingual devtest set without
    requiring parallel alignment.
    """
    if mode == "pairs":
        if max_sentences > 0:
            source_sentences = source_sentences[:max_sentences]
            target_sentences = target_sentences[:max_sentences]
        n = min(len(source_sentences), len(target_sentences))
        source_sentences = source_sentences[:n]
        target_sentences = target_sentences[:n]
        if n == 0:
            raise ValueError("source and target FLORES sentence pools must both be non-empty")
        pair_diffs: list[torch.Tensor] = []
        for src_sent, tgt_sent in zip(source_sentences, target_sentences):
            src_h = _sentence_hidden_state(model, tokenizer, src_sent, layer_idx, device)
            tgt_h = _sentence_hidden_state(model, tokenizer, tgt_sent, layer_idx, device)
            pair_diffs.append(tgt_h - src_h)
        raw_sv = torch.stack(pair_diffs).mean(0)
        src_count = tgt_count = n
    else:  # centroids
        if not source_sentences or not target_sentences:
            raise ValueError("source and target FLORES sentence pools must both be non-empty")
        src_states = [
            _sentence_hidden_state(model, tokenizer, s, layer_idx, device)
            for s in source_sentences
        ]
        tgt_states = [
            _sentence_hidden_state(model, tokenizer, s, layer_idx, device)
            for s in target_sentences
        ]
        raw_sv = torch.stack(tgt_states).mean(0) - torch.stack(src_states).mean(0)
        src_count = len(src_states)
        tgt_count = len(tgt_states)

    raw_norm = float(raw_sv.norm().item())
    unit_sv = raw_sv / raw_norm if raw_norm > 1e-8 else raw_sv

    meta = {
        "mode": mode,
        "source_sentence_count": src_count,
        "target_sentence_count": tgt_count,
        "layer_idx": layer_idx,
        "raw_vector_norm": round(raw_norm, 4),
    }
    return unit_sv, meta


@contextmanager
def steering_hook(
    model: Any,
    layer_indices: list[int],
    steering_vector: torch.Tensor,
    alpha: float,
) -> Iterator[None]:
    """Context manager that adds alpha * steering_vector to the output of each listed layer."""

    def _make_hook(sv: torch.Tensor, a: float):
        def _hook(module: Any, input: Any, output: Any) -> Any:
            v = sv.to(output[0].device, dtype=output[0].dtype)
            h = output[0] + a * v
            return (h,) + output[1:]
        return _hook

    handles = [
        model.model.layers[i].register_forward_hook(_make_hook(steering_vector, alpha))
        for i in layer_indices
    ]
    try:
        yield
    finally:
        for h in handles:
            h.remove()


def generate(
    model: Any,
    tokenizer: Any,
    prompt: str,
    device: torch.device,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    sv: torch.Tensor | None = None,
    alpha: float = 0.0,
    layer_indices: list[int] | None = None,
) -> str:
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    gen_kwargs: dict[str, Any] = dict(
        max_new_tokens=max_new_tokens,
        do_sample=temperature > 0,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )
    if temperature > 0:
        gen_kwargs["temperature"] = temperature
        gen_kwargs["top_p"] = top_p

    layers = layer_indices or []
    ctx = (
        steering_hook(model, layers, sv, alpha)
        if sv is not None and alpha > 0 and layers
        else _null_context()
    )
    with ctx, torch.no_grad():
        output = model.generate(**inputs, **gen_kwargs)

    generated = output[0][inputs["input_ids"].shape[-1]:]
    return tokenizer.decode(generated, skip_special_tokens=True).strip()


@contextmanager
def _null_context() -> Iterator[None]:
    yield


def language_heuristic(text: str, target_lang: str) -> dict[str, Any]:
    lowered = text.lower()
    stopwords: dict[str, tuple[str, ...]] = {
        "ind_Latn": (
            "yang", "dan", "untuk", "dengan", "saya", "tidak",
            "risiko", "publik", "adalah", "ini", "atau", "juga",
        ),
        "spa_Latn": (
            "que", "para", "con", "una", "los", "las",
            "riesgo", "público", "pero", "también", "del", "como",
        ),
        "eng_Latn": ("the", "and", "with", "that", "risk", "public", "should"),
    }
    hits = [
        word
        for word in stopwords.get(target_lang, ())
        if re.search(rf"\b{re.escape(word)}\b", lowered)
    ]
    return {
        "target_lang": target_lang,
        "stopword_hits": hits,
        "stopword_hit_count": len(hits),
        "non_ascii_ratio": round(sum(ord(ch) > 127 for ch in text) / max(len(text), 1), 4),
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model-id", required=True)
    p.add_argument("--flores-dir", required=True)
    p.add_argument("--source-lang", default="eng_Latn")
    p.add_argument("--target-lang", action="append", default=[])
    p.add_argument("--split", default="devtest")
    p.add_argument(
        "--max-pairs",
        type=int,
        default=0,
        help="Maximum sentences per language pool; 0 means use all loaded FLORES sentences.",
    )
    p.add_argument("--prompt", action="append", default=[])
    p.add_argument("--out", default="runs/language-steering-activation/probe.json")
    p.add_argument("--max-new-tokens", type=int, default=100)
    p.add_argument("--layer-idx", type=int, default=14, help="Transformer layer index (0-based). Repeated via --layer-idx is not supported; use --layer-indices.")
    p.add_argument("--layer-indices", type=str, default="", help="Comma-separated layer indices to apply steering simultaneously.")
    p.add_argument("--alpha", type=float, default=20.0, help="Steering strength in units of unit-norm vector.")
    p.add_argument("--alpha-sweep", type=str, default="", help="Comma-separated alpha values to sweep (overrides --alpha).")
    p.add_argument("--temperature", type=float, default=0.7)
    p.add_argument("--top-p", type=float, default=0.9)
    p.add_argument("--allow-download", action="store_true")
    p.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    p.add_argument(
        "--mode",
        choices=["pairs", "centroids"],
        default="pairs",
        help=(
            "'pairs' (default): treat FLORES sentences as parallel pairs, pairwise subtraction. "
            "'centroids': load all devtest sentences for each language independently (monolingual), "
            "compute language-level centroids, direction = target_centroid - english_centroid."
        ),
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    targets = args.target_lang or list(DEFAULT_TARGETS)
    prompts = args.prompt or list(DEFAULT_PROMPTS)

    if args.device == "cuda":
        device = torch.device("cuda")
    elif args.device == "cpu":
        device = torch.device("cpu")
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    alpha_values: list[float]
    if args.alpha_sweep:
        alpha_values = [float(x.strip()) for x in args.alpha_sweep.split(",") if x.strip()]
    else:
        alpha_values = [args.alpha]

    active_layers: list[int]
    if args.layer_indices:
        active_layers = [int(x.strip()) for x in args.layer_indices.split(",") if x.strip()]
    else:
        active_layers = [args.layer_idx]

    from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: PLC0415

    tokenizer = AutoTokenizer.from_pretrained(
        args.model_id, local_files_only=not args.allow_download
    )
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id,
        local_files_only=not args.allow_download,
        torch_dtype=torch.float16 if device.type == "cuda" else torch.float32,
    )
    model.to(device).eval()
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    num_layers = len(model.model.layers)
    print(f"Model: {args.model_id}  Layers: {num_layers}  Device: {device}")

    flores_dir = Path(args.flores_dir)
    rows: list[dict[str, Any]] = []
    sv_metadata: list[dict[str, Any]] = []

    for target in targets:
        src_sents = read_flores_file(flores_dir, args.split, args.source_lang)
        tgt_sents = read_flores_file(flores_dir, args.split, target)

        primary_layer = active_layers[0]
        max_desc = "all" if args.max_pairs <= 0 or args.mode == "centroids" else str(args.max_pairs)
        print(
            f"\nComputing steering vector: {args.source_lang} -> {target}  "
            f"mode={args.mode}  primary_layer={primary_layer}  active_layers={active_layers}  "
            f"sentences_per_language={max_desc}"
        )
        sv, sv_meta = compute_steering_vector(
            model,
            tokenizer,
            src_sents,
            tgt_sents,
            layer_idx=primary_layer,
            device=device,
            max_sentences=args.max_pairs,
            mode=args.mode,
        )
        sv_meta["source_lang"] = args.source_lang
        sv_meta["target_lang"] = target
        sv_meta["active_layers"] = active_layers
        sv_metadata.append(sv_meta)
        print(f"  raw_vector_norm={sv_meta['raw_vector_norm']}")

        for prompt in prompts:
            baseline = generate(
                model, tokenizer, prompt, device,
                max_new_tokens=args.max_new_tokens,
                temperature=args.temperature,
                top_p=args.top_p,
                sv=None,
                alpha=0.0,
                layer_indices=active_layers,
            )
            print(f"  baseline: {baseline[:80]!r}")

            for alpha in alpha_values:
                steered = generate(
                    model, tokenizer, prompt, device,
                    max_new_tokens=args.max_new_tokens,
                    temperature=args.temperature,
                    top_p=args.top_p,
                    sv=sv,
                    alpha=alpha,
                    layer_indices=active_layers,
                )
                bl_heur = language_heuristic(baseline, target)
                st_heur = language_heuristic(steered, target)
                print(f"  alpha={alpha}: {steered[:80]!r}  hits={st_heur['stopword_hit_count']}")
                rows.append(
                    {
                        "target_lang": target,
                        "active_layers": active_layers,
                        "alpha": alpha,
                        "prompt": prompt,
                        "baseline": baseline,
                        "steered": steered,
                        "baseline_language_heuristic": bl_heur,
                        "steered_language_heuristic": st_heur,
                    }
                )

    report = {
        "artifact_type": "activation_steering_probe",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model": args.model_id,
        "device": str(device),
        "source_lang": args.source_lang,
        "targets": targets,
        "active_layers": active_layers,
        "alpha_values": alpha_values,
        "split": args.split,
        "max_pairs": args.max_pairs,
        "num_model_layers": num_layers,
        "mode": args.mode,
        "method": (
            "FLORES-200 language-level centroids (mode=centroids): all devtest sentences "
            "for each language loaded independently (monolingual); "
            "direction = mean_pooled(target) - mean_pooled(english), unit-normalized."
            if args.mode == "centroids" else
            "FLORES-200 parallel pairs (mode=pairs): pairwise subtraction "
            "mean(tgt_hidden_i - src_hidden_i) at primary_layer, unit-normalized."
        ) + (
            " English is the default source anchor. "
            "alpha * steering_vector is added to the residual stream at each active_layer via forward hooks. "
            "No language instructions appear in the content prompts."
        ),
        "steering_vector_metadata": sv_metadata,
        "generations": rows,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
