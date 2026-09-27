"""Print the visible exchange, params, parsed price and fired CHECKS for smoke seeds (for reading SMOKE transcripts)."""
import json
import sys
from arena_plus.casebook import exchange
from arena_plus.metrics import score_game
from arena_plus.run import load_games

run, n = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 5
for g in sorted(load_games(run), key=lambda g: g["seed"])[:n]:
    r = score_game(g)
    extra = {k: r[k] for k in r if k in ("correct", "s", "capture", "rounds", "delivery", "warranty")}
    print(f"=== {g['game_id']} params={json.dumps(g['params'], ensure_ascii=False)} end={g['end']} price={g['price']} {extra} checks={r['checks']}")
    for s in ("seller", "buyer"):
        tail = g["system_prompts"][s].split("Please be sure to include all.")[-1].strip()
        if tail:
            print(f"  [{s} prompt tail] {tail}")
    print(exchange(g)); print()
