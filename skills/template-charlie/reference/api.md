# plate.py API and limits

```python
import sys; sys.path.insert(0, "<this skill's directory>")
from plate import Plate, dotmatrix, dumbbell, TEAL, AMBER, ROSE

p = Plate(number=2, headline="Casual riders at 8 to 11 degrees ride at 35% of normal.",
          deck="Trips per daytime hour in dry weather, indexed to the 17 to 20 degree bin (= 100).",
          source=["data/bikeshare/trips.csv", "data/bikeshare/weather.csv"],
          plotted="149,495 trips, dry daytime hours")   # what is actually drawn
ax = p.axes()                       # p.axes(1, 2) for two panels
ax.plot(x, y, color=TEAL, lw=2.2)
p.label(ax, x[-1], y[-1], "Members", TEAL)    # dot + direct label
p.mark(ax, x[1], y[1], 1)                      # numbered badge on the data
p.note(1, f"Casual riders ride at {share:.0f}% of their normal rate.")   # computed, not typed
p.save("plates/plate02")            # writes .png (200 dpi) and .svg
```

`examples/bikeshare_plates.py` is the full pattern for four plates. Keep every number in a note
computed from the data so an edited CSV does not leave a stale claim.

Helpers: `thin_thick(ax, x, y, color)` (day under a 7-day mean, returns the last point for `label`),
`shade(ax, x0, x1, "label")` (event band), `monthly(ax)` (Jan, Feb, ... date ticks),
`headroom(ax, 0.12)` (room above the data so peak badges stay inside), `rolling_mean`.

## Limits the code enforces or assumes

- **Margin notes.** About 3 notes of 3 to 4 lines each (34 characters a line). A fourth long note
  raises `ValueError` instead of printing over the footer. Merge or shorten.
- **Headline.** One finding, up to about 110 characters; wraps at 60 per line. Deck up to about 280
  characters (wraps at 140).
- **Left margin.** `p.axes(left=1.0)` reserves inches for y tick labels. Names over ~12 characters
  need `left=1.6` or more; text that does not fit runs off the page without a warning, so check the render.
- **Dumbbells.** `dumbbell(ax, labels, start, end, colors=[...], emphasis=i, badges={row: n})`.
  `colors` is per row; `badges` puts a numbered badge after that row's value label. About 12 rows per
  panel at the default size.
- **Labels.** `label()` takes `dx` and `dy` in points. Two line-end labels closer than about 20 px
  collide: separate them with `dy`.
- **Badges.** `mark()` offsets are in points. Keep them off the data and leave headroom for peaks.
  `ring=False` for arrows and bars drops the leader too.
- **Paths.** `source=` paths resolve from the current directory; a missing file warns and loses the
  row count and hash. Pass `drawn=False` for an identical PNG on re-run, `number=1` for a single plate.
- **Log and date axes** work; the range frame follows the data.
