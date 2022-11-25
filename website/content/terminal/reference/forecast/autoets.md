---
title: autoets
description: OpenBB Terminal Function
---

# autoets

Perform Automatic ETS (Error, Trend, Seasonality) forecast: https://nixtla.github.io/statsforecast/examples/getting_started_with_auto_arima_and_ets.html

### Usage

```python
autoets [--naive] [-d {}] [-c TARGET_COLUMN] [-n N_DAYS] [-s {N,A,M}] [-p SEASONAL_PERIODS] [-w START_WINDOW] [--end S_END_DATE] [--start S_START_DATE] [--residuals] [--forecast-only] [--export-pred-raw]
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
2022 Oct 21, 18:20 (🦋) /forecast/ $ load AAPL

2022 Oct 21, 18:21 (🦋) /forecast/ $ autoets AAPL



   Actual price: 143.39
┏━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Datetime   ┃ Prediction ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2022-10-21 │ 143.42     │
├────────────┼────────────┤
│ 2022-10-24 │ 143.42     │
├────────────┼────────────┤
│ 2022-10-25 │ 143.42     │
├────────────┼────────────┤
│ 2022-10-26 │ 143.42     │
├────────────┼────────────┤
│ 2022-10-27 │ 143.42     │
└────────────┴────────────┘
```
![autoets](https://user-images.githubusercontent.com/10517170/197297075-d141d735-0b35-43cc-bf4f-e746b6b1001e.png)

---
