"""reports/results.html: self-contained HTML, inline SVG, no JS chart libraries (GOALS §8).

Opens with the variant table (cap-collapse, IQR(s), correct rate, pass/fail), then one section per step:
histogram of s overlaid on baseline, plain paragraph (reports/notes/<run>.md), metric table, checks fired.
Fixed colour per language everywhere (LANG_COLOR).
"""
import html
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "reports" / "results.html"
NOTES = REPO / "reports" / "notes"
BASELINE = "var-baseline"

# Stage A steps in order: (step, run(s), label). Multi-arm steps list several runs.
STAGE_A = [
    ("S0", ["s0-smoke"], "setup and cost"),
    ("S1", ["var-baseline"], "replicate the collapse"),
    ("S2", ["var-noleak"], "prompt-artifact check"),
    ("S3", ["var-zopa"], "randomized values, some deals impossible"),
    ("S4", ["var-batna"], "outside options"),
    ("S5", ["var-deadline"], "asymmetric time pressure"),
    ("S6", ["var-multiissue"], "price + delivery + warranty"),
    ("S7", ["var-item"], "real product"),
    ("S8", ["var-quality"], "hidden condition"),
    ("S9", ["var-currency-usd", "var-currency-idrmkt", "var-currency-idrppp"], "currency and numeral scale"),
    ("S10", ["grounded-v1"], "combine what passed"),
]
STAGE_B = [("B1", ["lang-diag"], "same-language pairs"), ("B2", ["lang-cross"], "buyer x seller language"),
           ("B3", ["lang-currency"], "id buyer, IDR vs USD")]

# One fixed colour per language (dataviz reference palette, slots 1-5, light / dark steps).
LANG_COLOR = {"en": ("#2a78d6", "#3987e5"), "id": ("#eb6834", "#d95926"), "ar": ("#1baf7a", "#199e70"),
              "ja": ("#eda100", "#c98500"), "es": ("#e87ba4", "#d55181")}

CSS = """
:root{--surface:#fcfcfb;--panel:#ffffff;--ink:#0b0b0b;--ink2:#52514e;--muted:#8a8984;--grid:#e6e5e0;--base:#9b9a95;
--en:#2a78d6;--id:#eb6834;--ar:#1baf7a;--ja:#eda100;--es:#e87ba4;--pass:#0a7a33;--fail:#b3261e}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--surface:#1a1a19;--panel:#222220;--ink:#fff;--ink2:#c3c2b7;
--muted:#8f8e86;--grid:#383835;--base:#77766f;--en:#3987e5;--id:#d95926;--ar:#199e70;--ja:#c98500;--es:#d55181;--pass:#4cc27a;--fail:#f07167}}
:root[data-theme="dark"]{--surface:#1a1a19;--panel:#222220;--ink:#fff;--ink2:#c3c2b7;--muted:#8f8e86;--grid:#383835;--base:#77766f;
--en:#3987e5;--id:#d95926;--ar:#199e70;--ja:#c98500;--es:#d55181;--pass:#4cc27a;--fail:#f07167}
*{box-sizing:border-box}body{margin:0;background:var(--surface);color:var(--ink);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:980px;margin:0 auto;padding:24px 16px 64px}h1{font-size:26px;margin:0 0 4px}h2{font-size:20px;margin:40px 0 6px}
h3{font-size:15px;margin:18px 0 6px;color:var(--ink2)}p{margin:6px 0 10px;max-width:72ch}.sub{color:var(--ink2)}
table{border-collapse:collapse;width:100%;font-size:13.5px;margin:8px 0}th,td{padding:6px 8px;border-bottom:1px solid var(--grid);text-align:right}
th:first-child,td:first-child{text-align:left}th{color:var(--ink2);font-weight:600}.tw{overflow-x:auto}
.pass{color:var(--pass);font-weight:600}.fail{color:var(--fail);font-weight:600}.chip{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:baseline}
section{border-top:1px solid var(--grid);margin-top:28px}svg text{fill:var(--ink2);font-size:11px}.legend{font-size:13px;color:var(--ink2)}
code{font-size:12.5px}.small{font-size:12.5px;color:var(--muted)}
"""


def load(run):
    d = REPO / "runs" / run
    sm = json.loads((d / "summary.json").read_text()) if (d / "summary.json").exists() else None
    rows = [json.loads(l) for l in (d / "scores.jsonl").read_text().splitlines()] if (d / "scores.jsonl").exists() else []
    man = json.loads((d / "manifest.json").read_text()) if (d / "manifest.json").exists() else None
    return sm, rows, man


def pct(x):
    return "n/a" if x is None else f"{100 * x:.0f}%"


def num(x, d=2):
    return "n/a" if x is None else f"{x:.{d}f}"


