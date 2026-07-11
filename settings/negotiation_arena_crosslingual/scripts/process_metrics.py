#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from negotiation_arena_crosslingual.process_metrics import main  # noqa: E402

if __name__ == "__main__":
    os.chdir(ROOT)
    result = main()
    sys.exit(0 if result is None else int(result))
