#!/usr/bin/env python3
"""Bundle a Claude Dashboard page into one offline-capable HTML file.

The dashboard type gives page scripts a `dash` object (data, calc, onData,
colors). This script embeds the data and supplies a small stand-in for `dash`
so the same markup and scripts run in any browser. d3 comes from cdnjs unless
--inline-d3 points at a local d3.min.js.
"""
import argparse, csv, io, json, sys
from pathlib import Path

TOKENS = """
:root{--color-fg:#1f1e1d;--color-fg-muted:#6b6a66;--color-bg:#faf9f5;--color-panel:#fff;--color-border-line:#e5e2d9;--color-ok:#2e7d4f;--color-warn:#b7791f;--color-bad:#c0392b;
--cds-radius:10px;--cds-pad-xs:4px;--cds-pad-sm:8px;--cds-pad-md:12px;--cds-pad-lg:20px;--cds-gap-xs:4px;--cds-gap-sm:8px;--cds-gap-md:16px;--cds-gap-lg:24px;
--cds-font-size-caption:12px;--cds-font-size-body:15px;--cds-font-size-heading:16px;--cds-font-size-title:30px;--cds-font-weight-medium:500;
--cds-chart-muted:#c9c6bc;--cds-chart-grid:#e5e2d9;--cds-chart-axis:#b5b1a5;--cds-chart-reference:#8a867a;--cds-chart-status-critical:#c0392b;
--cds-surface-popover:#fff;--cds-border:#d8d4c8;--cds-shadow-popover:0 4px 14px rgba(0,0,0,.12);--cds-text-secondary:#6b6a66;
--cds-dur-slow:500ms;--cds-ease-out:cubic-bezier(.2,.7,.2,1);
--font-anthropic-sans:system-ui,-apple-system,"Segoe UI",sans-serif;--font-anthropic-serif:Georgia,"Times New Roman",serif}
@media (prefers-color-scheme:dark){:root{--color-fg:#ece9e1;--color-fg-muted:#a09d94;--color-bg:#1c1b19;--color-panel:#262522;--color-border-line:#3a3833;--cds-chart-muted:#4a4842;--cds-chart-grid:#3a3833;--cds-surface-popover:#2e2d2a;--cds-border:#44413b;--cds-text-secondary:#a09d94}}
body{margin:0;background:var(--color-bg);padding:clamp(12px,3vw,32px)}
@keyframes dash-sk{50%{opacity:.4}}
.dash-skeleton{min-height:1em;animation:dash-sk 1.2s infinite}
"""

SHIM = """
const __raw = %(data)s;
const __calc = {};
const __params = {};
const dash = {
  colors: ['#c96442','#5b7fa6','#6a9a6f','#d4a24c','#8a6bb0','#4f9a9a','#b5546b','#7d7d7d'],
  calc(id, o) { __calc[id] = o.fn(...o.inputs.map(i => __raw[i])); },
  loader() {},
  data(id) { const d = id in __calc ? __calc[id] : __raw[id]; return { status: d === undefined ? 'missing' : 'ok', data: d || [], meta: [] }; },
  params: () => ({ ...__params }),
  setParams(p) { Object.assign(__params, p); },
  resetParams() {},
  setLink() {},
  refresh() {},
  onData(fn) { fn(); let t; addEventListener('resize', () => { clearTimeout(t); t = setTimeout(fn, 80); }); }
};
"""


def load_rows(path: Path):
    text = path.read_text()
    if path.suffix == ".json":
        j = json.loads(text)
        return j if isinstance(j, list) else next(j[k] for k in ("rows", "data", "results") if k in j)
    delim = "\t" if path.suffix == ".tsv" else ","
    return list(csv.DictReader(io.StringIO(text), delimiter=delim))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True, help="the page's files/index.html (markup + style)")
    ap.add_argument("--js", action="append", default=[], help="page scripts, in load order")
    ap.add_argument("--data", action="append", default=[], help="datasetId=path.csv|tsv|json")
    ap.add_argument("--title", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--inline-d3", help="path to d3.min.js to embed (offline use)")
    a = ap.parse_args()

    data = {}
    for spec in a.data:
        k, _, p = spec.partition("=")
        if not p:
            sys.exit(f"--data needs id=path, got {spec!r}")
        data[k] = load_rows(Path(p))

    d3 = (f"<script>{Path(a.inline_d3).read_text()}</script>" if a.inline_d3
          else '<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>')
    scripts = "\n".join(Path(p).read_text() for p in a.js)
    shim = SHIM % {"data": json.dumps(data).replace("</", "<\\/")}
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{a.title}</title>
{d3}
<style>{TOKENS}</style>
</head><body>
<div id="dash-root">
{Path(a.html).read_text()}
</div>
<script>
{shim}
{scripts}
</script>
</body></html>"""
    Path(a.out).write_text(html)
    print(f"wrote {a.out} ({len(html):,} bytes, datasets: {', '.join(data) or 'none'})")


if __name__ == "__main__":
    main()
