#!/usr/bin/env bash
# Build the example dashboard: inline notebook.css into index.html, then bundle with dashboard-export.
# Works from any directory: paths resolve from this script's location.
set -euo pipefail
SK="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
EX="$SK/template-charlie/examples/dashboard"
OUT="${1:-out/template_charlie_dashboard.html}"
mkdir -p "$(dirname "$OUT")"
{ echo "<style>"; cat "$SK/template-charlie/notebook.css"; echo "</style>"; cat "$EX/body.html"; } > "$EX/index.html"
python3 "$SK/dashboard-export/build_standalone.py" \
  --html "$EX/index.html" --js "$SK/template-charlie/plate.js" --js "$EX/app.js" \
  --data daily="$EX/data/daily.csv" --data heat="$EX/data/heat.csv" --data ebike="$EX/data/ebike.csv" \
  --title "Bike share, 2025" --out "$OUT"
