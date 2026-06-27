#!/usr/bin/env python3
"""Contrastive Activation Addition (CAA) for language steering.

Instead of using mean hidden-state differences from FLORES sentence pairs,
CAA uses carefully designed contrast pairs that target the instruction-following
direction for language choice:

  positive: "Please respond in [TARGET_LANG]: [content]"
  negative: "Please respond in English: [content]"

The steering vector = mean(positive_hidden) - mean(negative_hidden) at a
specified layer. This vector captures the "respond in target language vs English"
direction within the instruction-following subspace, which should be more
effective than a raw language content difference.

This avoids prompt-level instructions in the CONTENT prompt: the content prompt
asks about a policy topic without language direction. The CAA vector pushes
the model toward target-language generation via the residual stream.
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


DEFAULT_PROMPTS = (
    "Public release of dual-use policy datasets should balance civic access and misuse risk.",
    "Open models can improve accountability, but deployment should account for downstream harm.",
)

LANG_NAMES = {
    "ind_Latn": "Indonesian",
    "spa_Latn": "Spanish",
    "fra_Latn": "French",
    "deu_Latn": "German",
    "zho_Hans": "Chinese",
}

# Diverse neutral topics for contrast pair generation (not the test prompts)
CONTRAST_TOPICS = [
    "The capital of France is Paris.",
    "Water boils at 100 degrees Celsius at sea level.",
    "The sun rises in the east.",
    "Mathematics is the language of science.",
    "Reading books expands the mind.",
    "Exercise is important for health.",
    "Technology has changed how we communicate.",
    "Education opens doors to opportunity.",
    "Music affects our emotions.",
    "The ocean covers most of the Earth's surface.",
    "Trees produce oxygen through photosynthesis.",
    "History teaches us about the past.",
    "Cooking requires practice and patience.",
    "Art expresses what words cannot.",
    "Time is a precious resource.",
    "Friendship is important in life.",
    "Science helps us understand nature.",
    "Cities are centers of culture and commerce.",
    "Sleep is essential for health.",
    "Language shapes how we think.",
]


def _sentence_hidden_state(
    model: Any,
    tokenizer: Any,
    text: str,
    layer_idx: int,
    device: torch.device,
) -> torch.Tensor:
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=256,
        padding=False,
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs, output_hidden_states=True)
    # hidden_states[0] = embedding; hidden_states[i+1] = layer i output
    hidden = outputs.hidden_states[layer_idx + 1]  # (1, seq_len, hidden_size)
    # Use last token position (most context-aware)
    return hidden[0, -1, :].float().cpu()


def compute_caa_vector(
    model: Any,
    tokenizer: Any,
    target_lang: str,
    layer_idx: int,
    device: torch.device,
    topics: list[str] | None = None,
) -> tuple[torch.Tensor, dict[str, Any]]:
    """Compute CAA steering vector using instruction-contrast pairs."""
    lang_name = LANG_NAMES.get(target_lang, target_lang)
    topics = topics or CONTRAST_TOPICS

    pos_states: list[torch.Tensor] = []
    neg_states: list[torch.Tensor] = []

    for topic in topics:
        pos_text = f"Please respond in {lang_name}: {topic}"
        neg_text = f"Please respond in English: {topic}"
        pos_states.append(_sentence_hidden_state(model, tokenizer, pos_text, layer_idx, device))
        neg_states.append(_sentence_hidden_state(model, tokenizer, neg_text, layer_idx, device))

    raw_sv = torch.stack(pos_states).mean(0) - torch.stack(neg_states).mean(0)
    raw_norm = float(raw_sv.norm().item())
    if raw_norm > 1e-8:
        unit_sv = raw_sv / raw_norm
    else:
        unit_sv = raw_sv

    meta = {
        "method": "caa_instruction_contrast",
        "target_lang": target_lang,
        "lang_name": lang_name,
        "layer_idx": layer_idx,
        "n_contrast_pairs": len(topics),
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
    def _make_hook(sv: torch.Tensor, a: float):
        def _hook(module: Any, input: Any, output: Any) -> Any:
            v = sv.to(output[0].device, dtype=output[0].dtype)
            return (output[0] + a * v,) + output[1:]
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


@contextmanager
def _null_context() -> Iterator[None]:
    yield


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


def language_heuristic(text: str, target_lang: str) -> dict[str, Any]:
    lowered = text.lower()
    stopwords: dict[str, tuple[str, ...]] = {
        "ind_Latn": (
            "yang", "dan", "untuk", "dengan", "saya", "tidak",
            "risiko", "publik", "adalah", "ini", "atau", "juga", "bahwa",
        ),
        "spa_Latn": (
            "que", "para", "con", "una", "los", "las",
            "riesgo", "público", "pero", "también", "del", "como", "son",
        ),
        "fra_Latn": (
            "que", "pour", "avec", "est", "les", "des", "une",
            "mais", "aussi", "donc", "risque",
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
    p.add_argument("--source-lang", default="eng_Latn")
    p.add_argument("--target-lang", action="append", default=[])
    p.add_argument("--prompt", action="append", default=[])
    p.add_argument("--out", default="runs/language-steering-caa/probe.json")
    p.add_argument("--max-new-tokens", type=int, default=100)
    p.add_argument("--layer-indices", type=str, default="14,16,18")
    p.add_argument("--alpha", type=float, default=20.0)
    p.add_argument("--alpha-sweep", type=str, default="")
    p.add_argument("--temperature", type=float, default=0.7)
    p.add_argument("--top-p", type=float, default=0.9)
    p.add_argument("--allow-download", action="store_true")
    p.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    targets = args.target_lang or ["ind_Latn", "spa_Latn"]
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

    active_layers = [int(x.strip()) for x in args.layer_indices.split(",") if x.strip()]

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
    print(f"CAA layers: {active_layers}  alpha sweep: {alpha_values}")

    rows: list[dict[str, Any]] = []
    sv_metadata: list[dict[str, Any]] = []

    for target in targets:
        print(f"\nComputing CAA vector: {args.source_lang} → {target}  layers={active_layers}")
        sv, sv_meta = compute_caa_vector(
            model, tokenizer, target,
            layer_idx=active_layers[0],
            device=device,
        )
        sv_meta["active_layers"] = active_layers
        sv_metadata.append(sv_meta)
        print(f"  raw_vector_norm={sv_meta['raw_vector_norm']}")

        for prompt in prompts:
            baseline = generate(
                model, tokenizer, prompt, device,
                max_new_tokens=args.max_new_tokens,
                temperature=args.temperature,
                top_p=args.top_p,
                sv=None, alpha=0.0, layer_indices=active_layers,
            )
            print(f"  baseline: {baseline[:80]!r}")

            for alpha in alpha_values:
                steered = generate(
                    model, tokenizer, prompt, device,
                    max_new_tokens=args.max_new_tokens,
                    temperature=args.temperature,
                    top_p=args.top_p,
                    sv=sv, alpha=alpha, layer_indices=active_layers,
                )
                bl_h = language_heuristic(baseline, target)
                st_h = language_heuristic(steered, target)
                print(f"  alpha={alpha}: {steered[:80]!r}  hits={st_h['stopword_hit_count']}")
                rows.append({
                    "target_lang": target,
                    "active_layers": active_layers,
                    "alpha": alpha,
                    "prompt": prompt,
                    "baseline": baseline,
                    "steered": steered,
                    "baseline_language_heuristic": bl_h,
                    "steered_language_heuristic": st_h,
                })

    report = {
        "artifact_type": "caa_steering_probe",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model": args.model_id,
        "device": str(device),
        "source_lang": args.source_lang,
        "targets": targets,
        "active_layers": active_layers,
        "alpha_values": alpha_values,
        "num_model_layers": num_layers,
        "method": (
            "Contrastive Activation Addition (CAA): contrast pairs are "
            "'Please respond in [LANG]: [topic]' vs 'Please respond in English: [topic]'. "
            "Steering vector = mean(pos_hidden[-1]) - mean(neg_hidden[-1]) at the primary layer, "
            "normalized to unit norm. Applied at active_layers during generation. "
            "Content prompts contain no language instructions."
        ),
        "caa_metadata": sv_metadata,
        "generations": rows,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
