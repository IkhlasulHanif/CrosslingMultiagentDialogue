"""Baseline valuation: upstream buy-sell, seller cost 40, buyer value 60 (runner/buysell_main.py)."""
from arena_plus.variants._checks import COMMON


def sample(seed):
    return {"c": 40, "v": 60}


def prompt_fragments(params, seat):
    return ""


def score(transcript, params):
    return {}


CHECKS = COMMON
