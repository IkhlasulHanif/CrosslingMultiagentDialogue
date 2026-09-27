"""Wait out an API throttle: one tiny k2.chat call every INTERVAL s until one succeeds (logged as run=throttle-probe)."""
import datetime as dt
import sys
import time
from arena_plus import k2

INTERVAL = int(sys.argv[1]) if len(sys.argv) > 1 else 300
i = 0
while True:
    i += 1
    try:
        k2.chat([{"role": "user", "content": "Reply with OK."}], run="throttle-probe", game_id=f"probe-{i}", turn=0, seat="none")
        print(f"[probe] OK at {dt.datetime.now(dt.timezone.utc):%H:%M:%S} UTC after {i} tries", flush=True)
        break
    except RuntimeError:
        print(f"[probe] still throttled at {dt.datetime.now(dt.timezone.utc):%H:%M:%S} UTC", flush=True)
        time.sleep(INTERVAL)
