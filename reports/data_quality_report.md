# Data Quality Report

Source: clean `sales_transactions.csv`

- Shape: 9,972,038 rows × 11 columns
- Date range: 2022-01-01 to 2025-12-31
- Unique SKUs: 5,000
- Missing values in selected pipeline columns: {'date': 0, 'sku_id': 0, 'quantity': 0, 'unit_price': 0, 'total_value': 0, 'discount_pct': 0, 'promo_id': 7881687}
- Duplicate rows: not calculated across the 10M-row raw file to preserve memory; the pipeline aggregates valid date/SKU/quantity records.

## Data Mapping

| FORESIGHT field | Actual dataset field | Status |
|---|---|---|
| SKU | `sales_transactions.sku_id` | Available |
| Date | `sales_transactions.date` | Available |
| Units sold | `sales_transactions.quantity` | Available |
| Revenue | `sales_transactions.total_value` | Available |
| Price | `sales_transactions.unit_price`; `sku_master.unit_price` | Available |
| Category | `sku_master.category` | Available |
| Promotion | `promo_id`, `discount_pct`; `promotions.csv` | Available |
| Inventory | `inventory_snapshot.stock_on_hand`, `reorder_point`, `safety_stock` | Available (snapshot, not history) |
| On order | — | Not available |

