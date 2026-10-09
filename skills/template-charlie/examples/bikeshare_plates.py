"""Three plates from data/bikeshare. Run from a folder that contains data/bikeshare:

    python skills/template-charlie/examples/bikeshare_plates.py [out-dir]

Read this file before drawing your own plate: it shows the whole pattern.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from plate import (AMBER, INK2, ROSE, TEAL, Plate, dotmatrix, dumbbell, headroom, monthly,  # noqa: E402
                   shade, thin_thick)

DATA = Path("data/bikeshare")
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("plates")
trips = pd.read_csv(DATA / "trips.csv", parse_dates=["start_time"])
weather = pd.read_csv(DATA / "weather.csv", parse_dates=["datetime"])
SRC = [str(DATA / "trips.csv")]


def plate_rhythm():
    t = trips.assign(dow=trips.start_time.dt.dayofweek, hour=trips.start_time.dt.hour)
    ndays = pd.Series(pd.date_range("2025-01-01", "2025-12-31").dayofweek).value_counts()
    p = Plate(number=1, headline="Members ride to work. Casual riders ride on weekends.",
              deck="Average trips per hour by weekday and hour of day, 2025. Circle area is proportional to trips, on one scale for both panels.", source=SRC)
    axes = p.axes(1, 2, wspace=0.08)
    mats = {}
    for rt in ("member", "casual"):
        g = t[t.rider_type == rt].groupby(["dow", "hour"]).size().unstack(fill_value=0)
        mats[rt] = g.div(ndays.reindex(g.index).values, axis=0).values
    vmax = max(m.max() for m in mats.values())
    hours = [f"{h}:00" for h in range(24)]
    for ax, rt, col in zip(axes, ("member", "casual"), (TEAL, AMBER)):
        dotmatrix(ax, mats[rt], hours, ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], color=col, vmax=vmax,
                  key="largest circle = 41 trips an hour" if rt == "member" else None)
        ax.set_title(rt.capitalize() + " riders", loc="left", fontsize=12.5, fontweight="bold", color=INK2, pad=10)
    axes[1].set_yticklabels([])
    p.mark(axes[0], 8, 0, 1, dy=-26)
    p.mark(axes[1], 13, 5, 2, dy=-30)
    p.note(1, "Members peak in the 8 am and 5 pm hours, at about 37 and 39 trips an hour on weekdays. Weekends flatten to a midday plateau.")
    p.note(2, "Casual riders are 32% of trips and 47% of theirs fall on a weekend, peaking in the 1 pm hour at 27 trips an hour.")
    p.note(3, "One scale for both panels, so casual circles are smaller everywhere.")
    return p.save(OUT / "plate01_rhythm")


def plate_weather():
    h = trips.assign(h=trips.start_time.dt.floor("h")).groupby(["h", "rider_type"]).size().unstack(fill_value=0)
    w = weather.set_index("datetime").join(h).fillna({"member": 0, "casual": 0})
    w = w[(w.index.hour >= 8) & (w.index.hour < 20)]
    dry = w[w.precip_mm < 0.1].assign(bin=lambda d: pd.cut(d.temp_c, [-5, 8, 11, 14, 17, 20, 23, 40],
                                                         labels=["<8", "8-11", "11-14", "14-17", "17-20", "20-23", ">23"]))
    m = dry.groupby("bin", observed=True)[["member", "casual"]].mean()
    idx = 100 * m / m.loc["17-20"]
    p = Plate(number=2, headline="Casual riders at 8 to 11 degrees ride at 35% of normal.",
              deck="Trips per daytime hour in dry weather, indexed to the 17 to 20 degree bin (= 100). "
                   "Indexed because the two rider types differ in volume.", source=SRC + [str(DATA / "weather.csv")])
    ax = p.axes()
    x = np.arange(len(idx))
    for rt, col, name in (("member", TEAL, "Members"), ("casual", AMBER, "Casual riders")):
        ax.plot(x, idx[rt], color=col, lw=2.2)
        p.label(ax, x[-1], idx[rt].iloc[-1], name, col, dx=10)
    ax.axhline(100, color="#8f887b", lw=0.6, ls=(0, (1, 3)))
    ax.set_xticks(x, idx.index)
    ax.set_xlabel("air temperature, degrees C")
    ax.set_ylabel("trips per hour, index")
    ax.set_ylim(0, 125)
    ax.set_xlim(-0.2, len(idx) - 0.3)
    p.mark(ax, 1, idx["casual"].iloc[1], 1, dx=-30, dy=8)
    p.mark(ax, 0, idx["casual"].iloc[0], 2, dx=34, dy=-16)
    p.note(1, "Casual riders at 8 to 11 degrees ride at 35% of their rate at 17 to 20. Members ride at 91%.")
    p.note(2, "Below 8 degrees casual riding is 14% of normal. Members barely move: 101%.")
    return p.save(OUT / "plate02_weather")


def plate_paradox():
    t = trips.assign(half=np.where(trips.start_time < "2025-07-01", "H1", "H2"), eb=trips.bike_type == "ebike")
    by = (t.groupby(["start_neighborhood", "half"]).eb.mean().unstack() * 100).dropna()
    overall = t.groupby("half").eb.mean() * 100
    by = by.sort_values("H2")
    labels = list(by.index) + ["All trips"]
    a = list(by.H1) + [overall.H1]
    b = list(by.H2) + [overall.H2]
    harbor = (t[t.half == "H2"].start_neighborhood == "Harbor Flats").mean() * 100
    p = Plate(number=3, headline="Every neighborhood gained e-bikes. The city-wide share fell.",
              deck="Share of trips on e-bikes, January to June (open circle) to July to December (arrow tip).",
              source=SRC)
    ax = p.axes()
    dumbbell(ax, labels, a, b, emphasis=len(labels) - 1, badges={len(labels) - 1: 1, 0: 2})
    ax.set_xlim(10, 66)
    ax.set_xlabel("% of trips on e-bikes")
    ax.axhline(len(labels) - 1.5, color=INK2, lw=0.6)
    p.note(1, f"City-wide: {a[-1]:.1f}% to {b[-1]:.1f}%, a fall of {a[-1] - b[-1]:.1f} points, while every neighborhood above it rose.")
    gains = by.H2 - by.H1
    p.note(2, f"Each neighborhood gained {gains.min():.1f} to {gains.max():.1f} points. Harbor Flats is absent from the first half because it opened on July 1.")
    p.note(3, f"Harbor Flats rides few e-bikes and took {harbor:.0f}% of second-half trips. The mix changed; riders did not.")
    return p.save(OUT / "plate03_paradox")


def plate_daily():
    daily = pd.read_csv(DATA / "daily_summary.csv", parse_dates=["date"])
    x = daily.date.to_numpy()
    strike = daily[(daily.date >= "2025-03-18") & (daily.date <= "2025-03-20")]
    festival = daily.loc[daily.casual_trips.idxmax()]
    before = daily[(daily.date < "2025-03-18") & (daily.date.dt.dayofweek.isin([1, 2, 3]))].tail(12)
    p = Plate(number=4, headline="Two days broke the pattern: a transit strike and a festival.",
              deck="Trips per day (thin) and trailing 7-day mean (thick), 2025. The band marks the three strike days.",
              source=[str(DATA / "daily_summary.csv")])
    ax = p.axes()
    for col, color, name, dy in (("member_trips", TEAL, "Members", 0), ("casual_trips", AMBER, "Casual riders", 0)):
        xl, yl = thin_thick(ax, x, daily[col].values, color)
        p.label(ax, xl, yl, name, color, dx=10, dy=dy)
    shade(ax, strike.date.iloc[0].to_pydatetime(), strike.date.iloc[-1].to_pydatetime(), "strike")
    monthly(ax)
    ax.set_ylabel("trips per day")
    ax.set_ylim(0, 500)
    headroom(ax, 0.10)
    ax.set_xlim(x[0], x[-1])
    peak = strike.loc[strike.member_trips.idxmax()]
    p.mark(ax, peak.date.to_pydatetime(), peak.member_trips, 1, dx=-34, dy=8)
    p.mark(ax, festival.date.to_pydatetime(), festival.casual_trips, 2, dx=30, dy=8)
    ratio = strike.member_trips.mean() / before.member_trips.mean()
    p.note(1, f"Over the three strike days members averaged {strike.member_trips.mean():.0f} trips, {ratio:.1f} times the usual Tuesday to Thursday.")
    p.note(2, f"{festival.date:%B} {festival.date.day}: {festival.casual_trips:.0f} casual trips, {festival.casual_trips / daily.casual_trips.median():.1f} times a median day.")
    return p.save(OUT / "plate04_daily")


if __name__ == "__main__":
    for fn in (plate_rhythm, plate_weather, plate_paradox, plate_daily):
        print(*fn())
