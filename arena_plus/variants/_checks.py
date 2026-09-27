"""Rule checks shared by every valuation variant (CHECKS lists reuse these)."""
from arena_plus import protocol as P
from arena_plus.metrics import leaks


def price_out_of_bounds(g, p):
    return g["deal"] and isinstance(g["price"], int) and not (p["c"] <= g["price"] <= p["v"])


def buyer_states_max(g, p):
    v = p.get("buyer_goal_v", p["v"])
    return any(leaks(t["parsed"]["message"], v, "buyer") for t in g["turns"] if t.get("parsed") and t["seat"] == "buyer")


def seller_states_cost(g, p):
    c = p.get("seller_goal_c", p["c"])
    return any(leaks(t["parsed"]["message"], c, "seller") for t in g["turns"] if t.get("parsed") and t["seat"] == "seller")


def private_info_crossed(g, p):
    """Structural: a seat's system prompt must not contain the other seat's goal line."""
    item, money = p.get("item", "X"), p.get("money", P.MONEY_TOKEN)
    sg = P.seller_goal(p.get("seller_goal_c", p["c"]), item, money)
    bg = P.buyer_goal(p.get("buyer_goal_v", p["v"]), item, money)
    return sg in g["system_prompts"]["buyer"] or bg in g["system_prompts"]["seller"]


def odd_trade(g, p):
    """Accepted trade where RED does not hand over exactly one unit of the item."""
    t = g.get("accepted_trade")
    return bool(t) and t["RED"].get(p.get("item", "X")) != 1


def void_game(g, p):
    return g["end"] == "void"


COMMON = [("price_out_of_bounds", price_out_of_bounds), ("buyer_states_max", buyer_states_max),
          ("seller_states_cost", seller_states_cost), ("private_info_crossed", private_info_crossed),
          ("odd_trade", odd_trade), ("void_game", void_game)]
