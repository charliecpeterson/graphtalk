# Using Claude with graphs

Slides and materials for a 20-minute talk on making better plots with Claude: Excel with
Claude, Claude Code, and two skills.

- **Slides:** [graphtalk.charlespeterson.dev](https://graphtalk.charlespeterson.dev)
- **Prompts:** every prompt from the talk is in [`docs/prompts.md`](docs/prompts.md)

## What is in here

| Folder | Holds |
|---|---|
| `data/bikeshare/` | Synthetic bike-share data for one year: `trips.csv`, `stations.csv`, `weather.csv`, `daily_summary.csv`, and `bike_data.xlsx` (the same data for Excel) |
| `skills/dashboard-export/` | Skill: build the dashboard, then also save HTML, SVG, PNG and R code for every plot |
| `skills/template-charlie/` | Skill: my chart style (headline is the finding, margin notes, direct labels, source line), with code and examples |
| `dist/` | The two skills as zips, ready to upload in Claude desktop (Customize > Skills) |
| `docs/` | The slides: `index.qmd` (source), `index.html`, `ask-the-data.pdf`, `prompts.md` |
| `out/` | Saved results to fall back on if a live run stalls: `demo-default-style/` (without the style skill) and `demo-charlie-style/` (with it) |

## Use the skills

- **Claude desktop:** upload `dist/dashboard-export.zip` and `dist/template-charlie.zip` under Customize > Skills.
- **Claude Code:** copy the folders from `skills/` into `.claude/skills/` in your project, then call them with `/dashboard-export` and `/template-charlie`.

## Rebuild the slides

Needs [Quarto](https://quarto.org). The PDF step also needs Node and Chrome.

```bash
./build.sh              # zips the skills, renders docs/index.html, writes docs/ask-the-data.pdf
./build.sh --html-only  # skip the PDF
```

The slides are served from `docs/` with GitHub Pages.
