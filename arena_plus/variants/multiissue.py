"""S6: price + delivery + warranty, private points tables with opposed priorities.

Points (no deal = 0 points for both):
  seller: (price - 40)  + warranty {none: 12, 1yr: 6, 2yr: 0} + delivery {slow: 4, standard: 2, fast: 0}
  buyer:  (60 - price)  + delivery {fast: 12, standard: 6, slow: 0} + warranty {2yr: 4, 1yr: 2, none: 0}
Price points are constant-sum (20). Warranty matters most to the seller, delivery to the buyer, so the
integrative package is (fast delivery, no warranty):
  max joint = 20 + max_w(seller_w + buyer_w) + max_d(seller_d + buyer_d) = 20 + 12 + 12 = 44.
Integrative capture = joint points achieved / 44. Buyer share s = buyer points / joint points.
"""
from arena_plus.variants._checks import COMMON

SELLER_W = {"none": 12, "1yr": 6, "2yr": 0}
SELLER_D = {"slow": 4, "standard": 2, "fast": 0}
BUYER_D = {"fast": 12, "standard": 6, "slow": 0}
BUYER_W = {"2yr": 4, "1yr": 2, "none": 0}
MAX_JOINT = 20 + max(SELLER_W[w] + BUYER_W[w] for w in SELLER_W) + max(SELLER_D[d] + BUYER_D[d] for d in SELLER_D)
assert MAX_JOINT == 44


def sample(seed):
    return {"issues": ["price", "delivery", "warranty"]}


FORMAT = ("This deal has three issues: price, delivery (fast / standard / slow) and warranty (none / 1yr / 2yr). "
          "Every proposal must state all three, in this exact trade format:\n"
          "Player RED Gives X: 1, delivery: <fast|standard|slow>, warranty: <none|1yr|2yr> | Player BLUE Gives {money}: amount\n")


def prompt_fragments(params, seat):
    money = params.get("money", "ZUP")
    head = FORMAT.format(money=money)
    if seat == "seller":
        return head + ("Your private points table (the other player has its own, different table): "
                       "price: (price - 40) points; warranty: none = 12, 1yr = 6, 2yr = 0; "
                       "delivery: slow = 4, standard = 2, fast = 0. No deal gives you 0 points. Maximize your points.")
    return head + ("Your private points table (the other player has its own, different table): "
                   "price: (60 - price) points; delivery: fast = 12, standard = 6, slow = 0; "
                   "warranty: 2yr = 4, 1yr = 2, none = 0. No deal gives you 0 points. Maximize your points.")


def _norm(val, allowed, default):
    t = str(val).strip().lower().replace(" ", "")
    t = {"1year": "1yr", "2years": "2yr", "2year": "2yr", "oneyear": "1yr", "twoyears": "2yr", "no": "none"}.get(t, t)
    return (t, False) if t in allowed else (default, True)


def terms(g):
    t = g["accepted_trade"]["RED"]
    d, dm = _norm(t.get("delivery", ""), BUYER_D, "standard")
    w, wm = _norm(t.get("warranty", ""), SELLER_W, "1yr")
    return d, w, dm or wm


def score(g, p):
    if not (g["deal"] and isinstance(g["price"], int)):
        return {"capture": 0.0 if g["end"] != "void" else None, "points_seller": 0, "points_buyer": 0}
    d, w, missing = terms(g)
    sp = (g["price"] - 40) + SELLER_W[w] + SELLER_D[d]
    bp = (60 - g["price"]) + BUYER_D[d] + BUYER_W[w]
    joint = sp + bp
    return {"capture": joint / MAX_JOINT, "points_seller": sp, "points_buyer": bp, "delivery": d, "warranty": w,
            "terms_missing": missing, "s_override": (bp / joint) if joint > 0 else None}


def missing_terms(g, p):
    return g["deal"] and bool(g.get("accepted_trade")) and terms(g)[2]


def table_crossed(g, p):
    return "(60 - price)" in g["system_prompts"]["seller"] or "(price - 40)" in g["system_prompts"]["buyer"]


CHECKS = COMMON + [("missing_terms", missing_terms), ("table_crossed", table_crossed)]
