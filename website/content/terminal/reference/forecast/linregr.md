---
title: linregr
description: OpenBB Terminal Function
---

# linregr

Perform a linear regression forecast: https://unit8co.github.io/darts/generated_api/darts.models.forecasting.linear_regression_model.html

### Usage

```python
linregr [--past-covariates PAST_COVARIATES] [--all-past-covariates] [--naive] [-d {}] [-c TARGET_COLUMN] [-n N_DAYS] [-t TRAIN_SPLIT] [-o OUTPUT_CHUNK_LENGTH] [--end S_END_DATE] [--start S_START_DATE] [--lags LAGS] [--residuals] [--forecast-only] [--explainability-raw] [--export-pred-raw]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| past_covariates | Past covariates(columns/features) in same dataset. Comma separated. | None | True | None |
| all_past_covariates | Adds all rows as past covariates except for date and the target column. | False | True | None |
| naive | Show the naive baseline for a model. | False | True | None |
| target_dataset | The name of the dataset you want to select | None | True | None |
| target_column | The name of the specific column you want to use | close | True | None |
| n_days | prediction days. | 5 | True | None |
| train_split | Start point for rolling training and forecast window. 0.0-1.0 | 0.85 | True | None |
| output_chunk_length | The length of the forecast of the model. | 5 | True | None |
| s_end_date | The end date (format YYYY-MM-DD) to select for testing | None | True | None |
| s_start_date | The start date (format YYYY-MM-DD) to select for testing | None | True | None |
| lags | Lagged target values used to predict the next time step. | 14 | True | None |
| residuals | Show the residuals for the model. | False | True | None |
| forecast_only | Do not plot the historical data without forecasts. | False | True | None |
| explainability_raw | Prints out a raw dataframe showing explainability results. | False | True | None |
| export_pred_raw | Export predictions to a csv file. | False | True | None |


---

## Examples

```python
2022 Jul 23, 10:36 (🦋) /forecast/ $ load GME_20220719_123734.csv -a GME

2022 Jul 23, 11:03 (🦋) /forecast/ $ linregr GME
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 115/115 [00:0700:00, 15.10it/s]
Logistic Regression model obtains MAPE: 10.85%



       Actual price: $ 146.64
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Datetime            ┃ Prediction ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2022-07-19 00:00:00 │ $ 144.41   │
├─────────────────────┼────────────┤
│ 2022-07-20 00:00:00 │ $ 142.69   │
├─────────────────────┼────────────┤
│ 2022-07-21 00:00:00 │ $ 140.94   │
├─────────────────────┼────────────┤
│ 2022-07-22 00:00:00 │ $ 139.89   │
├─────────────────────┼────────────┤
│ 2022-07-25 00:00:00 │ $ 136.04   │
└─────────────────────┴────────────┘
```
![linregr](https://user-images.githubusercontent.com/72827203/180615335-26395da8-3848-40f4-a68b-d2c14475db95.png)

---
