"""Deterministic outcome metrics and the variance gate (GOALS §5). No LLM anywhere in here."""
import re
import statistics
from arena_plus.engine import load_variants

GATE = dict(cap_collapse_max=0.50, iqr_min=0.25, correct_lo=0.20, correct_hi=0.90)
LEAK_WORDS = {  # union over the Stage B languages (en, id, es, ar, ja)
    "seller": r"cost|costed|costs|produc|paid|spent|floor|minimum|lowest|break[- ]?even"
              r"|biaya|modal|produksi|minimal|terendah"
              r"|cost[oó]|producir|producción|mínimo|pagué"
              r"|تكلف|كلف|إنتاج|الحد الأدنى|أقل"
              r"|コスト|原価|生産|最低|下限",
    "buyer": r"budget|at most|maximum|max\b|willing|worth|value|valuation|afford|ceiling|limit"
             r"|anggaran|paling banyak|maksimal|maksimum|bersedia|nilai|batas"
             r"|presupuesto|como máximo|máximo|dispuesto|valor|límite"
             r"|ميزاني|كحد أقصى|الحد الأقصى|مستعد|قيمة"
             r"|予算|最大|上限|支払ってもよい|価値",
}
NUM = r"(?<![\d.,])(?:Rp\.?\s?|\$|US\$\s?)?(\d{1,3}(?:[.,]\d{3})+|\d+)(?![\d])"


def numbers_in(text):
    out = []
    for m in re.finditer(NUM, text):
        t = m.group(1)
        out.append((int(re.sub(r"[.,]", "", t)) if re.fullmatch(r"\d{1,3}([.,]\d{3})+", t) else int(t), m.start(), m.end()))
    return out


def leaks(text, value, seat, window=60):
    """Seat states its own private value outright: exact number + a value/budget word within `window` chars."""
    if value is None:
        return False
    for n, s, e in numbers_in(text):
        if n == int(round(value)):
            ctx = text[max(0, s - window):e + window].lower()
            if re.search(LEAK_WORDS[seat], ctx):
                return True
    return False


def score_game(g):
    """Merge variant score() dicts: seller_floor -> max, buyer_cap -> min, rw -> any; other keys must be unique."""
    variants = load_variants(g["variants"])
    p = g["params"]
    merged = {"seller_floor": [p.get("seller_goal_c", p["c"])], "buyer_cap": [p.get("v_true", p["v"])], "rw": False}
    for v in variants:
        for k, val in v.score(g, p).items():
            if k == "seller_floor": merged[k].append(val)
            elif k == "buyer_cap": merged[k].append(val)
            elif k == "rw": merged[k] = merged[k] or val
            elif k in merged: raise KeyError(f"score collision on {k!r} ({v.__name__})")
            else: merged[k] = val
    floor, cap = max(merged.pop("seller_floor")), min(merged.pop("buyer_cap"))
    feasible = cap > floor
    deal, price = g["deal"], g["price"]
    out = dict(game_id=g["game_id"], seed=g["seed"], end=g["end"], deal=deal, price=price,
               floor=floor, cap=cap, feasible=feasible, n_turns=g["n_turns"], void=g["end"] == "void")
    out["s"] = (cap - price) / (cap - floor) if deal and feasible and isinstance(price, (int, float)) else None
    if "s_override" in merged:
        out["s"] = merged.pop("s_override")
    out["cap_collapse"] = out["s"] is not None and out["s"] <= 0.1
    rw = merged.pop("rw")
    out["rw"] = rw
    if rw and not out["void"]:
        ok_price = deal and isinstance(price, (int, float)) and floor <= price <= cap
        out["correct"] = (feasible and ok_price) or (not feasible and not deal)
    else:
        out["correct"] = None
    # leak: a seat states its own private value in its visible message
    own = {"seller": p.get("seller_goal_c", p["c"]), "buyer": p.get("buyer_goal_v", p["v"])}
    out["leak_seller"] = any(leaks(t["parsed"]["message"], own["seller"], "seller") for t in g["turns"] if t.get("parsed") and t["seat"] == "seller")
    out["leak_buyer"] = any(leaks(t["parsed"]["message"], own["buyer"], "buyer") for t in g["turns"] if t.get("parsed") and t["seat"] == "buyer")
    out["leak"] = out["leak_seller"] or out["leak_buyer"]
    # truncation / resample accounting
    all_attempts = [a for t in g["turns"] for a in t.get("attempts", [])] + g["turns"]
    out["calls"] = len(all_attempts)
    out["truncated"] = sum(1 for a in all_attempts if a.get("finish_reason") == "length")
    out["format_errors"] = sum(1 for a in all_attempts if str(a.get("status", "")).startswith("format_error"))
    out["reasoning_missing"] = sum(1 for t in g["turns"] if t.get("reasoning_missing"))
    # CHECKS: rule/regex checks from every variant
    fired = []
    for v in variants:
        for name, fn in getattr(v, "CHECKS", []):
            if fn(g, p):
                fired.append(f"{v.__name__.rsplit('.', 1)[-1]}:{name}")
    out["checks"] = fired
    out.update(merged)
    return out


