---
title: regr
description: This page provides a comprehensive guide on how to carry out a regression
  forecast using regr function in darts.models. Parameters such as past covariates,
  prediction days, train split, target dataset, and output chunk length are explained
  in great detail. Examples and usage documentation are also provided to aid in understanding.
keywords:
- regression forecast
- darts.models
- forecasting model
- regr function
- regr parameters
- past covariates
- prediction days
- train split
- forecast chunk length
- forecasting tool
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast /regr - Reference | OpenBB Terminal Docs" />

Perform a regression forecast: https://unit8co.github.io/darts/generated_api/darts.models.forecasting.regression_model.html

### Usage

```python wordwrap
regr [--past-covariates PAST_COVARIATES] [--all-past-covariates] [--naive] [-d {AAPL}] [-c TARGET_COLUMN] [-n N_DAYS] [-t TRAIN_SPLIT] [-o OUTPUT_CHUNK_LENGTH] [--end S_END_DATE] [--start S_START_DATE] [--lags LAGS] [--residuals] [--forecast-only] [--explainability-raw] [--export-pred-raw] [--metric {rmse,mse,mape,smape}]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| past_covariates | --past-covariates | Past covariates(columns/features) in same dataset. Comma separated. | None | True | None |
| all_past_covariates | --all-past-covariates | Adds all rows as past covariates except for date and the target column. | False | True | None |
| naive | --naive | Show the naive baseline for a model. | False | True | None |
| target_dataset | -d  --dataset | The name of the dataset you want to select | None | True | AAPL |
| target_column | -c  --target-column | The name of the specific column you want to use | close | True | None |
| n_days | -n  --n-days | prediction days. | 5 | True | None |
| train_split | -t  --train-split | Start point for rolling training and forecast window. 0.0-1.0 | 0.85 | True | None |
| output_chunk_length | -o  --output-chunk-length | The length of the forecast of the model. | 5 | True | None |
| s_end_date | --end | The end date (format YYYY-MM-DD) to select for testing | None | True | None |
| s_start_date | --start | The start date (format YYYY-MM-DD) to select for testing | None | True | None |
| lags | --lags | Lagged target values used to predict the next time step. | 14 | True | None |
| residuals | --residuals | Show the residuals for the model. | False | True | None |
| forecast_only | --forecast-only | Do not plot the historical data without forecasts. | False | True | None |
| explainability_raw | --explainability-raw | Prints out a raw dataframe showing explainability results. | False | True | None |
| export_pred_raw | --export-pred-raw | Export predictions to a csv file. | False | True | None |
| metric | --metric | Calculate precision based on a specific metric (rmse, mse, mape) | mape | True | rmse, mse, mape, smape |


---

## Examples

```python
2022 Jul 23, 10:36 (🦋) /forecast/ $ load GME_20220719_123734.csv -a GME

2022 Jul 23, 11:08 (🦋) /forecast/ $ regr GME
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 115/115 [00:0100:00, 111.85it/s]
Regression model obtains MAPE: 12.34%



       Actual price: $ 146.64
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Datetime            ┃ Prediction ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2022-07-19 00:00:00 │ $ 143.74   │
├─────────────────────┼────────────┤
│ 2022-07-20 00:00:00 │ $ 144.90   │
├─────────────────────┼────────────┤
│ 2022-07-21 00:00:00 │ $ 142.41   │
├─────────────────────┼────────────┤
│ 2022-07-22 00:00:00 │ $ 133.50   │
├─────────────────────┼────────────┤
│ 2022-07-25 00:00:00 │ $ 134.24   │
└─────────────────────┴────────────┘
```
![regr](https://user-images.githubusercontent.com/72827203/180615346-82fae367-d0cc-4d78-be30-b947a83df909.png)

---
