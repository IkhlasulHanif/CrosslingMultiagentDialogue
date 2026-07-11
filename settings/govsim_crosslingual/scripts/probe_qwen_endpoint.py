#!/usr/bin/env python3
"""Probe the configured local/Modal Qwen endpoint and write a JSON artifact."""

from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = ROOT / "code"
sys.path.insert(0, str(CODE_DIR))

from endpoint_probe import probe_endpoint  # noqa: E402


def main() -> int:
    result, path = probe_endpoint(
        ROOT,
        timeout_s=float(os.environ.get("GOVSIM_ENDPOINT_PROBE_TIMEOUT_S", "2")),
    )
    print(path.relative_to(ROOT))
    return 0 if result["endpoint_reachable"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
