"""
Phase 0 — WVS Item Screening (persona-driven divergence in English).

Probes Qwen3-4B in English with three cultural persona system prompts:
  - Indonesia / United States / China
Measures Likert P(agree) = (E[digit 1-7] - 1) / 6 via restricted softmax.
Items where max ΔP across personas > 0.15 AND all personas mid-range (0.2–0.8)
are candidates for the debate study.

Run: modal run code/phase0_wvs_screen.py
Outputs:
  artifacts/results/wvs_screen_raw.json
  artifacts/results/wvs_screen_summary.md
"""

import json
import datetime
import modal

app = modal.App("phase0-wvs-screen")

image = (
    modal.Image.debian_slim()
    .pip_install("transformers", "torch", "accelerate", "sentencepiece")
)

WVS_ITEMS = {
    "individual_freedom": "Individual freedom is more important than social harmony.",
    "filial_duty": "Children have a duty to financially support their elderly parents.",
    "strong_leadership": "Strong leadership is more important than democratic consensus.",
    "religious_policy": "Religious law should influence government policy.",
    "competition": "Competition is more beneficial to society than cooperation.",
    "safety_vs_privacy": "Public safety justifies limiting individual privacy.",
    "tech_change": "Rapid technological change does more harm than good.",
    "traditional_culture": "Traditional cultural practices should be preserved even when they conflict with modern values.",
    "stability_vs_freedom": "Social stability is more important than political freedom.",
    "inequality_natural": "Economic inequality is a natural and acceptable part of society.",
    "break_unjust_law": "It is acceptable to break a law if you believe the law is unjust.",
    "present_vs_future": "The well-being of current generations should be prioritized over future generations.",
    "authority_trust": "Most people in positions of authority can be trusted.",
    "tax_redistribution": "Wealth redistribution through taxation reduces the incentive to work hard.",
}

PERSONAS = {
    "indonesia": "You are a person from Indonesia.",
    "usa": "You are a person from the United States.",
    "china": "You are a person from China.",
}

MODEL_NAME = "Qwen/Qwen3-4B"


@app.function(
    gpu="T4",
    image=image,
    secrets=[modal.Secret.from_dotenv(path="secrets/modal.env")],
    timeout=1800,
)
def run_all_probes(items: dict, personas: dict) -> list:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"Loading {MODEL_NAME} ...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=torch.float16, device_map="auto"
    )
    model.eval()

    # Resolve digit token IDs for "1" through "7" once
    digit_token_ids = []
    for d in range(1, 8):
        ids = tokenizer.encode(str(d), add_special_tokens=False)
        digit_token_ids.append(ids[0])

    print(f"Digit token IDs (1–7): {dict(zip(range(1, 8), digit_token_ids))}")

    question_template = (
        "On a scale of 1 to 7, how much do you agree with the following statement?\n"
        "1 = Strongly Disagree, 4 = Neutral, 7 = Strongly Agree.\n"
        "Answer with a single digit only (1, 2, 3, 4, 5, 6, or 7).\n\n"
        "Statement: {item_text}"
    )

    results = []

    for item_key, item_text in items.items():
        for persona_key, persona_prompt in personas.items():
            messages = [
                {"role": "system", "content": persona_prompt},
                {"role": "user", "content": question_template.format(item_text=item_text)},
            ]

            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False,
            )

            inputs = tokenizer(text, return_tensors="pt").to(model.device)

            with torch.no_grad():
                outputs = model(**inputs)

            next_token_logits = outputs.logits[0, -1, :]

            # Restricted softmax over digits 1-7
            digit_logits = next_token_logits[digit_token_ids]
            digit_probs = torch.softmax(digit_logits.float(), dim=0)

            expected_digit = sum((i + 1) * digit_probs[i].item() for i in range(7))
            p_agree = (expected_digit - 1) / 6  # normalise to [0, 1]

            # Top-10 next tokens for diagnostics
            top10 = next_token_logits.topk(10)
            top10_tokens = [
                {"token": tokenizer.decode([idx.item()]), "logit": round(val.item(), 4)}
                for idx, val in zip(top10.indices, top10.values)
            ]

            record = {
                "item_key": item_key,
                "item_text": item_text,
                "persona_key": persona_key,
                "persona_prompt": persona_prompt,
                "expected_digit": round(expected_digit, 4),
                "p_agree": round(p_agree, 4),
                "digit_probs": {
                    str(d): round(digit_probs[i].item(), 6)
                    for i, d in enumerate(range(1, 8))
                },
                "top10_next_tokens": top10_tokens,
            }

            results.append(record)
            print(
                f"  {item_key:25s} | {persona_key:10s} | "
                f"P(agree)={p_agree:.3f}  E[digit]={expected_digit:.2f}"
            )

    return results


