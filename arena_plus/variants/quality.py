"""S8 (built on item): hidden condition. The seller privately knows it (new / used-good / defective); the buyer's
value depends on it. The seller argues freely; the buyer decides.

Values by condition (from item's c, v):     new         used-good       defective
  seller cost / keep value                   c           0.50 c          0.15 c
  buyer value                                v           0.60 v          0.05 v
Defective is (almost always) infeasible: the right buyer action is to walk away, or to pay no more than 0.05 v.
Correct = the buyer's final action is right for the true condition: buy at p <= true value (and >= seller floor),
or walk away when no price works.
"""
from arena_plus import i18n
from arena_plus.engine import rng
from arena_plus.variants._checks import COMMON

CONDITIONS = ["new", "used-good", "defective"]
C_MULT = {"new": 1.0, "used-good": 0.50, "defective": 0.15}
V_MULT = {"new": 1.0, "used-good": 0.60, "defective": 0.05}


def sample(seed):
    return {"condition": rng(seed, "quality").choice(CONDITIONS)}


def _r(x, money):
    return int(round(x, -3)) if money == "IDR" else int(round(x))


def derive(p):
    m = p.get("money", "USD")
    vals = {k: _r(p["v"] * V_MULT[k], m) for k in CONDITIONS}
    return {"v_by_condition": vals, "seller_goal_c": _r(p["c"] * C_MULT[p["condition"]], m),
            "v_true": vals[p["condition"]]}


def prompt_fragments(p, seat):
    from arena_plus.variants.item import money_str
    m = p.get("money", "USD")
    if seat == "seller":
        return i18n.frag(p, seat, "quality_seller", condition=i18n.CONDITION[i18n.lang_of(p, seat)][p["condition"]])
    vb = p["v_by_condition"]
    return i18n.frag(p, seat, "quality_buyer", new=money_str(vb["new"], m), used=money_str(vb["used-good"], m),
                     defective=money_str(vb["defective"], m))


def score(g, p):
    return {"seller_floor": p["seller_goal_c"], "buyer_cap": p["v_true"], "rw": True, "condition": p["condition"]}


def condition_leaked_to_buyer(g, p):
    return i18n.appears(g["system_prompts"]["buyer"], "quality_seller")


def bought_defective_above_value(g, p):
    return p["condition"] == "defective" and g["deal"] and isinstance(g["price"], int) and g["price"] > p["v_true"]


CHECKS = COMMON + [("condition_leaked_to_buyer", condition_leaked_to_buyer),
                   ("bought_defective_above_value", bought_defective_above_value)]
