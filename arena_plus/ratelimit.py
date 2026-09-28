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


# ---- rolling 24 h token quota (IFM counts the 10M/day cap over a rolling window, observed 2026-09-28) ----
QUOTA_SOFT = int(os.environ.get("K2_QUOTA_SOFT", "9500000"))
LOG = Path(__file__).resolve().parents[1] / "logs" / "api_calls.jsonl"
_cache = {"t": 0.0, "used": 0, "oldest": []}


def tokens_last_24h():
    now = time.time()
    if now - _cache["t"] > 30:   # re-read the log at most every 30 s
        used, recent = 0, []
        if LOG.exists():
            for line in LOG.read_text().splitlines():
                r = json.loads(line)
                if now - r["ts"] < 86400:
                    n = r["prompt_tokens"] + r["completion_tokens"]
                    used += n; recent.append((r["ts"], n))
        _cache.update(t=now, used=used, oldest=sorted(recent))
    return _cache["used"]


def wait_for_quota():
    """Block while the rolling-24h token count is above QUOTA_SOFT; resume as old calls roll out of the window."""
    while (used := tokens_last_24h()) > QUOTA_SOFT:
        print(f"[quota] {used:,} tokens in the last 24 h > {QUOTA_SOFT:,}; waiting", flush=True)
        _cache["t"] = 0
        time.sleep(300)
