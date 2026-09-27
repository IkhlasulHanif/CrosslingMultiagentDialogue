"""S5: asymmetric time pressure. One seat (random) loses 5% of its payoff per round; the other does not know."""
import math
from arena_plus import i18n
from arena_plus.engine import rng
from arena_plus.variants._checks import COMMON

DECAY = 0.05


def sample(seed):
    return {"pressured": rng(seed, "deadline").choice(["seller", "buyer"])}


def prompt_fragments(params, seat):
    if seat != params["pressured"]:
        return ""
    return i18n.frag(params, seat, "deadline")


def score(g, p):
    rounds = math.ceil(g["n_turns"] / 2)
    f = (1 - DECAY) ** rounds
    out = {"rounds": rounds, "pressured": p["pressured"]}
    if g["deal"] and isinstance(g["price"], int):
        out["payoff_seller"] = (g["price"] - p["c"]) * (f if p["pressured"] == "seller" else 1)
        out["payoff_buyer"] = (p["v"] - g["price"]) * (f if p["pressured"] == "buyer" else 1)
    return out


def pressure_leaked_to_other(g, p):
    other = "buyer" if p["pressured"] == "seller" else "seller"
    return i18n.appears(g["system_prompts"][other], "deadline")


CHECKS = COMMON + [("pressure_leaked_to_other", pressure_leaked_to_other)]
