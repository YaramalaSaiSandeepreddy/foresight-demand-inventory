"""Memory-efficient preparation of weekly SKU demand for Project FORESIGHT."""
from __future__ import annotations
import argparse, json
from collections import defaultdict
from pathlib import Path
import pandas as pd

REQUIRED = ["date", "sku_id", "quantity", "unit_price", "total_value", "discount_pct", "promo_id"]

def build_weekly(raw_path: Path, out_dir: Path, chunksize: int = 250_000) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    demand, revenue = defaultdict(float), defaultdict(float)
    row_count = 0; missing = defaultdict(int); date_min = None; date_max = None
    for chunk in pd.read_csv(raw_path, usecols=REQUIRED, chunksize=chunksize):
        row_count += len(chunk)
        for col, n in chunk.isna().sum().items(): missing[col] += int(n)
        chunk["date"] = pd.to_datetime(chunk["date"], errors="coerce")
        valid = chunk.dropna(subset=["date", "sku_id", "quantity"])
        if not valid.empty:
            current_min, current_max = valid.date.min(), valid.date.max()
            date_min = current_min if date_min is None or current_min < date_min else date_min
            date_max = current_max if date_max is None or current_max > date_max else date_max
            valid = valid[valid.quantity >= 0].copy()
            valid["week"] = valid.date.dt.to_period("W-SUN").apply(lambda p: p.start_time)
            grouped = valid.groupby(["sku_id", "week"], observed=True).agg(demand=("quantity", "sum"), revenue=("total_value", "sum")).reset_index()
            # Iterating compact NumPy arrays avoids a per-row pandas Series allocation.
            for sku, week, units, sales in grouped.itertuples(index=False, name=None):
                key=(sku, week); demand[key] += float(units); revenue[key] += float(sales)
    weekly = pd.DataFrame([(s, w, v, revenue[(s,w)]) for (s,w),v in demand.items()], columns=["sku_id", "week", "demand", "revenue"])
    weekly = weekly.sort_values(["sku_id", "week"])
    weekly.to_csv(out_dir / "weekly_demand.csv", index=False)
    audit = {"filename": raw_path.name, "rows": row_count, "columns": 11, "processed_rows": len(weekly), "unique_skus": int(weekly.sku_id.nunique()), "date_range": [str(date_min.date()), str(date_max.date())], "missing_values": dict(missing), "total_units": float(weekly.demand.sum()), "total_revenue": float(weekly.revenue.sum())}
    (out_dir / "pipeline_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    return audit

if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("--raw", required=True); p.add_argument("--out", default="data/processed"); p.add_argument("--chunksize", type=int, default=250000)
    args=p.parse_args(); print(json.dumps(build_weekly(Path(args.raw), Path(args.out), args.chunksize), indent=2))
