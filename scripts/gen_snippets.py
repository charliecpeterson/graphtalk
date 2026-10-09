#!/usr/bin/env python3
"""Pre-render step: wrap each skill's SKILL.md in a fenced block so index.qmd can include it.

Writes _generated/<skill>.md. The fence is four backticks because SKILL.md contains
three-backtick blocks of its own. Quarto runs this before every render (see _quarto.yml).
"""
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / "docs" / "_generated"
out.mkdir(exist_ok=True)
for skill in sorted((root / "skills").glob("*/SKILL.md")):
    text = skill.read_text().rstrip("\n")
    (out / f"{skill.parent.name}.md").write_text(f"````markdown\n{text}\n````\n")
print("wrote", ", ".join(sorted(p.name for p in out.glob("*.md"))))
