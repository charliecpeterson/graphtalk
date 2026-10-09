---
name: dashboard-export
description: Whenever you create or update a dashboard, in any form (a published Artifact, a Claude Dashboard artifact, an HTML/React page, a matplotlib/plotly/D3 multi-plot view), ALSO write out/SLUG/ with a standalone index.html plus an SVG, a PNG and an R script (ggplot2) for every plot, so the user can edit the figure in R. The files are in addition to the dashboard the user asked for, never instead of it. Trigger on any dashboard build, or on "export the dashboard", "make an HTML copy", "save the plots", "offline dashboard".
---

# Dashboard export: HTML + plot images

**This skill adds files. It never replaces the deliverable.** Build the dashboard
the user asked for first. If they asked for an artifact, or did not say where it
should live, publish it as an Artifact and give them the link. Then leave the
files below on disk as well. Never stop after writing files when a published
dashboard was wanted, and never publish without writing the files.

A dashboard should never exist only as a link, a chat render or a running
process. Every time you create or materially change one, leave these on disk
in the project (not the scratchpad):

```
out/<dashboard-slug>/
  index.html        standalone page: layout, styles, scripts, embedded data
  plots/
    <plot-id>.svg   vector copy of each plot
    <plot-id>.png   raster copy of each plot (2x scale)
    <plot-id>.R     R code that redraws that plot from data/<plot-id>.csv
  data/
    <plot-id>.csv   the exact rows each plot draws (always CSV, one per plot)
```

`<plot-id>` is a short kebab-case name matching the plot's heading or dataset
id. One SVG, PNG, R script and CSV per plot, not one per dashboard. The R script exists so
the user can make manual edits in R, so write it to be read and changed.

## Steps

1. **Pick the folder.** Reuse `out/<slug>/` if the dashboard was exported
   before; overwrite its files rather than creating a numbered copy.
