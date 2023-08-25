---
title: rnn
description: OpenBB Terminal Function
---

# rnn

Perform RNN forecast (Vanilla RNN, LSTM, GRU): https://unit8co.github.io/darts/generated_api/darts.models.forecasting.rnn_model.html

### Usage

```python
rnn [--hidden-dim HIDDEN_DIM] [--training_length TRAINING_LENGTH] [--naive] [-d {}] [-c TARGET_COLUMN] [-n N_DAYS] [-t TRAIN_SPLIT] [-i INPUT_CHUNK_LENGTH] [--force-reset FORCE_RESET] [--save-checkpoints SAVE_CHECKPOINTS] [--model-save-name MODEL_SAVE_NAME] [--n-epochs N_EPOCHS] [--model-type MODEL_TYPE] [--dropout DROPOUT] [--batch-size BATCH_SIZE] [--end S_END_DATE] [--start S_START_DATE] [--learning-rate LEARNING_RATE] [--residuals] [--forecast-only] [--export-pred-raw]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| hidden_dim | Size for feature maps for each hidden RNN layer (h_n) | 20 | True | None |
| training_length | The length of both input (target and covariates) and output (target) time series used during training. Generally speaking, training_length should have a higher value than input_chunk_length because otherwise during training the RNN is never run for as many iterations as it will during training. | 20 | True | None |
| naive | Show the naive baseline for a model. | False | True | None |
| target_dataset | The name of the dataset you want to select | None | True | None |
| target_column | The name of the specific column you want to use | close | True | None |
| n_days | prediction days. | 5 | True | None |
| train_split | Start point for rolling training and forecast window. 0.0-1.0 | 0.85 | True | None |
| input_chunk_length | Number of past time steps for forecasting module at prediction time. | 14 | True | None |
| force_reset | If set to True, any previously-existing model with the same name will be reset (all checkpoints will be discarded). | True | True | None |
| save_checkpoints | Whether to automatically save the untrained model and checkpoints. | True | True | None |
| model_save_name | Name of the model to save. | rnn_model | True | None |
| n_epochs | Number of epochs over which to train the model. | 300 | True | None |
| model_type | Either a string specifying the RNN module type ("RNN", "LSTM" or "GRU") | LSTM | True | None |
| dropout | Fraction of neurons affected by Dropout, from 0 to 1. | 0 | True | None |
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

2022 Jul 23, 11:03 (🦋) /forecast/ $ rnn GME
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 115/115 [00:0700:00, 15.10it/s]
RNN model obtains MAPE: 14.67%



       Actual price: $ 146.64
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Datetime            ┃ Prediction ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2022-07-19 00:00:00 │ $ 146.89   │
├─────────────────────┼────────────┤
│ 2022-07-20 00:00:00 │ $ 148.58   │
├─────────────────────┼────────────┤
│ 2022-07-21 00:00:00 │ $ 150.00   │
├─────────────────────┼────────────┤
│ 2022-07-22 00:00:00 │ $ 151.23   │
├─────────────────────┼────────────┤
│ 2022-07-25 00:00:00 │ $ 152.29   │
└─────────────────────┴────────────┘
```
![rnn](https://user-images.githubusercontent.com/72827203/180615355-5c30635a-be63-4b9a-836d-9feb3d3ac263.png)

---