def hist_svg(series, bins=10, w=640, h=200):
    """series: list of (label, values, css_var, filled). Overlaid histograms of s in [0,1] (outliers clamped)."""
    pad_l, pad_b, pad_t = 36, 28, 10
    iw, ih = w - pad_l - 10, h - pad_b - pad_t
    counts = []
    for _, vals, _, _ in series:
        c = [0] * bins
        for v in vals:
            c[min(bins - 1, max(0, int(min(max(v, 0), 1) * bins - 1e-9)))] += 1
        n = max(1, len(vals))
        counts.append([x / n for x in c])
    ymax = max([max(c) for c in counts] + [0.05])
    ymax = min(1.0, (int(ymax * 10) + 1) / 10)
    bw = iw / bins
    out = [f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="histogram of buyer share s">']
    for k in range(0, 6):
        y = pad_t + ih - ih * k / 5
        out.append(f'<line x1="{pad_l}" x2="{w - 10}" y1="{y:.1f}" y2="{y:.1f}" stroke="var(--grid)" stroke-width="1"/>')
        out.append(f'<text x="{pad_l - 6}" y="{y + 4:.1f}" text-anchor="end">{ymax * k / 5:.0%}</text>')
    for i in range(bins + 1):
        if i % 2 == 0:
            out.append(f'<text x="{pad_l + i * bw:.1f}" y="{h - 10}" text-anchor="middle">{i / bins:.1f}</text>')
    out.append(f'<text x="{w - 10}" y="{h - 10}" text-anchor="end">s (buyer share of surplus)</text>')
    k = len(series)
    for si, ((label, vals, var, filled), c) in enumerate(zip(series, counts)):
        sub = (bw - 2) / k
        for i, f in enumerate(c):
            bh = ih * f / ymax
            x = pad_l + i * bw + 1 + si * sub
            y = pad_t + ih - bh
            style = f'fill="var({var})"' if filled else f'fill="var({var})" fill-opacity="0.45"'
            out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(sub - 2, 1):.1f}" height="{max(bh, 0):.1f}" rx="2" {style}>'
                       f'<title>{html.escape(label)}: s in [{i / bins:.1f}, {(i + 1) / bins:.1f}) = {f:.0%} of deals</title></rect>')
    out.append(f'<line x1="{pad_l}" x2="{w - 10}" y1="{pad_t + ih}" y2="{pad_t + ih}" stroke="var(--muted)"/>')
    out.append("</svg>")
    return "".join(out)


def legend(series):
    return '<div class="legend">' + " &nbsp; ".join(
        f'<span class="chip" style="background:var({v});{"" if f else "opacity:.45"}"></span>{html.escape(l)} (n={len(vals)})'
        for l, vals, v, f in series) + "</div>"


def metric_table(runs):
    cols = ["games", "cap-collapse", "IQR(s)", "median s", "deal (feasible)", "deal (infeasible)", "correct", "leak",
            "capture", "turns", "tokens/game", "trunc.", "gate"]
    t = ['<div class="tw"><table><tr><th>run</th>' + "".join(f"<th>{c}</th>" for c in cols) + "</tr>"]
    for r in runs:
        sm, _, _ = load(r)
        if not sm:
            t.append(f"<tr><td>{r}</td><td colspan={len(cols)}>not run</td></tr>"); continue
        g = sm["gate"]
        t.append(f"<tr><td>{r}</td><td>{sm['n']}</td><td>{pct(sm['cap_collapse'])}</td><td>{num(sm['iqr'])}</td>"
                 f"<td>{num(sm['median_s'])}</td><td>{pct(sm['deal_rate_feasible'])}</td><td>{pct(sm['deal_rate_infeasible'])}</td>"
                 f"<td>{pct(sm['correct_rate'])}</td><td>{pct(sm['leak_rate'])}</td><td>{num(sm.get('integrative_capture'))}</td>"
                 f"<td>{num(sm['mean_turns'], 1)}</td><td>{num(sm.get('tokens_per_game'), 0)}</td><td>{pct(sm['truncated_turn_rate'])}</td>"
                 f"<td class=\"{'pass' if g['passed'] else 'fail'}\">{'PASS' if g['passed'] else 'FAIL'}</td></tr>")
    t.append("</table></div>")
    return "".join(t)


def overview(steps):
    t = ['<div class="tw"><table><tr><th>step · variant</th><th>games</th><th>cap-collapse</th><th>IQR(s)</th><th>correct rate</th><th>gate</th><th>why</th></tr>']
    for step, runs, _ in steps:
        for r in runs:
            sm, _, _ = load(r)
            if not sm:
                continue
            g = sm["gate"]
            t.append(f"<tr><td>{step} · {r}</td><td>{sm['n']}</td><td>{pct(sm['cap_collapse'])}</td><td>{num(sm['iqr'])}</td>"
                     f"<td>{pct(sm['correct_rate'])}</td><td class=\"{'pass' if g['passed'] else 'fail'}\">{'pass' if g['passed'] else 'fail'}</td>"
                     f"<td style='text-align:left'>{html.escape('; '.join(g['reasons']) or '—')}</td></tr>")
    t.append("</table></div>")
    return "".join(t)


