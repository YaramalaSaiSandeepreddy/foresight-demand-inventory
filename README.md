# Project FORESIGHT

Demand & Inventory Intelligence for NorthBay Living.

## Business Problem

NorthBay Living needs a clear weekly SKU demand forecast and inventory decisions that can be demonstrated without claiming unsupported data.

## Objective

Forecast eight weeks of SKU demand, benchmark against seasonal naive demand, calculate WAPE, and turn the supplied inventory snapshot into reorder / markdown recommendations.

## Dataset

Uses the supplied clean synthetic retail dataset: 10M transactions, 5,000 SKUs, 30 stores, 2022–2025. See `reports/data_quality_report.md` for the measured audit and mapping.

## Data Pipeline

`src/pipeline.py` reads only required columns in chunks and aggregates immediately to `data/processed/weekly_demand.csv` (`sku_id`, `week`, `demand`, `revenue`).

## Forecasting, Baseline & WAPE

`src/features.py` creates shifted lags (1, 2, 4, 8), shifted rolling features, and calendar features; shifted calculations prevent future leakage. `src/forecast.py` holds out the final 12 weeks, evaluates an 8-week seasonal-naive baseline versus a global `HistGradientBoostingRegressor`, selects the lower-WAPE method, saves the model, and recursively produces eight future weeks. Actual results are in `reports/model_results.csv`.

WAPE = sum(abs(actual − forecast)) / sum(abs(actual)).

## Risk Scoring

`src/risk.py` joins the supplied `inventory_snapshot.csv` and SKU cost/price data. It uses a documented **two-week lead-time assumption** (25% of the 8-week forecast); there is no inventory history or on-order field in the source. `sales_at_risk` and `capital_locked` are calculated estimates, not raw source fields.

## Dashboard

Run `streamlit run app/streamlit_app.py`. It provides Overview, Forecast, Risk, Decision Grid, and Insights pages and loads the saved model rather than retraining.

## How to Run

```text
python src/pipeline.py --raw work/extracted/retail_clean_dataset/sales_transactions.csv
python src/forecast.py
python src/risk.py --inventory work/extracted/retail_clean_dataset/inventory_snapshot.csv --sku work/extracted/retail_clean_dataset/sku_master.csv
python scripts/generate_reports.py
streamlit run app/streamlit_app.py
```

## Project Structure

`data/processed` holds compact modeling data; `src` contains the pipeline, features, forecast, and risk modules; `outputs` contains forecast and risk CSVs; `reports` contains evidence and charts; `models` holds the saved model; `app` holds Streamlit.

## Limitations & Future Improvements

The dataset is synthetic. Inventory is a snapshot and on-order quantities / lead times are unavailable. Production use should add live inventory history, supplier lead times, order pipeline, stockout censored-demand adjustment, and retraining monitoring.
