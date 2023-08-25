---
title: autoarima
description: OpenBB Terminal Function
---

# autoarima

Perform Automatic ARIMA forecast: https://nixtla.github.io/statsforecast/examples/getting_started_with_auto_arima_and_ets.html

### Usage

```python
autoarima [--naive] [-d {}] [-c TARGET_COLUMN] [-n N_DAYS] [-s {N,A,M}] [-p SEASONAL_PERIODS] [-w START_WINDOW] [--end S_END_DATE] [--start S_START_DATE] [--residuals] [--forecast-only] [--export-pred-raw]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| naive | Show the naive baseline for a model. | False | True | None |
| target_dataset | The name of the dataset you want to select | None | True | None |
| target_column | The name of the specific column you want to use | close | True | None |
| n_days | prediction days. | 5 | True | None |
| seasonal | Seasonality: N: None, A: Additive, M: Multiplicative. | A | True | N, A, M |
| seasonal_periods | Seasonal periods: 4: Quarterly, 7: Daily | 7 | True | None |
| start_window | Start point for rolling training and forecast window. 0.0-1.0 | 0.85 | True | None |
| s_end_date | The end date (format YYYY-MM-DD) to select for testing | None | True | None |
| s_start_date | The start date (format YYYY-MM-DD) to select for testing | None | True | None |
| residuals | Show the residuals for the model. | False | True | None |
| forecast_only | Do not plot the historical data without forecasts. | False | True | None |
| export_pred_raw | Export predictions to a csv file. | False | True | None |


---

## Examples

```python
2022 Nov 07, 16:17 (🦋) /stocks/ $ forecast

2022 Nov 07, 16:17 (🦋) /forecast/ $ autoarima AAPL

Cross Validation Time Series 1: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 115/115 [00:2100:00,  5.31it/s]
Forecast: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:0000:00,  1.68it/s]
AutoARIMA obtains MAPE: 2.86% 


   Actual price: 138.38    
┏━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Datetime   ┃ Prediction ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2022-11-07 │ 138.43     │
├────────────┼────────────┤
│ 2022-11-08 │ 138.43     │
├────────────┼────────────┤
│ 2022-11-09 │ 138.43     │
├────────────┼────────────┤
│ 2022-11-10 │ 138.43     │
├────────────┼────────────┤
│ 2022-11-11 │ 138.43     │
└────────────┴────────────┘
```
---
