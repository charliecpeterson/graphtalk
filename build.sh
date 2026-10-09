#!/usr/bin/env bash
# build.sh: render the deck (source and output both live in docs/) for GitHub Pages, plus a PDF handout.
#
# Usage:
#   ./build.sh                   # HTML + PDF
#   ./build.sh --html-only       # skip the PDF
#   CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ./build.sh
#       (decktape needs a Chrome; set this if it cannot find one)
#
# GitHub Pages: Settings > Pages > Deploy from a branch > main / docs.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

echo "> Zipping skills to dist/"
./scripts/zip_skills.sh

echo "> Rendering docs/index.qmd to docs/index.html"
quarto render docs/index.qmd

if [[ "${1:-}" == "--html-only" ]]; then
  echo "Done: docs/index.html"
  exit 0
fi


echo "Done"
echo "  HTML: docs/index.html"
echo "  PDF:  docs/ask-the-data.pdf"
