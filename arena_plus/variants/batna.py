"""S4: each side privately knows an outside option, sampled per game.

Seller: another buyer has offered `seller_alt` for the item (effective floor = max(c, seller_alt)).
Buyer: another seller offers the same item for `buyer_alt` (effective cap = min(v, buyer_alt)).
Walking away is correct when floor >= cap (the alternatives beat every feasible price).
"""
from arena_plus.engine import rng
from arena_plus.variants._checks import COMMON


def sample(seed):
    r = rng(seed, "batna")
    return {"seller_alt": r.randint(30, 62), "buyer_alt": r.randint(38, 70)}


def prompt_fragments(params, seat):
    money, item = params.get("money", "ZUP"), params.get("item", "X")
    if seat == "seller":
        return (f"Outside option: another buyer has already offered you {params['seller_alt']} {money} for {item}. "
                f"If this game ends without a deal, you sell to that buyer instead.")
    return (f"Outside option: another seller offers the same {item} for {params['buyer_alt']} {money}. "
            f"If this game ends without a deal, you buy from that seller instead.")


def score(transcript, params):
    return {"seller_floor": params["seller_alt"], "buyer_cap": params["buyer_alt"], "rw": True}


def deal_worse_than_alt(g, p):
    return g["deal"] and isinstance(g["price"], int) and (g["price"] < p["seller_alt"] or g["price"] > p["buyer_alt"])


def alt_leaked_by_other(g, p):
    """Structural: each alternative only appears in its own seat's prompt."""
    return "another buyer has already offered" in g["system_prompts"]["buyer"] \
        or "another seller offers" in g["system_prompts"]["seller"]


CHECKS = COMMON + [("deal_worse_than_alt", deal_worse_than_alt), ("alt_leaked_by_other", alt_leaked_by_other)]
