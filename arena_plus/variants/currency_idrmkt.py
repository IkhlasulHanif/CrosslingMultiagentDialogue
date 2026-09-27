"""S9 arm: prices in IDR at the market rate, from configs/fx.toml. Built on item (list after item)."""
from arena_plus.variants._currency import FX, KEYS, to_idr

OVERRIDES = KEYS + ("money", "buyer_money")


def sample(seed):
    return {}


def derive(p):
    return to_idr(p, FX["market"]["idr_per_usd"])


def prompt_fragments(params, seat):
    return ""


def score(transcript, params):
    return {}


CHECKS = []
