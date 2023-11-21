---
title: theta
description: This page provides a detailed guide on how to perform a Theta forecast
  using Python. Parameters with their descriptions and the process of exporting predictions
  to a CSV file are covered as well.
keywords:
- Theta forecast
- Predictive Modelling
- Historical Data
- Seasonality
- Forecasting
- Model Parameters
- Profit Forecast
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast /theta - Reference | OpenBB Terminal Docs" />

Perform Theta forecast: https://unit8co.github.io/darts/generated_api/darts.models.forecasting.theta.html

### Usage

```python wordwrap
theta [--naive] [-d {AAPL}] [-c TARGET_COLUMN] [-n N_DAYS] [-s {N,A,M}] [-p SEASONAL_PERIODS] [-w START_WINDOW] [--end S_END_DATE] [--start S_START_DATE] [--residuals] [--forecast-only] [--export-pred-raw] [--metric {rmse,mse,mape,smape}]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| naive | --naive | Show the naive baseline for a model. | False | True | None |
| target_dataset | -d  --dataset | The name of the dataset you want to select | None | True | AAPL |
| target_column | -c  --target-column | The name of the specific column you want to use | close | True | None |
| n_days | -n  --n-days | prediction days. | 5 | True | None |
| seasonal | -s  --seasonal | Seasonality: N: None, A: Additive, M: Multiplicative. | M | True | N, A, M |
| seasonal_periods | -p  --periods | Seasonal periods: 4: Quarterly, 7: Daily | 7 | True | None |
| start_window | -w  --window | Start point for rolling training and forecast window. 0.0-1.0 | 0.85 | True | None |
| s_end_date | --end | The end date (format YYYY-MM-DD) to select for testing | None | True | None |
| s_start_date | --start | The start date (format YYYY-MM-DD) to select for testing | None | True | None |
| residuals | --residuals | Show the residuals for the model. | False | True | None |
| forecast_only | --forecast-only | Do not plot the historical data without forecasts. | False | True | None |
| export_pred_raw | --export-pred-raw | Export predictions to a csv file. | False | True | None |
| metric | --metric | Calculate precision based on a specific metric (rmse, mse, mape) | mape | True | rmse, mse, mape, smape |


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
