"""Leakage-safe feature construction."""
import pandas as pd
LAGS=[1,2,4,8]
def make_features(weekly: pd.DataFrame) -> pd.DataFrame:
    df=weekly.copy(); df["week"]=pd.to_datetime(df["week"]); df=df.sort_values(["sku_id","week"])
    g=df.groupby("sku_id", group_keys=False)["demand"]
    for lag in LAGS: df[f"lag_{lag}"]=g.shift(lag)
    shifted=g.shift(1)
    for window in [4,8]:
        df[f"rolling_mean_{window}"]=shifted.groupby(df["sku_id"]).transform(lambda s:s.rolling(window, min_periods=window).mean())
    df["rolling_std_4"]=shifted.groupby(df["sku_id"]).transform(lambda s:s.rolling(4,min_periods=4).std())
    df["week_number"]=df.week.dt.isocalendar().week.astype(int); df["month"]=df.week.dt.month; df["quarter"]=df.week.dt.quarter
    return df
