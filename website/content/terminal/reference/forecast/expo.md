---
title: expo
description: This page provides a comprehensive guide to the expo usage for executing
  a Probabilistic Exponential Smoothing forecast. Parameters and their usage are laid
  out, along with examples for reference.
keywords:
- Probabilistic Exponential Smoothing
- forecast
- expo
- trend
- dampen
- naive
- target_column
- n_days
- seasonal_periods
- start_window
- s_end_date
- s_start_date
- residuals
- forecast_only
- export_pred_raw
- parameters
- usage examples
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast /expo - Reference | OpenBB Terminal Docs" />

Perform Probabilistic Exponential Smoothing forecast: https://unit8co.github.io/darts/generated_api/darts.models.forecasting.exponential_smoothing.html

### Usage

```python wordwrap
expo [--trend {N,A,M}] [--dampen DAMPEN] [--naive] [-d {AAPL}] [-c TARGET_COLUMN] [-n N_DAYS] [-s {N,A,M}] [-p SEASONAL_PERIODS] [-w START_WINDOW] [--end S_END_DATE] [--start S_START_DATE] [--residuals] [--forecast-only] [--export-pred-raw] [--metric {rmse,mse,mape,smape}]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| trend | --trend | Trend: N: None, A: Additive, M: Multiplicative. | A | True | N, A, M |
| dampen | --dampen | Dampening | F | True | None |
| naive | --naive | Show the naive baseline for a model. | False | True | None |
| target_dataset | -d  --dataset | The name of the dataset you want to select | None | True | AAPL |
| target_column | -c  --target-column | The name of the specific column you want to use | close | True | None |
| n_days | -n  --n-days | prediction days. | 5 | True | None |
| seasonal | -s  --seasonal | Seasonality: N: None, A: Additive, M: Multiplicative. | A | True | N, A, M |
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

2022 Jul 23, 10:52 (🦋) /forecast/ $ expo GME
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 115/115 [00:1600:00,  6.80it/s]
Exponential smoothing obtains MAPE: 12.88%



       Actual price: $ 146.64
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Datetime            ┃ Prediction ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2022-07-19 00:00:00 │ $ 146.35   │
├─────────────────────┼────────────┤
│ 2022-07-20 00:00:00 │ $ 148.63   │
├─────────────────────┼────────────┤
│ 2022-07-21 00:00:00 │ $ 148.86   │
├─────────────────────┼────────────┤
│ 2022-07-22 00:00:00 │ $ 151.76   │
├─────────────────────┼────────────┤
│ 2022-07-25 00:00:00 │ $ 149.74   │
└─────────────────────┴────────────┘
```
![expo](https://user-images.githubusercontent.com/72827203/180615313-e45d6cb3-06a8-45aa-ae4e-505df07e7210.png)

---
