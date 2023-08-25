---
title: nbeats
description: OpenBB Terminal Function
---

# nbeats

Perform NBEATS forecast (Neural Bayesian Estimation of Time Series): https://unit8co.github.io/darts/generated_api/darts.models.forecasting.nbeats.html

### Usage

```python
nbeats [--num_stacks NUM_STACKS] [--num_blocks NUM_BLOCKS] [--num_layers NUM_LAYERS] [--layer_widths LAYER_WIDTHS] [--past-covariates PAST_COVARIATES] [--all-past-covariates] [--naive] [-d {}] [-c TARGET_COLUMN] [-n N_DAYS] [-t TRAIN_SPLIT] [-i INPUT_CHUNK_LENGTH] [-o OUTPUT_CHUNK_LENGTH] [--force-reset FORCE_RESET] [--save-checkpoints SAVE_CHECKPOINTS] [--model-save-name MODEL_SAVE_NAME] [--n-epochs N_EPOCHS] [--batch-size BATCH_SIZE] [--end S_END_DATE] [--start S_START_DATE] [--learning-rate LEARNING_RATE] [--residuals] [--forecast-only] [--export-pred-raw]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| num_stacks | The number of stacks that make up the whole model. | 10 | True | None |
| num_blocks | The number of blocks making up every stack. | 3 | True | None |
| num_layers | The number of fully connected layers preceding the final forking layers in each block of every stack. | 4 | True | None |
| layer_widths | Determines the number of neurons that make up each fully connected layer in each block of every stack | 512 | True | None |
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
| model_save_name | Name of the model to save. | nbeats_model | True | None |
| n_epochs | Number of epochs over which to train the model. | 300 | True | None |
| batch_size | Number of time series (input and output) used in each training pass | 800 | True | None |
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

2022 Jul 23, 11:03 (🦋) /forecast/ $ nbeats GME
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 115/115 [00:0700:00, 15.10it/s]
NBEATS model obtains MAPE: 23.53%



       Actual price: $ 146.64
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Datetime            ┃ Prediction ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2022-07-19 00:00:00 │ $ 158.52   │
├─────────────────────┼────────────┤
│ 2022-07-20 00:00:00 │ $ 172.21   │
├─────────────────────┼────────────┤
│ 2022-07-21 00:00:00 │ $ 67.46    │
├─────────────────────┼────────────┤
│ 2022-07-22 00:00:00 │ $ 97.63    │
├─────────────────────┼────────────┤
│ 2022-07-25 00:00:00 │ $ 154.24   │
└─────────────────────┴────────────┘
```
![nbeats](https://user-images.githubusercontent.com/72827203/180615396-d29126ae-ad75-4f84-9f67-2121dc4e695a.png)

---
