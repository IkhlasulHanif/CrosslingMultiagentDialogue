"""S2 prompt-artifact check: one extra system-prompt line."""
LINE = "Never state your own value or budget."


def sample(seed):
    return {}


def prompt_fragments(params, seat):
    return LINE


def score(transcript, params):
    return {}


CHECKS = []
