---
title: theta
description: OpenBB Terminal Function
---

# theta

Perform Theta forecast: https://unit8co.github.io/darts/generated_api/darts.models.forecasting.theta.html

### Usage

```python
theta [--naive] [-d {}] [-c TARGET_COLUMN] [-n N_DAYS] [-s {N,A,M}] [-p SEASONAL_PERIODS] [-w START_WINDOW] [--end S_END_DATE] [--start S_START_DATE] [--residuals] [--forecast-only] [--export-pred-raw]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| naive | Show the naive baseline for a model. | False | True | None |
| target_dataset | The name of the dataset you want to select | None | True | None |
| target_column | The name of the specific column you want to use | close | True | None |
| n_days | prediction days. | 5 | True | None |
| seasonal | Seasonality: N: None, A: Additive, M: Multiplicative. | M | True | N, A, M |
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
2022 Jul 23, 10:36 (🦋) /forecast/ $ load GME_20220719_123734.csv -a GME

2022 Jul 23, 11:01 (🦋) /forecast/ $ theta GME
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 115/115 [00:2300:00,  4.88it/s]
Theta Model obtains MAPE: 12.71%



       Actual price: $ 146.64
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Datetime            ┃ Prediction ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2022-07-19 00:00:00 │ $ 145.41   │
├─────────────────────┼────────────┤
│ 2022-07-20 00:00:00 │ $ 147.28   │
├─────────────────────┼────────────┤
│ 2022-07-21 00:00:00 │ $ 147.28   │
├─────────────────────┼────────────┤
│ 2022-07-22 00:00:00 │ $ 148.66   │
├─────────────────────┼────────────┤
│ 2022-07-25 00:00:00 │ $ 147.18   │
└─────────────────────┴────────────┘
```
![theta](https://user-images.githubusercontent.com/72827203/180615324-5b50445c-cc95-4efa-84a6-85e85ddc2d28.png)

---
