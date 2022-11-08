```
usage: tcn [--num-filters NUM_FILTERS] [--weight-norm WEIGHT_NORM] [--dilation-base DILATION_BASE] [--past-covariates PAST_COVARIATES] [--all-past-covariates] [--naive] [-d {AAPL}]
           [-c TARGET_COLUMN] [-n N_DAYS] [-t TRAIN_SPLIT] [-i INPUT_CHUNK_LENGTH] [-o OUTPUT_CHUNK_LENGTH] [--force-reset FORCE_RESET] [--save-checkpoints SAVE_CHECKPOINTS]
           [--model-save-name MODEL_SAVE_NAME] [--n-epochs N_EPOCHS] [--dropout DROPOUT] [--batch-size BATCH_SIZE] [--end S_END_DATE] [--start S_START_DATE] [--learning-rate LEARNING_RATE]
           [--residuals] [--forecast-only] [--export-pred-raw] [-h] [--export EXPORT]
```

Perform TCN forecast: https://unit8co.github.io/darts/generated_api/darts.models.forecasting.tcn_model.html

```
optional arguments:
  --num-filters NUM_FILTERS
                        The number of filters in a convolutional layer of the TCN (default: 3)
  --weight-norm WEIGHT_NORM
                        Boolean value indicating whether to use weight normalization. (default: True)
  --dilation-base DILATION_BASE
                        The base of the exponent that will determine the dilation on every level. (default: 2)
  --past-covariates PAST_COVARIATES
                        Past covariates(columns/features) in same dataset. Comma separated. (default: None)
  --all-past-covariates
                        Adds all rows as past covariates except for date and the target column. (default: False)
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
  -o OUTPUT_CHUNK_LENGTH, --output-chunk-length OUTPUT_CHUNK_LENGTH
                        The length of the forecast of the model. (default: 5)
  --force-reset FORCE_RESET
                        If set to True, any previously-existing model with the same name will be reset (all checkpoints will be discarded). (default: True)
  --save-checkpoints SAVE_CHECKPOINTS
                        Whether to automatically save the untrained model and checkpoints. (default: True)
  --model-save-name MODEL_SAVE_NAME
                        Name of the model to save. (default: tcn_model)
  --n-epochs N_EPOCHS   Number of epochs over which to train the model. (default: 300)
  --dropout DROPOUT     Fraction of neurons afected by Dropout. (default: 0.1)
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

For more information and examples, use 'about tcn' to access the related guide.
```

Example:
```
2022 Jul 23, 10:36 (🦋) /forecast/ $ load GME_20220719_123734.csv -a GME

2022 Jul 23, 11:08 (🦋) /forecast/ $ tcn GME
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 115/115 [00:01<00:00, 111.85it/s]
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
