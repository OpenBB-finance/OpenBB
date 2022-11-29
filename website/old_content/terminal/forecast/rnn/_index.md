```
usage: rnn [--hidden-dim HIDDEN_DIM] [--training_length TRAINING_LENGTH] [--naive] [-d {AAPL}] [-c TARGET_COLUMN] [-n N_DAYS] [-t TRAIN_SPLIT] [-i INPUT_CHUNK_LENGTH]
           [--force-reset FORCE_RESET] [--save-checkpoints SAVE_CHECKPOINTS] [--model-save-name MODEL_SAVE_NAME] [--n-epochs N_EPOCHS] [--model-type MODEL_TYPE] [--dropout DROPOUT]
           [--batch-size BATCH_SIZE] [--end S_END_DATE] [--start S_START_DATE] [--learning-rate LEARNING_RATE] [--residuals] [--forecast-only] [--export-pred-raw] [-h] [--export EXPORT]
```

Perform RNN forecast (Vanilla RNN, LSTM, GRU):
https://unit8co.github.io/darts/generated_api/darts.models.forecasting.rnn_model.html

```
optional arguments:
  --hidden-dim HIDDEN_DIM
                        Size for feature maps for each hidden RNN layer (h_n) (default: 20)
  --training_length TRAINING_LENGTH
                        The length of both input (target and covariates) and output (target) time series used during training. Generally speaking, training_length should have a higher
                        value than input_chunk_length because otherwise during training the RNN is never run for as many iterations as it will during training. (default: 20)
  --naive               Show the naive baseline for a model. (default: False)
  -d {AAPL}, --target-dataset {AAPL}
                        The name of the dataset you want to select (default: None)
  -c TARGET_COLUMN, --target-column TARGET_COLUMN
                        The name of the specific column you want to use (default: close)
  -n N_DAYS, --n-days N_DAYS
                        prediction days. (default: 5)
  -t TRAIN_SPLIT, --train-split TRAIN_SPLIT
                        Start point for rolling training and forecast window. 0.0-1.0 (default: 0.85)
  -i INPUT_CHUNK_LENGTH, --input-chunk-length INPUT_CHUNK_LENGTH
                        Number of past time steps for forecasting module at prediction time. (default: 14)
  --force-reset FORCE_RESET
                        If set to True, any previously-existing model with the same name will be reset (all checkpoints will be discarded). (default: True)
  --save-checkpoints SAVE_CHECKPOINTS
                        Whether to automatically save the untrained model and checkpoints. (default: True)
  --model-save-name MODEL_SAVE_NAME
                        Name of the model to save. (default: rnn_model)
  --n-epochs N_EPOCHS   Number of epochs over which to train the model. (default: 300)
  --model-type MODEL_TYPE
                        Either a string specifying the RNN module type ("RNN", "LSTM" or "GRU") (default: LSTM)
  --dropout DROPOUT     Fraction of neurons afected by Dropout. (default: 0)
  --batch-size BATCH_SIZE
                        Number of time series (input and output) used in each training pass (default: 32)
  --end S_END_DATE      The end date (format YYYY-MM-DD) to select for testing (default: None)
  --start S_START_DATE  The start date (format YYYY-MM-DD) to select for testing (default: None)
  --learning-rate LEARNING_RATE
                        Learning rate during training. (default: 0.001)
  --residuals           Show the residuals for the model. (default: False)
  --forecast-only       Do not plot the hisotorical data without forecasts. (default: False)
  --export-pred-raw     Export predictions to a csv file. (default: False)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export figure into png, jpg, pdf, svg (default: )

For more information and examples, use 'about rnn' to access the related guide.
```

Example:
```
2022 Jul 23, 10:36 (🦋) /forecast/ $ load GME_20220719_123734.csv -a GME

2022 Jul 23, 11:03 (🦋) /forecast/ $ rnn GME
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 115/115 [00:07<00:00, 15.10it/s]
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
