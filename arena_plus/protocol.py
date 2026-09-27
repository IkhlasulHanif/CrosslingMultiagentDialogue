"""Upstream buy-sell protocol, reproduced as data.

The prompt template below is the body of `buy_sell_prompt` in
vendor/NegotiationArena/games/buy_sell_game/prompt.py, character for character.
Upstream code is never executed (sandbox policy on externally fetched code, see DEVIATIONS.md);
`tests/test_upstream_fidelity.py` compares this template against the upstream file text.
"""
import re

# negotiationarena/constants.py
MONEY_TOKEN = "ZUP"
RESOURCES_TAG = "my resources"
GOALS_TAG = "my goals"
REASONING_TAG = "reason"
PLAYER_ANSWER_TAG = "player answer"
PROPOSED_TRADE_TAG = "newly proposed trade"
MESSAGE_TAG = "message"
REFUSING_OR_WAIT_TAG = "NONE"
ACCEPTING_TAG = "ACCEPT"
REJECTION_TAG = "REJECT"
PROPOSAL_COUNT_TAG = "proposal count"
AGENT_ONE = "Player RED"   # seller
AGENT_TWO = "Player BLUE"  # buyer

TEMPLATE = '''You are playing game where you are buying or selling an object. There is only one object for sale/purcahse.

{AGENT_ONE} is going to sell one object. {AGENT_TWO} gives {MONEY_TOKEN} to buy resources.

RULES:

```
1. You must always respond with:

    A) Propose a trade with (you can only trade in integer amounts, not decimals):
    <{PLAYER_ANSWER_TAG}> PROPOSAL </{PLAYER_ANSWER_TAG}>
    <{PROPOSED_TRADE_TAG}> {AGENT_ONE} Gives {resources_available_in_game}: amount, ...| {AGENT_TWO} Gives {MONEY_TOKEN}: amount </{PROPOSED_TRADE_TAG}>

    B) Accept the trade by saying:
    <{PLAYER_ANSWER_TAG}> {ACCEPTING_TAG} </{PLAYER_ANSWER_TAG}>
    <{PROPOSED_TRADE_TAG}> NONE </{PROPOSED_TRADE_TAG}>

    C) Reject and end the game:
    <{PLAYER_ANSWER_TAG}> {REJECTION_TAG} </{PLAYER_ANSWER_TAG}>
    <{PROPOSED_TRADE_TAG}> NONE </{PROPOSED_TRADE_TAG}>

    Note: The game will end if one of the players {ACCEPTING_TAG} OR {REJECTION_TAG}. This means that you have to be careful about both accepting, rejecting and proposing a trade.

2. You are allowed at most {maximum_number_of_proposals} proposals of your own to complete the game, after which you can only reply with {ACCEPTING_TAG} or {REJECTION_TAG}.
DO NOT propose a new trade after {maximum_number_of_proposals} proposals. Your limit for proposals is {maximum_number_of_proposals}.

3. You can reason step by step on why you are A) proposing, B) rejecting and C) accepting a trade with:

<{REASONING_TAG}> [add reasoning] </{REASONING_TAG}> add as much text as you want

This information will not be sent to the other player. It is just for you to keep track of your reasoning.

4. At each turn send messages to each other by using the following format:

<{MESSAGE_TAG}>your message here</{MESSAGE_TAG}>

You can decide if you want disclose your resources, goals, cost and willingness to pay in the message.
```

Here is what you have access to:
```
Object that is being bought/sold: {resources_available_in_game}
<{RESOURCES_TAG}> {starting_initial_resources} </{RESOURCES_TAG}>
<{GOALS_TAG}> {player_goal} </{GOALS_TAG}>,
```

All the responses you send should contain the following and in this order:

```
<{PROPOSAL_COUNT_TAG}> [add here (inclusive of current)] </{PROPOSAL_COUNT_TAG}>
<{RESOURCES_TAG}> [add here] </{RESOURCES_TAG}>
<{GOALS_TAG}> [add here] </{GOALS_TAG}>
<{REASONING_TAG}> [add here] </{REASONING_TAG}>
<{PLAYER_ANSWER_TAG}> [add here] </{PLAYER_ANSWER_TAG}>
<{PROPOSED_TRADE_TAG}> [add here] </{PROPOSED_TRADE_TAG}>
<{MESSAGE_TAG}> [add here] </{MESSAGE_TAG}
```

Please be sure to include all.

{player_social_behaviour}
'''

CONST = {k: v for k, v in globals().items() if k.isupper() and isinstance(v, str) and k != "TEMPLATE"}


def seller_goal(cost, item="X", money=MONEY_TOKEN):
    # negotiationarena/game_objects/goal.py SellerGoal + Valuation.__str__
    return f"Sell resources for <{money}>. It costed {item}: {cost} {money} to produce the resources"