2. **Write `index.html`** so it opens by double-click: inline CSS and JS, data
   embedded as JSON, no build step. A library from a CDN is fine; offer
   `--inline` / a local copy if the user needs it to work with no network
   (downloading a library needs the user's yes first).
3. **Export every plot to SVG and PNG** using the route that matches how the
   plot was made:
   - matplotlib / seaborn: `fig.savefig(p/"id.svg")` and
     `fig.savefig(p/"id.png", dpi=200)`
   - plotly: `fig.write_image("id.svg")` and `fig.write_image("id.png", scale=2)`
     (needs `kaleido`)
   - D3 / hand-written SVG in the page: serialize the `<svg>` element with
     `new XMLSerializer().serializeToString(node)`, inlining computed styles and
     CSS variable values so it renders outside the page; write that as the SVG.
     Rasterize it by screenshotting the element in a headless browser (the
     built-in browser tools work) or with `cairosvg`/`rsvg-convert` if present.
     No Python raster library? Do it in the page: clone the `<svg>`, copy
     `getComputedStyle` values (fill, stroke, font-*, opacity, text-anchor) onto
     each clone element as inline style, add a `<title>`, a background `<rect>`
     and `width`/`height` from the viewBox, serialize, draw the SVG into a
     2x `<canvas>` through an `Image`, and POST the SVG text and
     `canvas.toDataURL().split(',')[1]` to a tiny `127.0.0.1` receiver script
     (with CORS headers) that writes them into `out/<slug>/plots/`. Do this once
     per plot, and once per tab or filter state that changes what is drawn.
   - canvas charts: `canvas.toBlob()` for the PNG; there is no SVG, so say so
     rather than faking one.
   Give every SVG a `<title>`, a white or theme-matching background rect, and
   an explicit `width`/`height`, so it is not transparent or zero-sized when
   opened alone.
4. **Check the output.** Serve the folder on 127.0.0.1
   (`python3 -m http.server --bind 127.0.0.1`), load `index.html`, confirm the
   console is clean and every plot renders. Open at least one PNG and one SVG
   to confirm they are not blank or clipped. Stop the server afterwards.
5. **Write the R code for every plot.** For each plot, save the rows it draws as
   `data/<plot-id>.csv` and write `plots/<plot-id>.R` (see "R scripts" below).
   Skip a plot only if no ggplot2 version is reasonable, and say which one.
6. **Publish the Artifact** when one was asked for or implied (see "Publishing
   as an Artifact" below), and give the link.
7. **Report** the Artifact link, the folder, the list of plot files (including the R scripts), and anything
   that differs from the live version (see below).

If the user's style skill applies (e.g. `template-charlie`), apply it to the
page and the exported images alike, so the files match what they saw.

## R scripts

Each `plots/<plot-id>.R` must run on its own, from the dashboard folder
(`Rscript plots/<plot-id>.R` with `out/<slug>/` as the working directory) and
rewrite that plot's SVG and PNG. Rules:

- Load only `ggplot2` and `readr` (plus `svglite` for SVG output). Install nothing.
- Read `data/<plot-id>.csv`, never the original source file, so the script
  matches the plot exactly. If the plot shows computed numbers (a mean, a share,
  a fitted line), compute them in the CSV or at the top of the script, not
  buried in the drawing code.
- Put the title, subtitle, colors, and sizes in clearly named variables at the
  top, under a `# Edit here` comment, so a manual edit is one line.
- End with `ggsave("plots/<plot-id>.svg", p, width = W, height = H)` and
  `ggsave("plots/<plot-id>.png", p, width = W, height = H, dpi = 200)`, with W
  and H in inches matching the exported image's shape.
- Match the Python or D3 version as closely as ggplot2 allows: same chart form,
  same title, same series colors, direct labels with `geom_text`, no default
  gray panel (`theme_minimal()` or `theme_classic()` as a base). If a style
  skill applies (for example `template-charlie`), copy its fonts, colors, and
  headline-as-finding as well. Tell the user that the R version is a close copy,
  not a pixel match.
- Run each script once with `Rscript` and confirm it writes both files. If R is
  not installed, still write the scripts and say they were not run.

Template:

```r
# plots/ebike-share.R: run from out/<slug>/
library(ggplot2); library(readr)

# Edit here ---------------------------------------------------------------
title    <- "Every neighborhood gained e-bikes; the city share fell"
subtitle <- "Share of trips on e-bikes, Jan to Jun versus Jul to Dec"
col_main <- "#00929B"; col_city <- "#D8435A"
# -------------------------------------------------------------------------

d <- read_csv("data/ebike-share.csv", show_col_types = FALSE)
d$series <- ifelse(d$neighborhood == "All trips", "city", "hood")
d$y <- reorder(d$neighborhood, d$h2)

p <- ggplot(d, aes(y = y, colour = series)) +
  geom_segment(aes(x = h1, xend = h2, yend = y),
               arrow = arrow(length = unit(2, "mm")), na.rm = TRUE) +
  geom_point(aes(x = h1), shape = 21, fill = "white", size = 2.5, na.rm = TRUE) +
  geom_text(aes(x = pmax(h1, h2, na.rm = TRUE), label = sprintf("%.1f%%", h2)),
            hjust = -0.4, size = 3, colour = "black") +
  scale_colour_manual(values = c(hood = col_main, city = col_city), guide = "none") +
  scale_x_continuous(expand = expansion(mult = c(0.02, 0.12))) +
  labs(title = title, subtitle = subtitle, x = "% of trips on e-bikes", y = NULL) +
  theme_classic(base_size = 11)

ggsave("plots/ebike-share.svg", p, width = 7, height = 4)
ggsave("plots/ebike-share.png", p, width = 7, height = 4, dpi = 200)
```

## Publishing as an Artifact

Publish from a copy of `index.html`, not from the file in `out/`:

1. Strip the `<!doctype>`, `<html>`, `<head>` and `<body>` tags. The Artifact
   tool wraps the page itself. Keep the `<title>` (a two to four word name, no
   subtitle), `<style>`, markup and scripts.
2. Scripts may load only from cdnjs.cloudflare.com, cdn.jsdelivr.net/npm,
   unpkg.com, cdn.tailwindcss.com or code.jquery.com, pinned to an exact version.
   Stylesheets only from Google Fonts. Everything else is inlined.
3. Call the Artifact tool with `icon` (one generic word such as `chart`) and a
   one-sentence `description`. Publishing is private by default; tell the user
   who can open it and that sharing is theirs to change.
4. To update later, publish the same file path again so the URL stays the same,
   and rebuild the files in `out/<slug>/` so the two never drift apart.

Report any difference between the Artifact and the files (for example, the R scripts are a close copy of each plot; or the
Artifact follows the viewer's light or dark setting and the PNGs are one theme).

## Claude Dashboard artifacts

A Dashboard-type artifact runs against a `dash` object (data, calc, onData,
colors) that does not exist outside claude.ai. For these, use the bundler in
this folder to produce `index.html`, then do step 3 on the result.

1. Keep the page source on disk while you build: markup and style as
   `dashboard/index.html`, scripts as `dashboard/app.js`, each dataset's rows
   as a local CSV/TSV/JSON file named after its id. Live-query datasets carry
   the user's own data access, so include their rows only if the user asks,
   and say who will see the file.
2. Run:

   ```bash
   python3 <this skill dir>/build_standalone.py \
     --html dashboard/index.html --js dashboard/app.js \
     --data daily=data/bikeshare/daily_summary.csv --title "<dashboard title>" \
     --out out/<slug>/index.html
   ```

   Add `--inline-d3 path/to/d3.min.js` for a file that works with no network.
3. Differences to mention: no live refresh, no Sources panel, no click-a-number
   query view; data is whatever was embedded.

Limits: the stand-in `dash` supports data, calc, onData, colors and no-op
params, loader and links. A page that relies on a filter or a loader needs
those written into the SHIM in `build_standalone.py` by hand. Design tokens are
light and dark fallbacks, so colors approximate the claude.ai theme rather than
match it.
