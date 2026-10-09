"""template-charlie: matplotlib helpers for the "plate" figure format.

A plate is one figure on warm paper with a takeaway headline, numbered
marginalia instead of a legend box, range-frame axes, and a provenance line
that records the data it was drawn from.

    from plate import Plate, dotmatrix, dumbbell, TEAL, AMBER, ROSE

    p = Plate(number=3, headline="Casual riders stay home when it is cold",
              deck="Trips per daytime hour, indexed to the 17-20 C bin.",
              source=["data/bikeshare/trips.csv", "data/bikeshare/weather.csv"])
    ax = p.axes()
    ax.plot(x, y, color=TEAL)
    p.label(ax, x[-1], y[-1], "Casual", TEAL)
    p.mark(ax, x[3], y[3], 1)
    p.note(1, "At 8 to 11 C casual riders ride at 35% of their normal rate.")
    p.save("out/plate03")        # writes out/plate03.png and out/plate03.svg
"""
from __future__ import annotations

import datetime as dt
import hashlib
import textwrap
import warnings
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager as fm
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

# ---- tokens -----------------------------------------------------------------
PAPER, INK, INK2, MUTED, RULE = "#f4efe4", "#1f1d1a", "#55504a", "#8f887b", "#cdc5b3"
BAND, GUIDE = "#e3dccb", "#8f887b"  # shaded event band, dotted reference line
BRAND = "#1C6D72"  # structure only (label bar, rules); too gray to carry data
# Series colours. Validated on PAPER with the dataviz validator: lightness band,
# chroma floor, normal-vision floor and 3:1 contrast pass; deutan separation of
# rose vs amber is 6.7, so identity must also ride on direct labels (see label()).
TEAL, AMBER, ROSE = "#00929B", "#B87800", "#D8435A"
SERIES = [TEAL, AMBER, ROSE]
SEQ = LinearSegmentedColormap.from_list(
    "plate_seq", ["#e6e6d8", "#b9d8d5", "#6fb8bb", TEAL, BRAND, "#0e3f43"])
DIV = LinearSegmentedColormap.from_list(
    "plate_div", ["#0e5f65", TEAL, "#9fd1d2", "#ece6d8", "#f0b6bd", ROSE, "#9c2438"])


def _pick(names: list[str]) -> str:
    have = {f.name for f in fm.fontManager.ttflist}
    return next((n for n in names if n in have), names[-1])


SERIF = _pick(["Charter", "Iowan Old Style", "Palatino", "Georgia", "DejaVu Serif"])
MONO = _pick(["Menlo", "DejaVu Sans Mono"])


def apply_style() -> None:
    plt.rcParams.update({
        "font.family": SERIF, "svg.fonttype": "none",
        "figure.facecolor": PAPER, "axes.facecolor": PAPER, "savefig.facecolor": PAPER,
        "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
        "axes.edgecolor": INK, "axes.linewidth": 0.8, "axes.grid": False,
        "axes.spines.top": False, "axes.spines.right": False,
        "xtick.direction": "out", "ytick.direction": "out",
        "xtick.major.size": 4, "ytick.major.size": 4, "xtick.major.width": 0.8, "ytick.major.width": 0.8,
        "xtick.labelsize": 10.5, "ytick.labelsize": 10.5, "axes.labelsize": 11,
        "lines.solid_capstyle": "round", "lines.solid_joinstyle": "round",
    })