def buyer_goal(value, item="X", money=MONEY_TOKEN):
    # negotiationarena/game_objects/goal.py BuyerGoal + Valuation.__str__
    return f"Buy resources with <{money}>. You are willing to pay at most {item}: {value} {money} for the resources."


def render(*, item, resources, goal, max_proposals, social="", money=MONEY_TOKEN, template=TEMPLATE):
    # Double braces in format() would be needed for literal braces; the template has none.
    return template.format(**{**CONST, "MONEY_TOKEN": money}, resources_available_in_game=item,
                           starting_initial_resources=resources, player_goal=goal,
                           maximum_number_of_proposals=max_proposals, player_social_behaviour=social)


# ---------- parsing (same semantics as upstream utils.get_tag_contents / ExchangeGameDefaultParser) ----------

def tag(response, name):
    """First <name> ... </name>, stripped; '' if absent (upstream returns garbage on absence; we return '')."""
    s, e = response.find(f"<{name}>"), response.find(f"</{name}>")
    if s < 0 or e < 0 or e < s:
        return ""
    return response[s + len(name) + 2:e].strip()


def parse_amount(tok: str):
    """Integer amount; tolerates thousands separators (1,640,000 / 1.640.000) and currency marks."""
    t = tok.strip().replace(" ", "").replace(" ", "")
    t = re.sub(r"^(Rp\.?|IDR|USD|US\$|\$)", "", t, flags=re.I)
    if re.fullmatch(r"\d{1,3}([.,]\d{3})+", t):
        t = re.sub(r"[.,]", "", t)
    if re.fullmatch(r"\d+([.,]0+)?", t):
        return int(re.split(r"[.,]", t)[0])
    if re.fullmatch(r"\d+", t):
        return int(t)
    return t  # non-numeric term (e.g. delivery: fast)


def parse_trade(text: str):
    """'Player RED Gives X: 1 | Player BLUE Gives ZUP: 55' -> {'RED': {'X': 1}, 'BLUE': {'ZUP': 55}}."""
    c = text.strip().replace("\n", " ")
    if c.upper() == REFUSING_OR_WAIT_TAG or not c:
        return None
    trade = {}
    for part in c.split("|"):
        if "Player" not in part or "Gives" not in part:
            raise ValueError(f"bad trade part: {part!r}")
        name = part.split("Player")[1].split("Gives")[0].strip().upper()
        items = {}
        for kv in part.split("Gives", 1)[1].split(","):
            if ":" not in kv:
                raise ValueError(f"bad resource: {kv!r}")
            k, v = kv.split(":", 1)
            items[k.strip()] = parse_amount(v)
        trade[name] = items
    if set(trade) != {"RED", "BLUE"}:
        raise ValueError(f"trade must name RED and BLUE: {list(trade)}")
    return trade


def trade_str(trade):
    if trade is None:
        return REFUSING_OR_WAIT_TAG
    fmt = lambda d: ", ".join(f"{k}: {v}" for k, v in d.items())
    return f"Player RED Gives {fmt(trade['RED'])} | Player BLUE Gives {fmt(trade['BLUE'])}"


def parse_reply(content: str):
    """Returns dict(answer, trade, message) or raises ValueError (format failure)."""
    answer = tag(content, PLAYER_ANSWER_TAG).upper().strip(" .*")
    message = tag(content, MESSAGE_TAG)
    if not message:  # upstream template itself has a broken closer '</message' - accept it
        m = re.search(r"<message>(.*?)(</message>?|$)", content, re.S)
        message = m.group(1).strip() if m else ""
    raw_trade = tag(content, PROPOSED_TRADE_TAG)
    raw_answer = answer
    # Upstream only tests answer == ACCEPT; any other answer carrying a trade is a proposal ("PROPOSE" etc.).
    if answer not in (ACCEPTING_TAG, REJECTION_TAG):
        answer = "PROPOSAL"
    trade = parse_trade(raw_trade) if answer == "PROPOSAL" else None
    if answer == "PROPOSAL" and trade is None:
        raise ValueError(f"no trade with answer {raw_answer!r}")
    return dict(answer=answer, trade=trade, message=message, raw_answer=raw_answer)


def public_string(parsed):
    """upstream AgentMessage.message_to_other_player: public tags in order MESSAGE, ANSWER, TRADE."""
    return "\n".join([f"<{MESSAGE_TAG}> {parsed['message']} </{MESSAGE_TAG}>",
                      f"<{PLAYER_ANSWER_TAG}> {parsed['answer']} </{PLAYER_ANSWER_TAG}>",
                      f"<{PROPOSED_TRADE_TAG}> {trade_str(parsed['trade'])} </{PROPOSED_TRADE_TAG}>"])