def note(run):
    f = NOTES / f"{run}.md"
    if not f.exists():
        return ""
    paras = [p.strip() for p in f.read_text().split("\n\n") if p.strip()]
    return "".join(f"<p>{html.escape(p)}</p>" for p in paras)


def step_section(step, runs, label):
    loaded = [(r, *load(r)) for r in runs]
    if not any(sm for _, sm, _, _ in loaded):
        return ""
    base_sm, base_rows, _ = load(BASELINE)
    series = []
    if base_rows and BASELINE not in runs:
        series.append(("baseline (var-baseline)", [x["s"] for x in base_rows if x["s"] is not None and not x["void"]], "--base", False))
    arm_vars = ["--en", "--ar", "--ja"] if len(runs) > 1 else ["--en"]
    for (r, sm, rows, _), var in zip(loaded, arm_vars):
        if rows:
            series.append((r, [x["s"] for x in rows if x["s"] is not None and not x["void"]], var, True))
    parts = [f'<section id="{step}"><h2>{step} · {html.escape(label)}</h2>',
             f'<p class="sub">{" · ".join(f"<code>{r}</code>" for r in runs)} (English–English; baseline in grey)</p>',
             note(runs[0]), legend(series), hist_svg(series), metric_table(runs)]
    fired = {}
    for r, sm, _, _ in loaded:
        for k, v in (sm or {}).get("checks_fired", {}).items():
            fired[k] = fired.get(k, 0) + v
    if fired:
        parts.append('<p class="small">CHECKS fired (games): ' + ", ".join(f"{html.escape(k)} {v}" for k, v in sorted(fired.items())) + "</p>")
    parts.append("</section>")
    return "".join(parts)


def lang_section():
    f = REPO / "reports" / "stage_b.html"
    return f.read_text() if f.exists() else ""


def main():
    body = [f"<main><h1>grounded-arena · results</h1>",
            '<p class="sub">K2 Horizon (IFM/K2-Horizon-375B-A23B) in both seats · upstream NegotiationArena buy-sell · '
            "temperature 1.0, top_p 0.95 · all numbers from deterministic metrics (GOALS §5).</p>",
            "<h2>Variants at a glance</h2>",
            "<p>Gate: cap-collapse ≤ 50%, IQR(s) ≥ 0.25, and for right-or-wrong games a correct rate within 20–90%. "
            "s = (v − p)/(v − c), the buyer's share of the surplus; cap-collapse = share of feasible deals with s ≤ 0.1.</p>",
            overview(STAGE_A[1:])]
    lang_legend = " &nbsp; ".join(f'<span class="chip" style="background:var(--{k})"></span>{k}' for k in LANG_COLOR)
    body.append(f'<p class="legend">Language colours (fixed everywhere): {lang_legend}. Stage A is English–English, drawn in the en colour.</p>')
    for step, runs, label in STAGE_A:
        body.append(step_section(step, runs, label))
    body.append(lang_section())
    body.append("</main>")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                   f"<title>Grounded Arena Results</title><style>{CSS}</style></head><body>{''.join(body)}</body></html>\n")
    print(f"wrote {OUT.relative_to(REPO)}")
    update_state()


def update_state():
    """Refresh the auto gate table in STATE.md between the gates markers."""
    st = REPO / "STATE.md"
    if not st.exists():
        return
    lines = ["| step | run | games | cap-collapse | IQR(s) | correct | leak | tokens/game | verdict |", "|---|---|---|---|---|---|---|---|---|"]
    for step, runs, _ in STAGE_A + STAGE_B:
        for r in runs:
            sm, _, _ = load(r)
            if sm:
                v = "PASS" if sm["gate"]["passed"] else "FAIL: " + "; ".join(sm["gate"]["reasons"])
                lines.append(f"| {step} | {r} | {sm['n']} | {pct(sm['cap_collapse'])} | {num(sm['iqr'])} | {pct(sm['correct_rate'])} | "
                             f"{pct(sm['leak_rate'])} | {num(sm.get('tokens_per_game'), 0)} | {v} |")
    t = st.read_text()
    a, b = "<!-- gates:start -->", "<!-- gates:end -->"
    if a in t and b in t:
        t = t.split(a)[0] + a + "\n" + "\n".join(lines) + "\n" + b + t.split(b)[1]
        st.write_text(t)


if __name__ == "__main__":
    main()
