# HTML dashboard (folio layout)

1. Put the page in `index.html`: paste `notebook.css` into a `<style>` block, then the markup (see
   `examples/dashboard/body.html`: a header, the `.stub` line, then `.plate` sections each with a
   `.folio` numeral, a `.plate-main` figure and an `<ol class="notes">`).
2. Load `plate.js` before your script. It gives `PLATE.rangeAxis`, `PLATE.directLabel`,
   `PLATE.badge`, `PLATE.tooltip`. `examples/dashboard/app.js` shows the pattern, including notes
   computed in JS.
3. Bundle with the `dashboard-export` skill. `examples/dashboard/build.sh` shows the exact command
   (`--js plate.js --js app.js`, one `--data` per CSV). Also export each plot as SVG and PNG, as
   that skill describes.
4. Hover tooltips show the exact value. Tabs are underlined text, never pill buttons.
5. The run stub is one mono line: date, each dataset's row count, the date span it covers.