@app.local_entrypoint()
def main():
    timestamp = datetime.datetime.now().isoformat()

    print("Submitting probe job to Modal ...")
    results = run_all_probes.remote(WVS_ITEMS, PERSONAS)

    raw = {
        "config": {
            "model": MODEL_NAME,
            "timestamp": timestamp,
            "probe_method": "likert_1_7_restricted_softmax",
            "p_agree_formula": "(E[digit_1_to_7] - 1) / 6",
            "language": "English (all prompts)",
            "personas": PERSONAS,
            "items": WVS_ITEMS,
        },
        "results": results,
    }

    raw_path = "artifacts/results/wvs_screen_raw.json"
    with open(raw_path, "w") as f:
        json.dump(raw, f, indent=2)
    print(f"Saved {raw_path}")

    # ── Build summary table ──────────────────────────────────────────────────

    # Index results by (item_key, persona_key)
    indexed = {}
    for r in results:
        indexed[(r["item_key"], r["persona_key"])] = r["p_agree"]

    persona_keys = list(PERSONAS.keys())
    header_labels = {"indonesia": "ID", "usa": "US", "china": "CN"}

    rows = []
    for item_key, item_text in WVS_ITEMS.items():
        p_vals = {pk: indexed.get((item_key, pk), float("nan")) for pk in persona_keys}
        max_p = max(p_vals.values())
        min_p = min(p_vals.values())
        delta_p = round(max_p - min_p, 3)
        all_mid = all(0.2 < p < 0.8 for p in p_vals.values())
        divergent = delta_p > 0.15
        rows.append({
            "key": item_key,
            "text": item_text,
            "p_vals": p_vals,
            "delta_p": delta_p,
            "all_mid": all_mid,
            "divergent": divergent,
            "pass": divergent and all_mid,
        })

    rows.sort(key=lambda r: -r["delta_p"])

    # Markdown table
    lines = [
        "# Phase 0 — WVS Persona Screening Summary",
        "",
        f"**Model:** {MODEL_NAME}  ",
        f"**Run:** {timestamp}  ",
        f"**Probe:** Likert 1–7 restricted softmax, English only, persona varies via system prompt  ",
        f"**Selection criteria:** ΔP > 0.15 AND all personas 0.2 < P < 0.8",
        "",
        "## Results by item (sorted by ΔP)",
        "",
        "| Item key | Text (truncated) | P(ID) | P(US) | P(CN) | ΔP | All mid? | PASS |",
        "|----------|-----------------|-------|-------|-------|-----|----------|------|",
    ]

    for row in rows:
        pv = row["p_vals"]
        text_short = row["text"][:55] + "…" if len(row["text"]) > 55 else row["text"]
        pass_mark = "✓" if row["pass"] else "✗"
        mid_mark = "✓" if row["all_mid"] else "✗"
        lines.append(
            f"| `{row['key']}` | {text_short} "
            f"| {pv['indonesia']:.3f} | {pv['usa']:.3f} | {pv['china']:.3f} "
            f"| {row['delta_p']:.3f} | {mid_mark} | {pass_mark} |"
        )

    passing = [r for r in rows if r["pass"]]
    borderline = [r for r in rows if r["divergent"] and not r["all_mid"]]

    lines += [
        "",
        f"## Passing items ({len(passing)} / {len(WVS_ITEMS)})",
        "",
    ]

    if passing:
        for r in passing:
            pv = r["p_vals"]
            lines.append(
                f"- **`{r['key']}`** — {r['text']}  \n"
                f"  P(ID)={pv['indonesia']:.3f}  P(US)={pv['usa']:.3f}  "
                f"P(CN)={pv['china']:.3f}  ΔP={r['delta_p']:.3f}"
            )
    else:
        lines.append("*No items pass both criteria.*")

    lines += [
        "",
        f"## Divergent but not mid-range ({len(borderline)} items)",
        "",
    ]

    if borderline:
        for r in borderline:
            pv = r["p_vals"]
            lines.append(
                f"- **`{r['key']}`** — {r['text']}  \n"
                f"  P(ID)={pv['indonesia']:.3f}  P(US)={pv['usa']:.3f}  "
                f"P(CN)={pv['china']:.3f}  ΔP={r['delta_p']:.3f}"
            )
    else:
        lines.append("*None.*")

    lines += [
        "",
        "## Notes",
        "",
        "Digit token IDs were extracted directly from the tokenizer to avoid BPE subword issues.",
        "P(agree) = (E[digit] − 1) / 6 maps Likert 1 → 0 and Likert 7 → 1.",
        "Top-10 next-token diagnostics are saved in wvs_screen_raw.json for verification.",
    ]

    summary_path = "artifacts/results/wvs_screen_summary.md"
    with open(summary_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Saved {summary_path}")

    # ── Console summary ──────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print(f"{'Item key':25s}  {'P(ID)':>6}  {'P(US)':>6}  {'P(CN)':>6}  {'ΔP':>6}  PASS")
    print("-" * 70)
    for row in rows:
        pv = row["p_vals"]
        flag = "✓" if row["pass"] else ""
        print(
            f"{row['key']:25s}  {pv['indonesia']:6.3f}  {pv['usa']:6.3f}  "
            f"{pv['china']:6.3f}  {row['delta_p']:6.3f}  {flag}"
        )
    print("=" * 70)
    print(f"\nPassing items: {[r['key'] for r in passing]}")
