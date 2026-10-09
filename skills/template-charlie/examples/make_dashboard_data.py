"""Aggregate data/bikeshare into the three small CSVs the example dashboard reads.

    python skills/template-charlie/examples/make_dashboard_data.py [out-dir]
Default out-dir: skills/template-charlie/examples/dashboard/data
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

D = Path("data/bikeshare")
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "dashboard" / "data"
OUT.mkdir(parents=True, exist_ok=True)

t = pd.read_csv(D / "trips.csv", parse_dates=["start_time"])
d = pd.read_csv(D / "daily_summary.csv")
d[["date", "trips", "member_trips", "casual_trips", "mean_temp_c", "total_precip_mm"]].to_csv(OUT / "daily.csv", index=False)

ndays = pd.Series(pd.date_range("2025-01-01", "2025-12-31").dayofweek).value_counts()
h = t.assign(dow=t.start_time.dt.dayofweek, hour=t.start_time.dt.hour).groupby(["rider_type", "dow", "hour"]).size().reset_index(name="n")
h["avg_trips"] = (h.n / h.dow.map(ndays)).round(2)
h[["rider_type", "dow", "hour", "avg_trips"]].to_csv(OUT / "heat.csv", index=False)

t["eb"] = t.bike_type == "ebike"
t["half"] = np.where(t.start_time < "2025-07-01", "h1", "h2")
e = (t.groupby(["start_neighborhood", "half"]).eb.mean().unstack() * 100).round(3).reset_index()
e.columns = ["neighborhood", "h1", "h2"]
a = (t.groupby("half").eb.mean() * 100).round(3)
pd.concat([e, pd.DataFrame([{"neighborhood": "All trips", "h1": a.h1, "h2": a.h2}])]).to_csv(OUT / "ebike.csv", index=False)
print("wrote", *sorted(p.name for p in OUT.iterdir()))