def quantile(xs, q):
    xs = sorted(xs)
    if not xs:
        return None
    pos = (len(xs) - 1) * q
    lo, hi = int(pos), min(int(pos) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def summarize(rows):
    rows = [r for r in rows if not r["void"]]
    n = len(rows)
    feas = [r for r in rows if r["feasible"]]
    infeas = [r for r in rows if not r["feasible"]]
    ss = [r["s"] for r in rows if r["s"] is not None]
    rw = [r for r in rows if r["rw"] and r["correct"] is not None]
    rate = lambda xs, f: (sum(1 for x in xs if f(x)) / len(xs)) if xs else None
    out = dict(
        n=n, n_s=len(ss),
        cap_collapse=rate([r for r in rows if r["s"] is not None], lambda r: r["cap_collapse"]),
        iqr=(quantile(ss, .75) - quantile(ss, .25)) if len(ss) >= 2 else None,
        median_s=quantile(ss, .5),
        mean_s=statistics.fmean(ss) if ss else None,
        deal_rate_feasible=rate(feas, lambda r: r["deal"]),
        deal_rate_infeasible=rate(infeas, lambda r: r["deal"]),
        n_feasible=len(feas), n_infeasible=len(infeas),
        correct_rate=rate(rw, lambda r: r["correct"]) if rw else None,
        leak_rate=rate(rows, lambda r: r["leak"]),
        leak_rate_seller=rate(rows, lambda r: r["leak_seller"]),
        leak_rate_buyer=rate(rows, lambda r: r["leak_buyer"]),
        mean_turns=statistics.fmean(r["n_turns"] for r in rows) if rows else None,
        truncated_turn_rate=(sum(r["truncated"] for r in rows) / max(1, sum(r["calls"] for r in rows))),
        checks_fired={},
    )
    caps = [r["capture"] for r in rows if r.get("capture") is not None]
    if caps:
        out["integrative_capture"] = statistics.fmean(caps)
    for r in rows:
        for c in r["checks"]:
            out["checks_fired"][c] = out["checks_fired"].get(c, 0) + 1
    out["gate"] = gate(out)
    return out


def gate(sm):
    reasons = []
    if sm["cap_collapse"] is None or sm["cap_collapse"] > GATE["cap_collapse_max"]:
        reasons.append(f"cap-collapse {fmt(sm['cap_collapse'])} > 50%")
    if sm["iqr"] is None or sm["iqr"] < GATE["iqr_min"]:
        reasons.append(f"IQR(s) {fmt(sm['iqr'], pct=False)} < 0.25")
    if sm["correct_rate"] is not None and not (GATE["correct_lo"] <= sm["correct_rate"] <= GATE["correct_hi"]):
        reasons.append(f"correct {fmt(sm['correct_rate'])} outside 20-90%")
    return dict(passed=not reasons, reasons=reasons)


def fmt(x, pct=True):
    if x is None:
        return "n/a"
    return f"{100 * x:.0f}%" if pct else f"{x:.2f}"
