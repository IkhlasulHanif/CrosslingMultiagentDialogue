#!/usr/bin/env python3
"""Activation-level language steering from FLORES-200 parallel sentence pairs.

Computes a steering vector = mean(target_hidden_states) - mean(source_hidden_states)
at a specified transformer layer, normalized to unit norm, then injects
alpha * steering_vector into the residual stream during generation via a
forward hook registered on that layer.

This avoids prompt-level language instructions and operates directly on
internal representations, giving coherent language switching (unlike logit bias
which causes token repetition at high scales).
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
    max_pairs: int = 200,
) -> tuple[torch.Tensor, dict[str, Any]]:
    """Return (unit-norm steering vector, metadata)."""
    n = min(len(source_sentences), len(target_sentences), max_pairs)
    src_states: list[torch.Tensor] = []
    tgt_states: list[torch.Tensor] = []

    for i in range(n):
        src_states.append(
            _sentence_hidden_state(model, tokenizer, source_sentences[i], layer_idx, device)
        )
        tgt_states.append(
            _sentence_hidden_state(model, tokenizer, target_sentences[i], layer_idx, device)
        )

    raw_sv = torch.stack(tgt_states).mean(0) - torch.stack(src_states).mean(0)
    raw_norm = float(raw_sv.norm().item())
    if raw_norm > 1e-8:
        unit_sv = raw_sv / raw_norm
    else:
        unit_sv = raw_sv

    meta = {
        "pair_count": n,
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
    p.add_argument("--max-pairs", type=int, default=200)
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
        src_sents = read_flores_file(flores_dir, args.split, args.source_lang)[: args.max_pairs]
        tgt_sents = read_flores_file(flores_dir, args.split, target)[: args.max_pairs]

        primary_layer = active_layers[0]
        print(f"\nComputing steering vector: {args.source_lang} → {target}  primary_layer={primary_layer}  active_layers={active_layers}  n={min(len(src_sents), len(tgt_sents), args.max_pairs)}")
        sv, sv_meta = compute_steering_vector(
            model,
            tokenizer,
            src_sents,
            tgt_sents,
            layer_idx=primary_layer,
            device=device,
            max_pairs=args.max_pairs,
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
        "method": (
            "FLORES-200 parallel sentences define a steering vector as "
            "mean_pooled(target_hidden) - mean_pooled(source_hidden) at primary_layer, "
            "normalized to unit norm. During generation, alpha * steering_vector is "
            "added to the residual stream at each active_layer via forward hooks. "
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
