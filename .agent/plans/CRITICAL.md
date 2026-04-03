# CRITICAL: Missing Values in Final Parquet Files

## What is the problem?

Some patients arrived without certain vitals being recorded (e.g., unconscious, emergency arrival).
These cells are empty (NaN) in both `train_final.parquet` and `test_final.parquet`.

Right now, CatBoost handles them silently on its own — but we should handle them ourselves in the final parquet so the data is clean and consistent for any model we use.

## Which fields have missing values?

| Field | Missing in Train | Missing in Test | What it means |
|---|---|---|---|
| `systolic_bp` | 4,146 | 962 | Top blood pressure number |
| `diastolic_bp` | 4,146 | 962 | Bottom blood pressure number |
| `mean_arterial_pressure` | 4,146 | 962 | Average blood pressure |
| `pulse_pressure` | 4,146 | 962 | Difference between systolic and diastolic |
| `shock_index` | 4,146 | 962 | Heart rate ÷ systolic BP (derived from BP) |
| `respiratory_rate` | 3,067 | 752 | Breaths per minute |
| `temperature_c` | 574 | 106 | Body temperature in Celsius |

> Note: `systolic_bp`, `diastolic_bp`, `mean_arterial_pressure`, `pulse_pressure`, and `shock_index` are all missing for the **same 4,146 rows** — meaning those patients had no BP reading at all.

## What should we do?

Fill the missing values with the **median** of that column (calculated from train only, then applied to both train and test).

Median is better than average here because vitals can have extreme outliers (e.g., a very sick patient with BP of 60), and the median is not affected by those extremes.

### Steps:
1. Calculate the median of each missing column **from train only**
2. Fill train missing values with those medians
3. Fill test missing values with the **same train medians** (never use test data to calculate stats)
4. Save the filled data back to `train_final.parquet` and `test_final.parquet`

This should be done inside `feature_engineering.py` after merging and before saving the final parquets.
