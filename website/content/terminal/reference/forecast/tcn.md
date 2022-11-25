---
title: tcn
description: OpenBB Terminal Function
---

# tcn

Perform TCN forecast: https://unit8co.github.io/darts/generated_api/darts.models.forecasting.tcn_model.html

### Usage

```python
tcn [--num-filters NUM_FILTERS] [--weight-norm WEIGHT_NORM] [--dilation-base DILATION_BASE] [--past-covariates PAST_COVARIATES] [--all-past-covariates] [--naive] [-d {}] [-c TARGET_COLUMN] [-n N_DAYS] [-t TRAIN_SPLIT] [-i INPUT_CHUNK_LENGTH] [-o OUTPUT_CHUNK_LENGTH] [--force-reset FORCE_RESET] [--save-checkpoints SAVE_CHECKPOINTS] [--model-save-name MODEL_SAVE_NAME] [--n-epochs N_EPOCHS] [--dropout DROPOUT] [--batch-size BATCH_SIZE] [--end S_END_DATE] [--start S_START_DATE] [--learning-rate LEARNING_RATE] [--residuals] [--forecast-only] [--export-pred-raw]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| num_filters | The number of filters in a convolutional layer of the TCN | 3 | True | None |
| weight_norm | Boolean value indicating whether to use weight normalization. | True | True | None |
| dilation_base | The base of the exponent that will determine the dilation on every level. | 2 | True | None |
| past_covariates | Past covariates(columns/features) in same dataset. Comma separated. | None | True | None |
| all_past_covariates | Adds all rows as past covariates except for date and the target column. | False | True | None |
| naive | Show the naive baseline for a model. | False | True | None |
| target_dataset | The name of the dataset you want to select | None | True | None |
| target_column | The name of the specific column you want to use | close | True | None |
| n_days | prediction days. | 5 | True | None |
| train_split | Start point for rolling training and forecast window. 0.0-1.0 | 0.85 | True | None |
| input_chunk_length | Number of past time steps for forecasting module at prediction time. | 14 | True | None |
| output_chunk_length | The length of the forecast of the model. | 5 | True | None |
| force_reset | If set to True, any previously-existing model with the same name will be reset (all checkpoints will be discarded). | True | True | None |
| save_checkpoints | Whether to automatically save the untrained model and checkpoints. | True | True | None |
| model_save_name | Name of the model to save. | tcn_model | True | None |
| n_epochs | Number of epochs over which to train the model. | 300 | True | None |
| dropout | Fraction of neurons affected by Dropout, from 0 to 1. | 0.1 | True | None |
| batch_size | Number of time series (input and output) used in each training pass | 32 | True | None |
| s_end_date | The end date (format YYYY-MM-DD) to select for testing | None | True | None |
| s_start_date | The start date (format YYYY-MM-DD) to select for testing | None | True | None |
| learning_rate | Learning rate during training. | 0.001 | True | None |
| residuals | Show the residuals for the model. | False | True | None |
| forecast_only | Do not plot the historical data without forecasts. | False | True | None |
| export_pred_raw | Export predictions to a csv file. | False | True | None |


---

## Examples

```python
2022 Jul 23, 10:36 (🦋) /forecast/ $ load GME_20220719_123734.csv -a GME

2022 Jul 23, 11:08 (🦋) /forecast/ $ tcn GME
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 115/115 [00:0100:00, 111.85it/s]
TCN model obtains MAPE: 19.12%



       Actual price: $ 146.64
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Datetime            ┃ Prediction ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2022-07-19 00:00:00 │ $ 135.73   │
├─────────────────────┼────────────┤
│ 2022-07-20 00:00:00 │ $ 142.42   │
├─────────────────────┼────────────┤
│ 2022-07-21 00:00:00 │ $ 140.68   │
├─────────────────────┼────────────┤
│ 2022-07-22 00:00:00 │ $ 152.98   │
├─────────────────────┼────────────┤
│ 2022-07-25 00:00:00 │ $ 154.55   │
└─────────────────────┴────────────┘
```
![tcn](https://user-images.githubusercontent.com/72827203/180615408-ac6f9289-c3e9-486f-b262-701ef1906373.png)

---
