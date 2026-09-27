"""S2 prompt-artifact check: one extra system-prompt line."""
from arena_plus import i18n

LINE = i18n.FRAG["noleak"]["en"]


def sample(seed):
    return {}


def prompt_fragments(params, seat):
    return i18n.frag(params, seat, "noleak")


def score(transcript, params):
    return {}


CHECKS = []
