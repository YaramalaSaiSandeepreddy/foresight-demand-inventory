"""Inventory risk scores using supplied inventory snapshot data."""
import argparse
from pathlib import Path
import numpy as np,pandas as pd
def score(forecast_path, inventory_path, sku_path, out_path):
    fc=pd.read_csv(forecast_path); forward=fc.groupby("sku_id",as_index=False).forecast_demand.sum().rename(columns={"forecast_demand":"forecast_demand"})
    inv=pd.read_csv(inventory_path).groupby("sku_id",as_index=False).agg(on_hand=("stock_on_hand","sum"), reorder_point=("reorder_point","sum"), safety_stock=("safety_stock","sum"))
    sku=pd.read_csv(sku_path,usecols=["sku_id","category","unit_price","cost_price"])
    d=forward.merge(inv,on="sku_id",how="left").merge(sku,on="sku_id",how="left"); d[["on_hand","reorder_point","safety_stock"]]=d[["on_hand","reorder_point","safety_stock"]].fillna(0)
    lead=d.forecast_demand*0.25 # 2 weeks / 8-week horizon; explicit documented operating assumption
    d["stockout_risk"]=(1-(d.on_hand/(lead+d.safety_stock+1))).clip(0,1); d["overstock_risk"]=((d.on_hand-d.forecast_demand)/(d.forecast_demand+1)).clip(0,1)
    hi_s=d.stockout_risk>=.5; hi_o=d.overstock_risk>=.5
    d["risk_level"]=np.select([hi_s&~hi_o,~hi_s&hi_o,hi_s&hi_o],["High stockout","High overstock","Volatile"],default="Healthy")
    d["recommended_action"]=np.select([hi_s&~hi_o,~hi_s&hi_o,hi_s&hi_o],["REORDER NOW","MARKDOWN / CLEAR","WATCH / VOLATILE"],default="HEALTHY")
    d["sales_at_risk"]=(np.maximum(0,lead+d.safety_stock-d.on_hand)*d.unit_price).round(2); d["capital_locked"]=(np.maximum(0,d.on_hand-d.forecast_demand)*d.cost_price).round(2)
    d.to_csv(out_path,index=False); return d
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--forecast",default="outputs/forecast.csv");p.add_argument("--inventory",required=True);p.add_argument("--sku",required=True);p.add_argument("--out",default="outputs/risk_scores.csv");a=p.parse_args();score(a.forecast,a.inventory,a.sku,a.out)
