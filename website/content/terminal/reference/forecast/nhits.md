---
title: nhits
description: OpenBB Terminal Function
---

# nhits

Perform nhits forecast: https://unit8co.github.io/darts/generated_api/darts.models.forecasting.tft_model.html

### Usage

```python
nhits [--num-stacks NUM_STACKS] [--num-blocks NUM_BLOCKS] [--num-layers NUM_LAYERS] [--layer_widths LAYER_WIDTHS] [--activation {ReLU,RReLU,PReLU,Softplus,Tanh,SELU,LeakyReLU,Sigmoid}] [--max_pool_1d] [--past-covariates PAST_COVARIATES] [--all-past-covariates] [--naive] [-d {}] [-c TARGET_COLUMN] [-n N_DAYS] [-t TRAIN_SPLIT] [-i INPUT_CHUNK_LENGTH] [-o OUTPUT_CHUNK_LENGTH] [--force-reset FORCE_RESET] [--save-checkpoints SAVE_CHECKPOINTS] [--model-save-name MODEL_SAVE_NAME] [--n-epochs N_EPOCHS] [--dropout DROPOUT] [--batch-size BATCH_SIZE] [--end S_END_DATE] [--start S_START_DATE] [--residuals] [--forecast-only] [--export-pred-raw]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| num_stacks | The number of stacks that make up the model | 3 | True | None |
| num_blocks | The number of blocks making up every stack | 1 | True | None |
| num_layers | The number of fully connected layers | 2 | True | None |
| layer_widths | The number of neurons in each layer | 512 | True | None |
| activation | The desired activation | ReLU | True | ReLU, RReLU, PReLU, Softplus, Tanh, SELU, LeakyReLU, Sigmoid |
| maxpool1d | Whether to use max_pool_1d or AvgPool1d | True | True | None |
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
| model_save_name | Name of the model to save. | nhits_model | True | None |
| n_epochs | Number of epochs over which to train the model. | 300 | True | None |
| dropout | Fraction of neurons affected by Dropout, from 0 to 1. | 0.1 | True | None |
| batch_size | Number of time series (input and output) used in each training pass | 32 | True | None |
| s_end_date | The end date (format YYYY-MM-DD) to select for testing | None | True | None |
| s_start_date | The start date (format YYYY-MM-DD) to select for testing | None | True | None |
| residuals | Show the residuals for the model. | False | True | None |
| forecast_only | Do not plot the historical data without forecasts. | False | True | None |
| export_pred_raw | Export predictions to a csv file. | False | True | None |


---

## Examples

```python
2022 Oct 11, 06:38 D /forecast/ $ load AAPL_20220719_201127.csv

2022 Oct 11, 06:38 D /forecast/ $ nhits AAPL_20220719_201127
Epoch 153: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 25/25 [00:0000:00, 183.87it/s, loss=-1.56, train_loss=-1.60, val_loss=-.954]
Predicting NHITS for 5 days
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 115/115 [00:0100:00, 92.46it/s]
NHITS model obtains MAPE: 7.45%



   Actual price: 147.07
┏━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Datetime   ┃ Prediction ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2022-07-19 │ 134.84     │
├────────────┼────────────┤
│ 2022-07-20 │ 141.80     │
├────────────┼────────────┤
│ 2022-07-21 │ 131.06     │
├────────────┼────────────┤
│ 2022-07-22 │ 102.95     │
├────────────┼────────────┤
│ 2022-07-25 │ 123.72     │
└────────────┴────────────┘
```
![nbeats](https://user-images.githubusercontent.com/72827203/195015203-3644fe8c-e1f7-49ab-9595-a19b474948cc.png)

---
