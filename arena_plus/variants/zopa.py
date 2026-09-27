"""S3: seller cost c and buyer value v sampled per game; in 25% of games v < c (no deal possible)."""
from arena_plus.engine import rng
from arena_plus.variants._checks import COMMON

P_INFEASIBLE = 0.25


def sample(seed):
    r = rng(seed, "zopa")
    c = r.randint(20, 60)
    if r.random() < P_INFEASIBLE:
        v = c - r.randint(2, 15)
    else:
        v = c + r.randint(5, 40)
    return {"c": c, "v": v}


def prompt_fragments(params, seat):
    return ""


def score(transcript, params):
    return {"rw": True}


def deal_when_impossible(g, p):
    return g["deal"] and p["v"] < p["c"]


CHECKS = COMMON + [("deal_when_impossible", deal_when_impossible)]
