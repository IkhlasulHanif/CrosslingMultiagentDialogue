"""Offline checks: determinism, composition, parsing, scoring on synthetic transcripts (no API calls)."""
from arena_plus import protocol as P
from arena_plus.engine import load_variants, merge_params, system_prompt
from arena_plus.metrics import score_game, leaks, summarize

RUNS = [["fixed"], ["fixed", "noleak"], ["zopa"], ["fixed", "batna"], ["fixed", "deadline"], ["fixed", "multiissue"]]


def fake_game(variants, seed, price, end="accept", red_extra=None):
    vs = load_variants(variants)
    p = merge_params(vs, seed)
    money = p.get("money", "ZUP")
    red = {p.get("item", "X"): 1, **(red_extra or {})}
    trade = {"RED": red, "BLUE": {money: price}} if price is not None else None
    msg = "Deal."
    turns = [dict(turn=1, seat="seller", status="ok", finish_reason="stop", content="", reasoning="",
                  parsed=dict(answer="PROPOSAL", trade=trade, message=msg))]
    return dict(game_id=f"t-{seed:04d}", run="t", seed=seed, variants=variants, params=p,
                system_prompts={s: system_prompt(p, s, vs) for s in ("seller", "buyer")},
                end=end, deal=end == "accept", price=price if end == "accept" else None,
                accepted_trade=trade if end == "accept" else None, proposer="seller", n_turns=2, turns=turns)


def test_determinism_and_collisions():
    for names in RUNS:
        vs = load_variants(names)
        assert merge_params(vs, 11) == merge_params(vs, 11)
    try:
        merge_params(load_variants(["fixed", "zopa"]), 1); raise AssertionError("no collision")
    except KeyError:
        pass


def test_private_info():
    for names in RUNS:
        for seed in range(1, 30):
            g = fake_game(names, seed, 50)
            fired = score_game(g)["checks"]
            assert not any("crossed" in c or "leaked" in c for c in fired), (names, seed, fired)


def test_parse():
    r = P.parse_reply("<player answer> PROPOSAL </player answer>\n<newly proposed trade> Player RED Gives X: 1 | Player BLUE Gives ZUP: 1.640.000 </newly proposed trade>\n<message> hi </message")
    assert r["trade"]["BLUE"]["ZUP"] == 1640000 and r["message"] == "hi"
    r = P.parse_reply("<player answer> ACCEPT </player answer><newly proposed trade> NONE </newly proposed trade><message>ok</message>")
    assert r["answer"] == "ACCEPT" and r["trade"] is None
    r = P.parse_reply("<player answer>PROPOSAL</player answer><newly proposed trade>Player RED Gives X: 1, delivery: fast, warranty: none | Player BLUE Gives ZUP: 52</newly proposed trade><message>m</message>")
    assert r["trade"]["RED"]["delivery"] == "fast"


def test_scoring():
    s = score_game(fake_game(["fixed"], 1, 58))
    assert abs(s["s"] - 0.1) < 1e-9 and s["cap_collapse"] and s["correct"] is None
    z = [score_game(fake_game(["zopa"], seed, None, end="reject")) for seed in range(1, 40)]
    assert all(r["correct"] == (not r["feasible"]) for r in z)
    m = score_game(fake_game(["fixed", "multiissue"], 1, 50, red_extra={"delivery": "fast", "warranty": "none"}))
    assert m["capture"] == 1.0
    assert leaks("My budget is 60, sorry", 60, "buyer") and not leaks("I offer 60", 60, "buyer")
    assert leaks("biaya produksi saya Rp 1.600.000", 1600000, "seller")
    summarize([s, m])


if __name__ == "__main__":
    test_determinism_and_collisions(); test_private_info(); test_parse(); test_scoring(); print("variants ok")
