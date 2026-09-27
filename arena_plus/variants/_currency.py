"""Shared conversion for the IDR arms of S9 (configs/fx.toml). Amounts rounded to the nearest IDR 1,000."""
import tomllib
from pathlib import Path

FX = tomllib.loads((Path(__file__).resolve().parents[2] / "configs" / "fx.toml").read_text())
KEYS = ("c", "v", "hist_low", "hist_high", "ref_price")


def to_idr(p, rate):
    out = {k: int(round(p[k] * rate, -3)) for k in KEYS}
    out["money"] = "IDR"
    out["buyer_money"] = int(round(out["v"] * 1000 / 60, -3))
    out["idr_rate"] = rate
    return out
