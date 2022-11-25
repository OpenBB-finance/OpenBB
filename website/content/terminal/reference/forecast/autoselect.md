---
title: autoselect
description: OpenBB Terminal Function
---

# autoselect

Perform Automatic Statistical Forecast (select best statistical model from AutoARIMA, AutoETS, AutoCES, MSTL, ...)

### Usage

```python
autoselect [--naive] [-d {}] [-c TARGET_COLUMN] [-n N_DAYS] [-s {N,A,M}] [-p SEASONAL_PERIODS] [-w START_WINDOW] [--end S_END_DATE] [--start S_START_DATE] [--residuals] [--forecast-only] [--export-pred-raw]
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
2022 Nov 09, 15:23 (🦋) /forecast/ $ load AAPL

2022 Nov 09, 15:24 (🦋) /forecast/ $ autoselect AAPL

Cross Validation Time Series 1: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 115/115 [00:4700:00,  2.40it/s]
Forecast: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:0100:00,  1.80s/it]


  Performance per model.  
   Best model: AutoETS    
┏━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Model         ┃ MAPE   ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ AutoETS       │ 2.91%  │
├───────────────┼────────┤
│ AutoARIMA     │ 2.93%  │
├───────────────┼────────┤
│ RWD           │ 3.04%  │
├───────────────┼────────┤
│ AutoCES       │ 3.15%  │
├───────────────┼────────┤
│ MSTL          │ 3.40%  │
├───────────────┼────────┤
│ SeasonalNaive │ 4.32%  │
├───────────────┼────────┤
│ SeasWA        │ 8.06%  │
└───────────────┴────────┘

   Actual price: 139.50    
┏━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Datetime   ┃ Prediction ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2022-11-09 │ 139.47     │
├────────────┼────────────┤
│ 2022-11-10 │ 139.47     │
├────────────┼────────────┤
│ 2022-11-11 │ 139.47     │
├────────────┼────────────┤
│ 2022-11-14 │ 139.47     │
├────────────┼────────────┤
│ 2022-11-15 │ 139.47     │
└────────────┴────────────┘
```
---
