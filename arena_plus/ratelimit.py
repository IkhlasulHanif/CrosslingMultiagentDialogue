"""Cross-process request limiter for the IFM per-minute request guard (429 "Request rate limit exceeded").

Every engine call to k2.chat first takes a slot: at most RPM calls started in any rolling 60 s window, shared by
all runner processes through a lock file. Keeps retries (and their backoff sleeps) rare.
"""
import fcntl
import json
import os
import time
from pathlib import Path

RPM = int(os.environ.get("K2_RPM", "12"))
F = Path(__file__).resolve().parents[1] / "logs" / ".ratelimit.json"


def acquire():
    F.parent.mkdir(exist_ok=True)
    while True:
        with open(F, "a+") as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            fh.seek(0)
            try:
                ts = json.loads(fh.read() or "[]")
            except json.JSONDecodeError:
                ts = []
            now = time.time()
            ts = [t for t in ts if now - t < 60]
            if len(ts) < RPM:
                ts.append(now)
                fh.seek(0); fh.truncate(); fh.write(json.dumps(ts))
                return
            wait = 60 - (now - ts[0]) + 0.05
        time.sleep(max(wait, 0.2))
