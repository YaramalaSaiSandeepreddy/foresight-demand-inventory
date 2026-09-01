"""Time-aware global forecasting and eight-week recursive forecasts."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import joblib, numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from features import make_features
FEATURES=["lag_1","lag_2","lag_4","lag_8","rolling_mean_4","rolling_mean_8","rolling_std_4","week_number","month","quarter"]
def metrics(actual, pred):
    return {"wape": float(np.abs(actual-pred).sum()/np.abs(actual).sum()), "mae":float(mean_absolute_error(actual,pred)), "rmse":float(mean_squared_error(actual,pred)**.5), "bias":float((pred-actual).sum()/np.abs(actual).sum())}
def run(weekly_path, model_path, outputs_dir):
    weekly=pd.read_csv(weekly_path, parse_dates=["week"]); feat=make_features(weekly).dropna(subset=FEATURES)
    cutoff=feat.week.max()-pd.Timedelta(weeks=12); train=feat[feat.week<=cutoff]; test=feat[feat.week>cutoff]
    baseline=test["lag_8"].to_numpy() # 8-week repeating cycle: weekly series has < 4 years; reliable enough, documented
    base=metrics(test.demand.to_numpy(), baseline)
    model=HistGradientBoostingRegressor(max_iter=160, learning_rate=.08, max_leaf_nodes=31, l2_regularization=1.0, random_state=42)
    # A deterministic cap keeps the global model fast enough for a one-day demo.
    fit_train=train.sample(n=min(len(train), 300_000), random_state=42)
    model.fit(fit_train[FEATURES], fit_train.demand)
    pred=np.clip(model.predict(test[FEATURES]),0,None); ml=metrics(test.demand.to_numpy(),pred)
    results=pd.DataFrame([{"model":"Seasonal naive (8-week lag)",**base},{"model":"HistGradientBoostingRegressor",**ml}]); outputs_dir.mkdir(parents=True, exist_ok=True); results.to_csv(outputs_dir.parent/"reports"/"model_results.csv",index=False)
    chosen="ml" if ml["wape"]<=base["wape"] else "baseline"; final_model=model if chosen=="ml" else None
    joblib.dump({"model":final_model,"features":FEATURES,"selected_model":chosen,"baseline_lag":8,"metrics":{"baseline":base,"ml":ml}},model_path)
    history=weekly[["sku_id","week","demand"]].copy(); last=history.week.max(); forecasts=[]
    for step in range(1,9):
        nextweek=last+pd.Timedelta(weeks=step); combined=make_features(history)
        rows=combined[combined.week==nextweek] # none; construct rows from history by append zero then features
        filler=pd.DataFrame({"sku_id":history.sku_id.unique(),"week":nextweek,"demand":0.0})
        temp=make_features(pd.concat([history,filler],ignore_index=True)); candidates=temp[temp.week==nextweek].copy()
        if chosen=="ml": y=np.clip(final_model.predict(candidates[FEATURES].fillna(0)),0,None)
        else: y=candidates["lag_8"].fillna(candidates["rolling_mean_4"]).fillna(0).to_numpy()
        filler["demand"]=y; forecasts.append(filler.rename(columns={"week":"forecast_week","demand":"forecast_demand"})); history=pd.concat([history,filler],ignore_index=True)
    forecast=pd.concat(forecasts,ignore_index=True); forecast.to_csv(outputs_dir/"forecast.csv",index=False)
    return results, chosen
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--weekly",default="data/processed/weekly_demand.csv");p.add_argument("--model",default="models/forecast_model.joblib");p.add_argument("--outputs",default="outputs");a=p.parse_args();Path(a.model).parent.mkdir(parents=True,exist_ok=True);print(run(a.weekly,a.model,Path(a.outputs))[0])