def _balanced(text: str, width: int) -> list[str]:
    """Greedy wrap at `width`; if that leaves a short orphan last line, balance the lines instead."""
    lines = textwrap.wrap(text, width)
    if len(lines) > 1 and len(lines[-1]) < 0.4 * width:
        n = len(lines)
        lines = textwrap.wrap(text, -(-len(text) // n) + 2)
    return lines


def _provenance(paths, plotted: str = "") -> str:
    parts = []
    for raw in paths:
        p = Path(raw)
        if p.is_file():
            data = p.read_bytes()
            rows = max(0, data.count(b"\n") - 1) if p.suffix in {".csv", ".tsv"} else None
            sha = hashlib.sha256(data).hexdigest()[:7]
            parts.append(f"{raw}  {'n=' + format(rows, ',') + '  ' if rows is not None else ''}sha {sha}")
        else:
            warnings.warn(f"template-charlie: source {raw!r} not found from {Path.cwd()}; no row count or hash recorded")
            parts.append(str(raw))
    if plotted:
        parts.append(f"plotted: {plotted}")
    return "   |   ".join(parts) if parts else "no data file recorded"


class Plate:
    """One figure. Build with axes(), annotate with mark()/note()/label(), then save()."""

    def __init__(self, headline: str, deck: str = "", number: int = 1, source=(), plotted: str = "",
                 size=(12.0, 6.75), notes: bool = True, label: str = "PLATE", drawn=True):
        """headline: the finding as one sentence, up to ~110 characters (wraps at 60 per line).
        deck: what is plotted and in what units, up to ~280 characters (wraps at 140).
        source: data file paths, resolved from the current directory (row count and hash are read from them).
        plotted: what subset is actually drawn ("16,830 started GPU jobs"); printed after the sources so the
            footer never implies the whole file was plotted.
        number: plate number; use 1 for a single plate. drawn: True stamps today's date, a string stamps
            that text, False omits it so a re-run with unchanged data gives an identical PNG."""
        apply_style()
        self.W, self.H = size
        self.number, self.label_word, self.has_notes = number, label, notes
        self.fig = plt.figure(figsize=size, facecolor=PAPER)
        self._axes: list = []
        self._notes: dict[int, str] = {}
        self._source, self._plotted, self._drawn = list(source), plotted, drawn
        self._chrome(headline, deck)

    # inch helpers: x from the left edge, y from the top edge
    def _fx(self, inch: float) -> float:
        return inch / self.W

    def _fy(self, inch_from_top: float) -> float:
        return 1 - inch_from_top / self.H

    def _line(self, x0, x1, y_top, lw, color=INK):
        self.fig.add_artist(Line2D([self._fx(x0), self._fx(x1)], [self._fy(y_top)] * 2,
                                   transform=self.fig.transFigure, lw=lw, color=color, solid_capstyle="butt"))

    def _chrome(self, headline: str, deck: str) -> None:
        f, left, right = self.fig, 0.6, self.W - 0.6
        for cx, cy in [(0.2, 0.2), (self.W - 0.2, 0.2), (0.2, self.H - 0.2), (self.W - 0.2, self.H - 0.2)]:
            sx, sy = (1 if cx < 1 else -1), (1 if cy < 1 else -1)  # crop marks, pointing inward
            f.add_artist(Line2D([self._fx(cx), self._fx(cx + 0.16 * sx)], [cy / self.H] * 2,
                                transform=f.transFigure, lw=0.7, color=RULE))
            f.add_artist(Line2D([self._fx(cx)] * 2, [cy / self.H, (cy + 0.16 * sy) / self.H],
                                transform=f.transFigure, lw=0.7, color=RULE))
        f.add_artist(Rectangle((self._fx(left), self._fy(0.42)), 0.30 / self.W, 0.075 / self.H,
                               transform=f.transFigure, fc=BRAND, ec="none"))
        f.text(self._fx(left + 0.42), self._fy(0.38), f"{self.label_word} {self.number:02d}", fontfamily=MONO,
               fontsize=8.5, color=INK2, va="center", ha="left")
        h = _balanced(headline, 60)
        y = 0.62
        for line in h:
            f.text(self._fx(left), self._fy(y), line, fontsize=23, fontweight="bold", va="top", ha="left")
            y += 0.40
        if deck:
            y += 0.04
            for line in _balanced(deck, 140):
                f.text(self._fx(left), self._fy(y), line, fontsize=12, fontstyle="italic", color=INK2, va="top", ha="left")
                y += 0.235
        y += 0.12
        self._line(left, right, y, 1.6)
        self._line(left, right, y + 0.045, 0.5)
        self._body_top = y + 0.38
        self._line(left, right, self.H - 0.66, 0.5, RULE)
        f.text(self._fx(left), self._fy(self.H - 0.42), _provenance(self._source, self._plotted), fontfamily=MONO,
               fontsize=7.2, color=MUTED, va="center", ha="left")
        stamp = "" if self._drawn is False else f"drawn {dt.date.today().isoformat() if self._drawn is True else self._drawn}  |  "
        f.text(self._fx(right), self._fy(self.H - 0.42), f"{stamp}template-charlie", fontfamily=MONO,
               fontsize=7.2, color=MUTED, va="center", ha="right")
        self._notes_x0 = right - 2.85 if self.has_notes else right
        self._body_right = (self._notes_x0 - 0.45) if self.has_notes else right

    def axes(self, nrows: int = 1, ncols: int = 1, left: float = 1.0, **gs_kw):
        """The main plotting area. Returns one Axes, or an array when nrows*ncols > 1.
        left: inches reserved for y tick labels. Category names longer than ~12 characters need 1.6 or more;
        text is never clipped, it runs off the page."""
        gs = self.fig.add_gridspec(
            nrows, ncols, left=self._fx(left), right=self._fx(self._body_right),
            top=self._fy(self._body_top), bottom=1.3 / self.H,
            **({"wspace": 0.18, "hspace": 0.35} | gs_kw))
        out = np.array([[self.fig.add_subplot(gs[r, c]) for c in range(ncols)] for r in range(nrows)])
        self._axes.extend(out.ravel())
        return out[0, 0] if out.size == 1 else (out.ravel() if min(nrows, ncols) == 1 else out)

    # ---- annotation ------------------------------------------------------
    def label(self, ax, x, y, text, color=INK, dx=8, dy=0, ha="left", va="center", size=11):
        """Direct label at a line end. The dot carries the color; the words stay ink.
        Two labels within ~20 px vertically will collide: nudge them apart with dy (points) or va."""
        ax.scatter([x], [y], s=34, color=color, edgecolor=PAPER, linewidth=1.4, zorder=5, clip_on=False)
        ax.annotate(text, (x, y), xytext=(dx if ha == "left" else -dx, dy), textcoords="offset points",
                    ha=ha, va=va, fontsize=size, fontstyle="italic", color=INK, annotation_clip=False)

    def mark(self, ax, x, y, n: int, dx=0, dy=24, ring=True, leader=None):
        """Numbered badge near the data, tied to margin note n by its number.
        Keep the badge off the data: dx/dy are offsets in points. ring=False for arrows and bars
        (which also drops the leader line unless leader=True)."""
        leader = ring if leader is None else leader
        if ring:
            ax.scatter([x], [y], s=70, facecolor="none", edgecolor=INK, linewidth=1.0, zorder=6, clip_on=False)
        ax.annotate(str(n), (x, y), xytext=(dx, dy), textcoords="offset points", ha="center", va="center",
                    fontsize=8.5, color=PAPER, fontfamily=MONO, zorder=7, annotation_clip=False,
                    bbox=dict(boxstyle="circle,pad=0.3", fc=INK, ec="none"),
                    arrowprops=dict(arrowstyle="-", color=INK, lw=0.8, shrinkA=7, shrinkB=7 if ring else 0) if leader else None)

    def note(self, n: int, text: str) -> None:
        self._notes[n] = text

    def _draw_notes(self) -> None:
        if not self._notes:
            return
        f, x0, y = self.fig, self._notes_x0, self._body_top
        limit = self.H - 0.85  # inches from top; the footer rule sits at H - 0.66
        for n in sorted(self._notes):
            lines = textwrap.wrap(self._notes[n], 34)
            if y + 0.205 * len(lines) > limit:
                raise ValueError(
                    f"template-charlie: note {n} runs past the footer. The margin holds about 3 notes of 3 to 4 lines "
                    f"(34 characters per line). Merge or shorten notes, or pass notes=False to Plate.")
            f.text(self._fx(x0 + 0.13), self._fy(y + 0.02), str(n), ha="center", va="center", fontsize=8.5,
                   color=PAPER, fontfamily=MONO, bbox=dict(boxstyle="circle,pad=0.3", fc=INK, ec="none"))
            for i, line in enumerate(lines):
                f.text(self._fx(x0 + 0.38), self._fy(y + 0.02 + i * 0.205), line, fontsize=10.5, va="center", ha="left")
            y += 0.205 * len(lines) + 0.34

    def _rangeframe(self, ax) -> None:
        """Axis lines span the data range: first tick to last tick, extended to the data if it runs past them
        (monthly date ticks end at Dec 1 while the data runs to Dec 31)."""
        for side, ticks, lim, dl in (("bottom", ax.get_xticks(), ax.get_xlim(), ax.dataLim.intervalx),
                                     ("left", ax.get_yticks(), ax.get_ylim(), ax.dataLim.intervaly)):
            if not ax.spines[side].get_visible():
                continue
            lo, hi = min(lim), max(lim)
            t = [v for v in ticks if lo - 1e-9 <= v <= hi + 1e-9]
            if len(t) < 2:
                continue
            a, b = min(t), max(t)
            if np.isfinite(dl).all():
                a, b = min(a, max(dl[0], lo)), max(b, min(dl[1], hi))
            ax.spines[side].set_bounds(a, b)

    def save(self, base: str | Path, dpi: int = 200) -> list[Path]:
        for ax in self._axes:
            self._rangeframe(ax)
        self._draw_notes()
        base = Path(base)
        base.parent.mkdir(parents=True, exist_ok=True)
        out = []
        for ext in ("png", "svg"):
            path = base.with_suffix(f".{ext}")
            self.fig.savefig(path, dpi=dpi)
            out.append(path)
        plt.close(self.fig)
        return out


# ---- forms that do not look like a default chart ----------------------------
def dotmatrix(ax, values, xlabels, ylabels, color=TEAL, vmax=None, max_area=200, key=None):
    """Grid of circles whose AREA encodes the value, on ledger rules. Replaces the heatmap."""
    values = np.asarray(values, dtype=float)
    vmax = vmax or values.max()
    ny, nx = values.shape
    for i in range(ny):
        ax.axhline(i, color=RULE, lw=0.6, zorder=0)
    xs, ys = np.meshgrid(np.arange(nx), np.arange(ny))
    ax.scatter(xs.ravel(), ys.ravel(), s=(values / vmax * max_area).ravel(), color=color, linewidth=0, zorder=2)
    ax.set_xlim(-0.7, nx - 0.3)
    ax.set_ylim(ny - 0.4, -0.6)
    ax.set_yticks(range(ny), ylabels)
    step = max(1, nx // 8)
    ax.set_xticks(range(0, nx, step), [xlabels[k] for k in range(0, nx, step)])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    if key:
        ax.text(1.0, 1.04, key, transform=ax.transAxes, ha="right", va="bottom", fontsize=9.5, color=MUTED, fontstyle="italic")
    return vmax


def dumbbell(ax, labels, start, end, colors=None, emphasis=None, fmt="{:.0f}%", badges=None):
    """One arrow per row from `start` (open circle) to `end` (arrow tip). Any pair works: before and after,
    failures excluding OOM vs all failures, plan vs actual. The value label sits after the tip.

    colors: per-row list of colors (default TEAL); emphasis: one row index drawn in ROSE;
    badges: {row_index: n} puts numbered badge n just after that row's value label.
    About 12 rows fit comfortably per panel at 12 x 6.75 in; with more, use a tall Plate size or split panels."""
    start, end = np.asarray(start, float), np.asarray(end, float)
    badges = badges or {}
    for i, (a, b) in enumerate(zip(start, end)):
        hot = emphasis is not None and i == emphasis
        col = ROSE if hot else (colors[i] if colors is not None else TEAL)
        ax.annotate("", xy=(b, i), xytext=(a, i), arrowprops=dict(arrowstyle="-|>", color=col, lw=2.0 if hot else 1.5,
                                                                   mutation_scale=11, shrinkA=3, shrinkB=0))
        ax.scatter([a], [i], s=36, facecolor=PAPER, edgecolor=col, linewidth=1.3, zorder=4)
        sign = -1 if b < a else 1
        text = fmt.format(b)
        ax.annotate(text, (b, i), xytext=(10 * sign, 0), textcoords="offset points", ha="right" if sign < 0 else "left",
                    va="center", fontsize=9.5, color=INK2, fontfamily=MONO, annotation_clip=False)
        if i in badges:
            off = sign * (10 + 6.0 * len(text) + 14)
            ax.annotate(str(badges[i]), (b, i), xytext=(off, 0), textcoords="offset points", ha="center", va="center",
                        fontsize=8.5, color=PAPER, fontfamily=MONO, zorder=7, annotation_clip=False,
                        bbox=dict(boxstyle="circle,pad=0.3", fc=INK, ec="none"))
    ax.set_yticks(range(len(labels)), labels)
    ax.set_ylim(len(labels) - 0.4, -0.7)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.grid(axis="y", color=RULE, lw=0.5)
    ax.set_axisbelow(True)


# ---- small helpers ------------------------------------------------------------
def headroom(ax, frac: float = 0.12) -> None:
    """Add headroom above the data so numbered badges at peaks stay inside the axes."""
    lo, hi = ax.get_ylim()
    if ax.get_yscale() == "log":
        ax.set_ylim(lo, hi * (hi / lo) ** frac)
    else:
        ax.set_ylim(lo, hi + (hi - lo) * frac)


def rolling_mean(y, window: int = 7) -> np.ndarray:
    """Trailing mean; the first window-1 values are NaN."""
    y = np.asarray(y, dtype=float)
    c = np.cumsum(np.insert(y, 0, 0.0))
    out = np.full(len(y), np.nan)
    out[window - 1:] = (c[window:] - c[:-window]) / window
    return out


def thin_thick(ax, x, y, color=TEAL, window: int = 7):
    """The day as a thin faint line under a thick trailing mean. Returns (x_last, mean_last) for label()."""
    x, y = np.asarray(x), np.asarray(y, dtype=float)
    ax.plot(x, y, color=color, lw=1.0, alpha=0.35)
    m = rolling_mean(y, window)
    ax.plot(x, m, color=color, lw=2.6)
    return x[-1], m[-1]


def shade(ax, x0, x1, label: str | None = None) -> None:
    """A quiet vertical band for an event or window. Name it with label, set in muted italic along the top."""
    ax.axvspan(x0, x1, color=BAND, lw=0, zorder=0)
    if label:
        ax.text(x0, 1.0, " " + label, transform=ax.get_xaxis_transform(), ha="left", va="top",
                fontsize=9.5, fontstyle="italic", color=MUTED)


def monthly(ax) -> None:
    """Month-start ticks labelled Jan, Feb, ... on a date axis."""
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
