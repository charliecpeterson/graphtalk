# Palette and choosing a form

## Palette

Brand teal `#1C6D72` is structure only (label bar, rules): measured, it is too gray to carry data.
Series colors are teal `#00929B`, amber `#B87800`, rose `#D8435A`, in that order, three at most.
They were adjusted from the brand colors until they passed the dataviz validator on paper `#f4efe4`
(lightness band, chroma floor, normal-vision floor, 3:1 contrast).

The rose and amber pair is 6.7 apart under deuteranopia. That is only legal because every series is
also direct-labeled, so never ship one without the label.

Night mode (HTML only): `#139AA3`, `#BD8316`, `#DB4E63` on `#1b1a17`, also validated.
Re-run the validator if you change a hex:

```bash
node <dataviz skill dir>/scripts/validate_palette.js "#00929B,#B87800,#D8435A" --mode light --surface "#f4efe4"
```

Magnitude uses `SEQ` (paper to teal to deep brand teal). Polarity uses `DIV` (teal to paper-gray to
rose). One hue per job, never a rainbow.

## Choosing a form

| The job | Use | Not |
|---|---|---|
| A value over hours and weekdays | `dotmatrix` | heatmap |
| Before and after, or any A vs B rate, per item | `dumbbell` | grouped bars, slope chart with 8 crossing lines |
| Trend with noise | `thin_thick` (thin day, thick 7-day mean), direct labels, `shade` for a window | one jagged line, legend |
| Two series on different scales | index both to 100 at a baseline, one axis | dual axis (never) |
| Part of a whole | a small table of numbers or a single stacked rule | pie or donut |
| Headline numbers | none at the top; put the number in the plate headline or a margin note | KPI tiles, stat strip |

To add a form, write a function beside `dotmatrix` in `plate.py` that takes an Axes and keeps the
same ink, rules and fonts.

## Choose the form by the reader's job

Ask what the reader must do with the chart, then pick the form. The default bar, pie and
scatter come from habit, not from the job.

| The reader must | Form | Not | In plate.py? |
|---|---|---|---|
| See one headline number | The number inside the plate headline or a margin note | A stat tile or big-number card (rule 10) | n/a |
| Compare a few magnitudes | Dot plot or sorted horizontal bars, value printed at the end, one accent mark | Vertical bars, 3-D, pie | draw with `ax.hlines` + `ax.plot` |
| Compare A against B per item | `dumbbell` | Grouped bars | yes |
| Follow change over time | `thin_thick`, direct labels, `shade` for an event | A bar per period; one jagged line | yes |
| See a pattern across two categories (hour by weekday) | `dotmatrix` | Rainbow or default heatmap | yes |
| See a share of a whole | One stacked rule, six segments at most, labeled in place | Pie or donut | draw with `ax.barh(left=)` |
| See hierarchy and share together | Treemap | Nested pies | no: build it, same tokens |
| See quantity moving through stages | Sankey or a flow table | A table of percentages | no: build it, same tokens |
| See structure or architecture | A small diagram | A long bullet list | no |
| Relate two measures | Scatter with a fitted line and one labeled outlier | Dual axes (never); scatter with no line | yes, plain axes |

A form that is not in `plate.py` still gets the plate chrome (headline, margin notes,
provenance line, ink and paper colors). Write it as a function beside `dotmatrix`.

## Three tests before you draw

1. **The costume test.** If the point of the chart needs a sentence to find, it is a
   table wearing a costume. Print the table, or change the form until the finding is the
   most visible thing on the plate.
2. **One accent.** Gray out the context and put color on the single series or mark the
   headline is about. Use a magnitude ramp (`SEQ`) for amount and the three series colors
   only for identity.
3. **Back of the room.** Labels and values stay readable at slide size. If a label needs
   a legend lookup, label the mark directly.
