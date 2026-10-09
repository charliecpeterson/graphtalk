#!/usr/bin/env bash
# Zip each skill folder into dist/<name>.zip for upload in Claude desktop
# (Customize > Skills). The folder name sits at the top of the zip, SKILL.md inside it.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
mkdir -p dist
for d in skills/*/; do
  name="$(basename "$d")"
  rm -f "dist/$name.zip"
  (cd skills && zip -qr "../dist/$name.zip" "$name" -x "*/__pycache__/*" "*.DS_Store")
  echo "dist/$name.zip  ($(du -h "dist/$name.zip" | cut -f1))"
done
