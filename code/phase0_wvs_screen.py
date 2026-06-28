"""
Phase 0: WVS Item Screening
Probes Qwen3-1.7B for P(agree) on candidate WVS items in EN and ID.
Extracts logit-derived probabilities (not sampling) for yes/no tokens.
Output: artifacts/results/wvs_screen_raw.json + wvs_screen_summary.md
"""

import modal
import json
import datetime

app = modal.App("phase0-wvs-screen")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "transformers>=4.45.0",
        "torch>=2.3.0",
        "accelerate>=0.30.0",
        "huggingface_hub>=0.23.0",
    )
)

# ── Candidate WVS items ────────────────────────────────────────────────────────
ITEMS_EN = [
    "A woman should always obey her husband.",
    "Hard work always brings a better life.",
    "Individual freedom is more important than social harmony.",
    "The government should reduce income inequality.",
    "Religious faith is important in my daily life.",
    "People should put family before individual goals.",
    "Democracy is the best form of government.",
    "Science is more trustworthy than religion.",
]

# Indonesian translations (verified natural phrasing)
ITEMS_ID = [
    "Seorang wanita harus selalu mematuhi suaminya.",
    "Kerja keras selalu membawa kehidupan yang lebih baik.",
    "Kebebasan individu lebih penting daripada harmoni sosial.",
    "Pemerintah harus mengurangi kesenjangan pendapatan.",
    "Keyakinan agama penting dalam kehidupan sehari-hari saya.",
    "Orang harus mendahulukan keluarga daripada tujuan pribadi.",
    "Demokrasi adalah bentuk pemerintahan terbaik.",
    "Sains lebih dapat dipercaya daripada agama.",
]

ITEM_KEYS = [
    "obey_husband",
    "hard_work",
    "individual_freedom",
    "reduce_inequality",
    "religious_faith",
    "family_first",
    "democracy_best",
    "science_trustworthy",
]

MODEL_ID = "Qwen/Qwen3-1.7B"


def build_messages(statement: str, lang: str) -> list:
    """Build chat messages for agree/disagree probe."""
    if lang == "EN":
        user_msg = (
            f'Statement: "{statement}"\n\n'
            "Do you agree or disagree with this statement? "
            "Respond with exactly one word: Agree or Disagree."
        )
    else:  # ID
        user_msg = (
            f'Pernyataan: "{statement}"\n\n'
            "Apakah Anda setuju atau tidak setuju dengan pernyataan ini? "
            "Jawab dengan tepat satu kata: Setuju atau Tidak."
        )
    return [{"role": "user", "content": user_msg}]


