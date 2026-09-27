"""Build data/items.jsonl from AmazonHistoryPrice (Xia et al. 2024, arXiv 2402.15813).

Source: github.com/TianXiaSJTU/AmazonPriceHistory @ 834ad9066d0627f0332504d5fa6d236706f2402b, data/AmazonHistoryPrice/*.json
Keeps products with 20 <= average price <= 2000 USD and lowest < highest. Fields: id, name, category, ref_price
(camelcamelcamel average), hist_low, hist_high, asin link.
"""
import json
import re
from pathlib import Path

D = Path(__file__).resolve().parent
money = lambda s: float(s.replace("$", "").replace(",", ""))


def short(title):
    t = re.split(r"\s[|,–-]\s|, ", title)[0].strip()
    return t if len(t) <= 90 else t[:87].rsplit(" ", 1)[0] + "..."


rows = []
for f in sorted((D / "AmazonHistoryPrice").glob("*.json")):
    for r in json.loads(f.read_text()):
        try:
            ref, lo, hi = money(r["average_price"]), money(r["lowest_price"]), money(r["highest_price"])
        except ValueError:
            continue
        if 20 <= ref <= 2000 and lo < hi:
            rows.append(dict(name=short(r["title"]), category=r["category"], ref_price=round(ref, 2),
                             hist_low=round(lo, 2), hist_high=round(hi, 2), link=r["amazon_link"]))
rows.sort(key=lambda r: (r["category"], r["name"]))
seen, out = set(), []
for r in rows:
    if r["name"] not in seen:
        seen.add(r["name"]); out.append({"id": len(out), **r})
(D / "items.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out))
print(f"{len(out)} items")
