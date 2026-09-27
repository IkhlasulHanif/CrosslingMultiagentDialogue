"""S9 arm: prices in IDR at the PPP-adjusted price (World Bank PPP conversion factor), from configs/fx.toml. Built on item (list after item)."""
from arena_plus.variants._currency import FX, KEYS, to_idr

OVERRIDES = KEYS + ("money", "buyer_money")


def sample(seed):
    return {}


def derive(p):
    return to_idr(p, FX["ppp"]["idr_per_intl_dollar"])


def prompt_fragments(params, seat):
    return ""


def score(transcript, params):
    return {}


CHECKS = []