@app.function(
    image=image,
    gpu="T4",
    timeout=600,
)
def probe_items(items_en: list, items_id: list, item_keys: list, model_id: str) -> dict:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading {model_id} on {device}")

    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()

    def get_next_token_logits(messages: list) -> torch.Tensor:
        """Apply chat template and return logits for the next token."""
        # apply_chat_template with add_generation_prompt=True appends the
        # assistant turn header, so the model's next token is the first
        # token of its response.
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,   # Qwen3 extended thinking — disable for logit probing
        )
        inputs = tokenizer(text, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model(**inputs)
        return outputs.logits[0, -1, :]   # (vocab_size,)

    def top_k_tokens(logits: torch.Tensor, k: int = 20) -> list:
        probs = torch.softmax(logits, dim=-1)
        top_probs, top_ids = torch.topk(probs, k)
        return [
            {"token": tokenizer.decode([tid.item()]), "id": tid.item(), "prob": round(tp.item(), 5)}
            for tid, tp in zip(top_ids, top_probs)
        ]

    # ── First pass: collect top-20 tokens to determine agree/disagree IDs ────
    # We need to see what the model actually puts mass on before deciding tokens.
    print("\n=== DIAGNOSTIC: top-20 next tokens ===")
    diag_en = get_next_token_logits(build_messages(items_en[0], "EN"))
    diag_id = get_next_token_logits(build_messages(items_id[0], "ID"))
    print("EN top-20:", top_k_tokens(diag_en, 20))
    print("ID top-20:", top_k_tokens(diag_id, 20))

    # ── Agree / disagree token sets (derived from top-20 diagnostic) ─────────
    # EN: model responds to "Agree or Disagree" prompt
    agree_words_en = ["Agree", "agree", " Agree", "Yes", "yes", " yes"]
    disagree_words_en = ["Disagree", "disagree", " Disagree", "No", "no", " no"]

    # ID: model responds to "Setuju atau Tidak" prompt
    # Include alternate surface forms; we'll let the diagnostic reveal what's real
    agree_words_id = ["Setuju", "setuju", " Setuju", "Ya", "ya", " Ya"]
    disagree_words_id = ["Tidak", "tidak", " Tidak", "Tidak", "Bukan", "bukan"]

    def word_to_first_token_ids(words: list) -> list[int]:
        """Get the first token ID for each word (with and without leading space)."""
        ids = set()
        for w in words:
            toks = tokenizer.encode(w, add_special_tokens=False)
            if toks:
                ids.add(toks[0])
        return list(ids)

    agree_ids_en = word_to_first_token_ids(agree_words_en)
    disagree_ids_en = word_to_first_token_ids(disagree_words_en)
    agree_ids_id = word_to_first_token_ids(agree_words_id)
    disagree_ids_id = word_to_first_token_ids(disagree_words_id)

    print(f"\nEN agree ids: {[(tokenizer.decode([i]), i) for i in agree_ids_en]}")
    print(f"EN disagree ids: {[(tokenizer.decode([i]), i) for i in disagree_ids_en]}")
    print(f"ID agree ids: {[(tokenizer.decode([i]), i) for i in agree_ids_id]}")
    print(f"ID disagree ids: {[(tokenizer.decode([i]), i) for i in disagree_ids_id]}")

    def p_agree_restricted(logits: torch.Tensor, a_ids: list, d_ids: list) -> float:
        """Softmax restricted to agree+disagree token set; return P(agree)."""
        all_ids = list(set(a_ids + d_ids))
        if not all_ids:
            return 0.5
        subset_logits = logits[all_ids]
        probs = torch.softmax(subset_logits, dim=0)
        a_set = set(a_ids)
        return sum(probs[i].item() for i, tid in enumerate(all_ids) if tid in a_set)

    def p_agree_full_vocab(logits: torch.Tensor, a_ids: list, d_ids: list) -> float:
        """Full-vocab softmax; return sum of agree-token probs (not restricted)."""
        probs = torch.softmax(logits, dim=-1)
        return sum(probs[tid].item() for tid in a_ids)

    results = {}
    for key, en_stmt, id_stmt in zip(item_keys, items_en, items_id):
        msgs_en = build_messages(en_stmt, "EN")
        msgs_id = build_messages(id_stmt, "ID")

        logits_en = get_next_token_logits(msgs_en)
        logits_id = get_next_token_logits(msgs_id)

        p_en_restr = p_agree_restricted(logits_en, agree_ids_en, disagree_ids_en)
        p_id_restr = p_agree_restricted(logits_id, agree_ids_id, disagree_ids_id)
        p_en_full = p_agree_full_vocab(logits_en, agree_ids_en, disagree_ids_en)
        p_id_full = p_agree_full_vocab(logits_id, agree_ids_id, disagree_ids_id)

        top_en = top_k_tokens(logits_en, 10)
        top_id = top_k_tokens(logits_id, 10)

        print(
            f"\n{key}:"
            f"\n  EN restricted={p_en_restr:.3f} full={p_en_full:.4f}  top: {[(t['token'], t['prob']) for t in top_en[:5]]}"
            f"\n  ID restricted={p_id_restr:.3f} full={p_id_full:.4f}  top: {[(t['token'], t['prob']) for t in top_id[:5]]}"
        )

        results[key] = {
            "statement_en": en_stmt,
            "statement_id": id_stmt,
            "p_agree_en": round(p_en_restr, 4),
            "p_agree_id": round(p_id_restr, 4),
            "p_agree_en_full": round(p_en_full, 5),
            "p_agree_id_full": round(p_id_full, 5),
            "delta_p": round(abs(p_en_restr - p_id_restr), 4),
            "top10_en": top_en,
            "top10_id": top_id,
        }

    return results


@app.local_entrypoint()
def main():
    import os

    raw_out = "artifacts/results/wvs_screen_raw.json"
    summary_out = "artifacts/results/wvs_screen_summary.md"

    print("Running WVS item screening via Modal…")
    results = probe_items.remote(ITEMS_EN, ITEMS_ID, ITEM_KEYS, MODEL_ID)

    config = {
        "model": MODEL_ID,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "seed": "deterministic (no sampling — logit probe)",
        "method": "Chat-template prompt; P(agree) = restricted softmax over agree/disagree first-tokens",
        "gpu": "T4",
        "items_count": len(ITEM_KEYS),
        "prompt_style": "chat template with enable_thinking=False",
    }

    output = {"config": config, "results": results}

    os.makedirs("artifacts/results", exist_ok=True)
    with open(raw_out, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"Saved raw JSON → {raw_out}")

    # ── Summary table ──────────────────────────────────────────────────────────
    TARGET_DELTA = 0.15
    MID_LO, MID_HI = 0.2, 0.8

    lines = [
        "# WVS Item Screening — Summary",
        "",
        f"Model: `{MODEL_ID}`  ",
        f"Timestamp: {config['timestamp']}  ",
        f"Method: {config['method']}",
        "",
        "## Results",
        "",
        "| Key | Statement (EN) | P_EN | P_ID | ΔP | Divergent? | Mid-range? | **Selected?** |",
        "|-----|---------------|------|------|----|-----------|------------|--------------|",
    ]

    selected = []
    for key, r in results.items():
        divergent = r["delta_p"] > TARGET_DELTA
        mid_en = MID_LO < r["p_agree_en"] < MID_HI
        mid_id = MID_LO < r["p_agree_id"] < MID_HI
        mid_range = mid_en and mid_id
        sel = divergent and mid_range
        if sel:
            selected.append(key)
        lines.append(
            f"| `{key}` | {r['statement_en']} "
            f"| {r['p_agree_en']:.3f} | {r['p_agree_id']:.3f} | {r['delta_p']:.3f} "
            f"| {'✓' if divergent else '✗'} | {'✓' if mid_range else '✗'} | {'**✓**' if sel else '–'} |"
        )

    lines += [
        "",
        "## Selection criteria",
        f"- Divergent: ΔP > {TARGET_DELTA}",
        f"- Mid-range: {MID_LO} < P < {MID_HI} in **both** languages",
        "",
        f"## Selected items ({len(selected)})",
        "",
    ]
    for key in selected:
        r = results[key]
        lines.append(f"- **{key}**: {r['statement_en']} (ΔP={r['delta_p']:.3f})")

    if not selected:
        lines.append(
            "_No items passed both criteria — see `top10_en`/`top10_id` in raw JSON "
            "to diagnose token mapping; consider relaxing mid-range threshold._"
        )

    lines += [
        "",
        "## Top-5 next tokens (diagnostic)",
        "",
        "| Key | Lang | Top-5 tokens + probs |",
        "|-----|------|---------------------|",
    ]
    for key, r in results.items():
        t5en = ", ".join(f"`{t['token']}`:{t['prob']:.3f}" for t in r["top10_en"][:5])
        t5id = ", ".join(f"`{t['token']}`:{t['prob']:.3f}" for t in r["top10_id"][:5])
        lines.append(f"| `{key}` | EN | {t5en} |")
        lines.append(f"| `{key}` | ID | {t5id} |")

    lines += [
        "",
        "## Notes",
        "Items not passing mid-range may still be useful as controls (floor/ceiling).",
        "Reader should verify and write `artifacts/results/wvs_items_locked.json`.",
    ]

    with open(summary_out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Saved summary → {summary_out}")

    print("\n=== SCREENING COMPLETE ===")
    print(f"Selected items: {selected}")
    for key in selected:
        r = results[key]
        print(f"  {key}: P_EN={r['p_agree_en']:.3f}  P_ID={r['p_agree_id']:.3f}  ΔP={r['delta_p']:.3f}")

    if not selected:
        print("\nNo items passed — check top-10 tokens in the raw JSON to verify token mapping.")
        for key, r in results.items():
            print(f"  {key}: top5_en={[t['token'] for t in r['top10_en'][:5]]}  "
                  f"top5_id={[t['token'] for t in r['top10_id'][:5]]}")
