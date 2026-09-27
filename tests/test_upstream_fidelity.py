"""Static check: our prompt template equals the upstream f-string body (upstream is read as text, never executed)."""
import re
from pathlib import Path
from arena_plus.protocol import TEMPLATE, CONST

UP = Path(__file__).resolve().parents[1] / "vendor/NegotiationArena"


def test_template_matches_upstream():
    src = (UP / "games/buy_sell_game/prompt.py").read_text()
    body = src.split('prompt = f"""', 1)[1].split('"""', 1)[0]
    assert body == TEMPLATE


def test_constants_match_upstream():
    src = (UP / "negotiationarena/constants.py").read_text()
    up = dict(re.findall(r'^(\w+) = "(.*)"$', src, re.M))
    for k, v in CONST.items():
        assert up[k] == v, k


if __name__ == "__main__":
    test_template_matches_upstream(); test_constants_match_upstream(); print("fidelity ok")
