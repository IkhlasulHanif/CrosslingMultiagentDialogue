"""Generate configs/runs/*.toml for S3-S9 and Stage B.

  python configs/make_configs.py stageA --noleak {0,1}      S3-S9 (noleak line added from S3 on if S2 adopted it)
  python configs/make_configs.py stageB --variants a,b,...  B1-B3 on the grounded-v1 variant list
"""
import sys
from pathlib import Path

D = Path(__file__).resolve().parent / "runs"
WORKERS = 4


def write(run, step, note, variants, n, langs=None, seed_start=1):
    lines = [f'step = "{step}"', f'note = "{note}"', "variants = [" + ", ".join(f'"{v}"' for v in variants) + "]",
             f"n = {n}", f"seed_start = {seed_start}", f"workers = {WORKERS}"]
    if langs:
        lines.append(f'langs = {{ seller = "{langs[0]}", buyer = "{langs[1]}" }}')
    (D / f"{run}.toml").write_text("\n".join(lines) + "\n")
    print("wrote", run)


def stage_a(noleak):
    nl = ["noleak"] if noleak else []
    write("var-zopa", "S3", "randomized c and v; 25% of games v < c (walk away is correct)", ["zopa"] + nl, 100)
    write("var-batna", "S4", "private outside options for both sides on 40/60", ["fixed", "batna"] + nl, 100)
    write("var-deadline", "S5", "one random seat loses 5% of payoff per round; the other does not know", ["fixed", "deadline"] + nl, 100)
    write("var-multiissue", "S6", "price + delivery + warranty with private opposed points tables", ["fixed", "multiissue"] + nl, 100)
    write("var-item", "S7", "real AmazonHistoryPrice product; c and v around its reference price", ["item"] + nl, 100)
    write("var-quality", "S8", "S7 + hidden condition known only to the seller", ["item", "quality"] + nl, 100)
    write("var-currency-usd", "S9", "S7 in USD (arm 1 of 3, shared seeds)", ["item"] + nl, 60)
    write("var-currency-idrmkt", "S9", "S7 in IDR at the market rate (arm 2 of 3, shared seeds)", ["item", "currency_idrmkt"] + nl, 60)
    write("var-currency-idrppp", "S9", "S7 in IDR at the PPP-adjusted price (arm 3 of 3, shared seeds)", ["item", "currency_idrppp"] + nl, 60)


LANGS = ["en", "id", "ar", "ja", "es"]


def stage_b(variants, cut_b2=False, seed_start=1001):
    for l in LANGS:
        write(f"lang-diag-{l}", "B1", f"both seats speak {l}", variants, 100, (l, l), seed_start)
    for b in LANGS:
        for s in LANGS:
            if b != s and (not cut_b2 or "en" in (b, s)):
                write(f"lang-cross-b{b}-s{s}", "B2", f"buyer speaks {b}, seller speaks {s}", variants, 60, (s, b), seed_start)


if __name__ == "__main__":
    if sys.argv[1] == "stageA":
        stage_a(sys.argv[sys.argv.index("--noleak") + 1] == "1")
    else:
        stage_b(sys.argv[sys.argv.index("--variants") + 1].split(","), "--cut-b2" in sys.argv)
