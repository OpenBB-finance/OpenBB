```
usage: brnn [--n-rnn-layers N_RNN_LAYERS] [--hidden-size HIDDEN_SIZE] [--past-covariates PAST_COVARIATES] [-d {GME}] [-c TARGET_COLUMN] [-n N_DAYS] [--forecast-horizon FORECAST_HORIZON] [-t TRAIN_SPLIT] [-i INPUT_CHUNK_LENGTH]
            [-o OUTPUT_CHUNK_LENGTH] [--force-reset FORCE_RESET] [--save-checkpoints SAVE_CHECKPOINTS] [--model-save-name MODEL_SAVE_NAME] [--n-epochs N_EPOCHS] [--model-type MODEL_TYPE] [--dropout DROPOUT] [--batch-size BATCH_SIZE]
            [--learning-rate LEARNING_RATE] [--residuals] [-f] [-h] [--export EXPORT]
```

Perform BRNN forecast (Vanilla RNN, LSTM, GRU)

```
optional arguments:

  --n-rnn-layers N_RNN_LAYERS
                        Number of layers in the RNN module. (default: 1)
  --hidden-size HIDDEN_SIZE
                        Size for feature maps for each hidden RNN layer (h_n) (default: 10)
  --past-covariates PAST_COVARIATES
                        Past covariates(columns/features) in same dataset. Comma separated. (default: None)
  -d {GME}, --target-dataset {GME}
                        The name of the dataset you want to select (default: None)
  -c TARGET_COLUMN, --target-column TARGET_COLUMN
                        The name of the specific column you want to use (default: close)
  -n N_DAYS, --n-days N_DAYS
                        prediction days. (default: 5)
  --forecast-horizon FORECAST_HORIZON
                        Days/Points to forecast for historical back-testing (default: 5)
  -t TRAIN_SPLIT, --train-split TRAIN_SPLIT
                        Start point for rolling training and forecast window. 0.0-1.0 (default: 0.85)
  -i INPUT_CHUNK_LENGTH, --input-chunk-length INPUT_CHUNK_LENGTH
                        Number of past time steps for forecasting module at prediction time. (default: 14)
  -o OUTPUT_CHUNK_LENGTH, --output-chunk-length OUTPUT_CHUNK_LENGTH
                        The length of the forecast of the model. (default: 5)
  --force-reset FORCE_RESET
                        If set to True, any previously-existing model with the same name will be reset (all checkpoints will be discarded). (default: True)
  --save-checkpoints SAVE_CHECKPOINTS
                        Whether to automatically save the untrained model and checkpoints. (default: True)
  --model-save-name MODEL_SAVE_NAME
                        Name of the model to save. (default: brnn_model)
  --n-epochs N_EPOCHS   Number of epochs over which to train the model. (default: 100)
  --model-type MODEL_TYPE
                        Either a string specifying the RNN module type ("RNN", "LSTM" or "GRU") (default: LSTM)
  --dropout DROPOUT     Fraction of neurons afected by Dropout. (default: 0)
  --batch-size BATCH_SIZE
                        Number of time series (input and output) used in each training pass (default: 32)
  --learning-rate LEARNING_RATE
                        Learning rate during training. (default: 0.001)
  --residuals           Show the residuals for the model. (default: False)
  -f, --forecast_only   Do not plot the hisotorical data without forecasts. (default: False)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export figure into png, jpg, pdf, svg (default: )

For more information and examples, use 'about export' to access the related guide.
```

Example:
```
2022 Jul 23, 10:36 (🦋) /forecast/ $ load GME_20220719_123734.csv -a GME

2022 Jul 23, 11:03 (🦋) /forecast/ $ brnn GME
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 115/115 [00:07<00:00, 15.10it/s]
Block RNN model obtains MAPE: 17.09%



       Actual price: $ 146.64
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Datetime            ┃ Prediction ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2022-07-19 00:00:00 │ $ 147.89   │
├─────────────────────┼────────────┤
│ 2022-07-20 00:00:00 │ $ 149.11   │
├─────────────────────┼────────────┤
│ 2022-07-21 00:00:00 │ $ 149.59   │
├─────────────────────┼────────────┤
│ 2022-07-22 00:00:00 │ $ 141.46   │
├─────────────────────┼────────────┤
│ 2022-07-25 00:00:00 │ $ 144.99   │
└─────────────────────┴────────────┘
```
![brnn](https://user-images.githubusercontent.com/72827203/180615365-1644ce7a-050e-4ee1-92c2-4518db14f53d.png)
