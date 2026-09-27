"""S7: the abstract item becomes a sampled AmazonHistoryPrice product (data/items.jsonl).

Both seats see its name, category and public historical price range (lowest / highest). Seller cost c and buyer
value v are sampled around the reference (average) price: c = ref x U(0.55, 0.85), v = ref x U(1.00, 1.30), so every
game stays feasible, as in the baseline. Prices are in USD (the money token of the trade format).
"""
import json
from pathlib import Path
from arena_plus import i18n
from arena_plus.engine import rng
from arena_plus.variants._checks import COMMON

ITEMS = [json.loads(l) for l in (Path(__file__).resolve().parents[2] / "data" / "items.jsonl").read_text().splitlines()]


def sample(seed):
    r = rng(seed, "item")
    it = r.choice(ITEMS)
    ref = it["ref_price"]
    c = round(ref * r.uniform(0.55, 0.85))
    v = max(c + 1, round(ref * r.uniform(1.00, 1.30)))
    return {"item_id": it["id"], "item_name": it["name"], "category": it["category"], "ref_price": ref,
            "hist_low": it["hist_low"], "hist_high": it["hist_high"], "c": c, "v": v, "money": "USD",
            "buyer_money": int(round(v * 1000 / 60, -1))}


def money_str(x, money):
    if money == "USD":
        return f"${x:,.2f}" if x != int(x) else f"${int(x):,}"
    return f"{money} {int(round(x)):,}"


def prompt_fragments(params, seat):
    m = params["money"]
    return i18n.frag(params, seat, "item", name=params["item_name"], category=params["category"],
                     low=money_str(params["hist_low"], m), high=money_str(params["hist_high"], m), money=m)


def score(transcript, params):
    return {}


CHECKS = COMMON
