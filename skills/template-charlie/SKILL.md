---
name: template-charlie
description: >
  Charles Peterson's house style for any chart, plot, figure, PNG/SVG or dashboard:
  warm-paper "plates" with a takeaway headline, numbered margin notes, direct labels,
  range-frame axes and a provenance line. Use for any visualization you draw for him,
  in any project (talks, papers, reports, dashboards), or when he says "plate", "my
  style", "make it look like mine", or says a figure looks generic or AI-made. Use
  instead of default matplotlib, seaborn, plotly or card-and-KPI-tile styling. Pairs
  with dashboard-export (HTML + SVG/PNG files) and dataviz (palette validation).
---

# template-charlie

Models draw every chart the same way: centered noun-phrase title, boxed legend, default blue and
orange, gridlines everywhere, a row of big-number tiles on top. That sameness is the tell. This
skill replaces it with one specific look that belongs to one person, and it ships code and rendered
examples so the look is reproduced, not described.

**Before drawing anything, open two PNGs in `examples/gallery/`** (for instance `plate02_weather.png`
and `plate01_rhythm.png`). The target is the images, not the rules below.

## The look (ten rules)

1. **Paper, not white.** Warm paper ground, ink text, hairline rules, crop marks in the corners.
2. **The headline is the finding.** One sentence with a number in it ("Casual riders at 8 to 11
   degrees ride at 35% of normal."), never a noun phrase ("Ridership by Temperature"). Bold serif,
   left-aligned. An italic deck of one or two lines says what is plotted and in what units.
3. **Numbered marginalia, no legend box.** Ink badges on the data; matching notes in the right
   margin, each stating a number computed from the data. The notes are the argument.
4. **Direct labels.** Name a series at the end of its line. Color is on the mark, words are ink.
5. **Range-frame axes.** Axis lines span the data only. No box, no top or right spine, no gridlines
   (ledger rules only where a table needs them).
6. **A provenance line on every plate.** Data file, row count, short hash, date. If a subset is
   plotted, say so (`plotted=`). If the data came from elsewhere, say where.
7. **Non-default forms.** Dot matrix over heatmap, dumbbell over grouped bars, thin raw line under a
   thick 7-day mean over one jagged line. See `reference/palette-and-forms.md`.
8. **Mono for numbers, serif for words.** Menlo for badges, provenance, values; Charter for the rest.
9. **Nothing decorative.** No gradients, shadows, rounded cards, emoji, icons, 3D.
10. **No summary on top.** No KPI tiles, stat strip, "key takeaways" or executive summary in any form.
    The first plate's headline is the finding. A dashboard opens with title, one italic line and a
    one-line mono run stub (date, row counts, date span), then straight into plate 01.

Palette: series teal `#00929B`, amber `#B87800`, rose `#D8435A`, three at most, always direct-labeled.
Brand teal `#1C6D72` is for structure only. Details and the validator command are in
`reference/palette-and-forms.md`.

### Layout tells to remove on sight

Stat strip or tiles at the top; rounded shadowed cards; hero banner; centered headings; three equal
columns; pill buttons or tabs; gradient or glass backgrounds; icons or emoji by headings; a "Key
insights" panel; a boxed legend; a title that names the chart; even spacing with no hierarchy;
dual axes; pie or donut charts.

## Workflow

1. **State the finding first.** Compute the number the plate is about from the data. If you cannot
   write the headline sentence, you do not know what to plot yet.
2. **Pick the form** by the reader's job, from the tables in `reference/palette-and-forms.md`. Run its three tests (costume, one accent, back of the room) before drawing. Skip a plain bar, pie or scatter unless the table names it.
3. **Draw it.**
   - Static figure (PNG/SVG): `plate.py`, API and limits in `reference/api.md`.
     `p.save(path)` writes both a 200 dpi PNG and an SVG, which is what `dashboard-export` wants.
   - Dashboard (HTML): `notebook.css` + `plate.js`, recipe in `reference/dashboard-html.md`.
   - Other library (plotly, ggplot, Observable): copy the tokens from `plate.py` (colors, fonts,
     rules above) rather than the library defaults. Same look, different engine.
4. **Look at it.** Render, open the PNG (or screenshot the HTML) and check, in this order:
   headline is a finding on one or two balanced lines; every series has a direct label; every badge
   has a matching note and every note's number is right (computed, not typed); nothing touches
   another label or the footer; `plotted=` is set if rows were filtered; no layout tell from the list
   above. Fix what you see before reporting done. A figure never looked at is not finished.
5. **Save into the project,** not the scratchpad: plates to `plates/` or the project's figure folder,
   dashboards via `dashboard-export` to `out/<slug>/`.

## Voice

Direct subject-verb-object, a number in every claim, no hedging ("seems to", "appears"), no em
dashes, no exclamation marks, no "insights", no "unlock". Headlines and notes are the only prose on a
plate. Say what the data shows and no more: if you suspect a cause the data cannot show, write
"suspect" in a note and name what would confirm it, never in the headline. A recommended fix goes in
the last note, as an action with its evidence.

## Using it in another project

The skill is self-contained. In Claude Code, copy this folder into the project's `.claude/skills/` (or
`~/.claude/skills/` for every project). In Claude desktop, zip the folder and upload it under
Customize > Skills. Data paths in `source=` resolve from the current directory.
To make it someone else's style, change the tokens at the top of `plate.py` and the variables at the
top of `notebook.css`, replace `examples/gallery/` with plates in the new look, and rewrite the
ten rules; the structure (finding headline, marginalia, direct labels, provenance) can stay.

## Files

| File | What it is |
|---|---|
| `plate.py` | `Plate` class (chrome, axes, `mark`, `note`, `label`, `save`), `dotmatrix`, `dumbbell`, `thin_thick`, `shade`, `monthly`, `headroom`, tokens, colormaps |
| `notebook.css`, `plate.js` | HTML dashboard: tokens, folio layout, d3 helpers (range axis, direct label, badge, tooltip) |
| `reference/` | `api.md` (matplotlib API and limits), `palette-and-forms.md`, `dashboard-html.md` |
| `examples/gallery/` | The target: four rendered plates |
| `examples/bikeshare_plates.py`, `examples/dashboard/` | The same plates as code, and a working dashboard (demo data only) |

Needs Python with matplotlib, numpy, pandas. Node only for the palette validator.
