"""Buy-sell game loop on top of the upstream protocol, with K2 seats (GOALS §3.3).

Seats: seller = Player RED (moves first, upstream order), buyer = Player BLUE.
Each seat keeps its own message list; assistant turns replay `reasoning_content` verbatim.
"""
import importlib
import random
import time
from arena_plus import i18n, k2, protocol as P, ratelimit

ITERATIONS = 10                       # upstream runner/buysell_main.py
MAX_PROPOSALS = ITERATIONS // 2 - 1   # upstream BuySellGame.init_players
MAX_RESAMPLE = 3                      # format failures / truncations per turn before the game is voided
SEATS = ("seller", "buyer")
ENGINE_RETRIES = 5                    # engine-level retries of a whole k2.chat call (after k2's own 6)


def load_variants(names):
    return [importlib.import_module(f"arena_plus.variants.{n}") for n in names]


def merge_params(variants, seed):
    """sample() dicts merge; a key collision raises. Optional derive(params) adds computed keys (also checked)."""
    params = {}
    for v in variants:
        for k, val in v.sample(seed).items():
            if k in params:
                raise KeyError(f"param collision on {k!r} ({v.__name__})")
            params[k] = val
    for v in variants:
        if hasattr(v, "derive"):
            for k, val in v.derive(dict(params)).items():
                if k in params and k not in getattr(v, "OVERRIDES", ()):
                    raise KeyError(f"derived param collision on {k!r} ({v.__name__})")
                params[k] = val
    if "c" not in params or "v" not in params:
        raise KeyError("no valuation variant supplied c and v")
    return params


def system_prompt(params, seat, variants):
    """Stage A: upstream English frame. Stage B (params["lang"] set): localized frame + reply-language pin."""
    item, money = params.get("item", "X"), params.get("money", P.MONEY_TOKEN)
    lang = params.get("lang", {}).get(seat)
    c, v = params.get("seller_goal_c", params["c"]), params.get("buyer_goal_v", params["v"])
    if seat == "seller":
        goal = P.seller_goal(c, item, money) if lang is None else i18n.SELLER_GOAL[lang].format(money=money, item=item, cost=c)
        resources = f"{item}: 1"
    else:
        goal = P.buyer_goal(v, item, money) if lang is None else i18n.BUYER_GOAL[lang].format(money=money, item=item, value=v)
        resources = f"{money}: {params.get('buyer_money', 1000 if money == P.MONEY_TOKEN else 10 * params['v'])}"
    render = P.render if lang is None else (lambda **kw: i18n.render(lang, **kw))
    base = render(item=item, resources=resources, goal=goal, max_proposals=MAX_PROPOSALS, money=money)
    frags = [f for f in (v.prompt_fragments(params, seat) for v in variants) if f]
    if lang is not None:
        frags.append(i18n.PIN[lang])
    text = base + ("\n" + "\n".join(frags) + "\n" if frags else "")
    if seat == "buyer":  # upstream ChatGPTAgent.init_agent: BLUE's role is appended to its system prompt
        text += f"You are {P.AGENT_TWO}." if lang is None else i18n.ROLE[lang].format(player=P.AGENT_TWO)
    return text


def _chat(messages, **kw):
    """k2.chat behind the shared rate limiter; if k2's own retries are exhausted (sustained 429s),
    wait a minute and try again with a fresh limiter slot instead of dropping the game."""
    for attempt in range(ENGINE_RETRIES):
        ratelimit.acquire()
        try:
            return k2.chat(messages, **kw)
        except RuntimeError as e:
            if isinstance(e, k2.BudgetExceeded) or attempt == ENGINE_RETRIES - 1:
                raise
            time.sleep(60)


def _reasoning(msg):
    r = getattr(msg, "reasoning_content", None)
    if r is None and msg.model_extra:
        r = msg.model_extra.get("reasoning_content", msg.model_extra.get("reasoning"))
    return r


def play(run, seed, variant_names, langs=None):
    """langs: None (Stage A, English upstream frame) or {"seller": code, "buyer": code} (Stage B)."""
    variants = load_variants(variant_names)
    params = merge_params(variants, seed)
    if langs:
        params["lang"] = dict(langs)
    game_id = f"{run}-{seed:04d}"
    msgs = {s: [{"role": "system", "content": system_prompt(params, s, variants)}] for s in SEATS}
    red_role = f"You are {P.AGENT_ONE}." if not langs else i18n.ROLE[langs["seller"]].format(player=P.AGENT_ONE)
    msgs["seller"].append({"role": "user", "content": red_role})  # upstream RED init
    turns, end, last_proposal = [], "limit", None
    for it in range(1, ITERATIONS + 1):
        seat = SEATS[(it - 1) % 2]
        attempts = []
        for attempt in range(MAX_RESAMPLE):
            msg, finish = _chat(msgs[seat], run=run, game_id=game_id, turn=it, seat=seat)
            reasoning, content = _reasoning(msg), msg.content or ""
            rec = dict(finish_reason=finish, content=content, reasoning=reasoning)
            if finish == "length":
                rec["status"] = "truncated"; attempts.append(rec); continue
            try:
                parsed = P.parse_reply(content)
                if parsed["answer"] == P.ACCEPTING_TAG and last_proposal is None:
                    raise ValueError("ACCEPT with no standing proposal")
                if parsed["answer"] == P.ACCEPTING_TAG and last_proposal["seat"] == seat:
                    raise ValueError("ACCEPT of own proposal")
            except ValueError as e:
                rec["status"] = f"format_error: {e}"; attempts.append(rec); continue
            rec["status"] = "ok"; rec["parsed"] = parsed; attempts.append(rec)
            break
        final = attempts[-1]
        turn = dict(turn=it, seat=seat, attempts=attempts[:-1], **final)
        turns.append(turn)
        if final["status"] != "ok":
            end = "void"; break
        # this seat's own turn, both fields (reasoning "" stays "", None becomes "" and is counted)
        msgs[seat].append({"role": "assistant", "content": final["content"],
                           "reasoning_content": final["reasoning"] if final["reasoning"] is not None else ""})
        turn["reasoning_missing"] = final["reasoning"] is None
        pub = P.public_string(final["parsed"])
        turn["public"] = pub
        other = SEATS[it % 2]
        msgs[other].append({"role": "user", "content": pub})
        a = final["parsed"]["answer"]
        if a == "PROPOSAL":
            last_proposal = dict(seat=seat, turn=it, trade=final["parsed"]["trade"])
        elif a == P.ACCEPTING_TAG:
            end = "accept"; break
        else:
            end = "reject"; break
    money = params.get("money", P.MONEY_TOKEN)
    price = None
    if end == "accept":
        blue = last_proposal["trade"]["BLUE"]
        price = blue.get(money, next((v for v in blue.values() if isinstance(v, int)), None))
    return dict(game_id=game_id, run=run, seed=seed, variants=variant_names, params=params,
                system_prompts={s: msgs[s][0]["content"] for s in SEATS},
                end=end, deal=end == "accept", price=price,
                accepted_trade=last_proposal["trade"] if end == "accept" else None,
                proposer=last_proposal["seat"] if end == "accept" else None,
                n_turns=len(turns), turns=turns)


def rng(seed, salt):
    """Per-variant deterministic RNG: same seed -> same params, independent across variants."""
    return random.Random(f"{salt}:{seed}")
