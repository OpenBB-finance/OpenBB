```
usage: nbeats [--num_stacks NUM_STACKS] [--num_blocks NUM_BLOCKS] [--num_layers NUM_LAYERS] [--layer_widths LAYER_WIDTHS] [--past-covariates PAST_COVARIATES] [--all-past-covariates]
              [--naive] [-d {AAPL}] [-c TARGET_COLUMN] [-n N_DAYS] [-t TRAIN_SPLIT] [-i INPUT_CHUNK_LENGTH] [-o OUTPUT_CHUNK_LENGTH] [--force-reset FORCE_RESET]
              [--save-checkpoints SAVE_CHECKPOINTS] [--model-save-name MODEL_SAVE_NAME] [--n-epochs N_EPOCHS] [--batch-size BATCH_SIZE] [--end S_END_DATE] [--start S_START_DATE]
              [--learning-rate LEARNING_RATE] [--residuals] [--forecast-only] [--export-pred-raw] [-h] [--export EXPORT]
```

Perform NBEATS forecast (Neural Bayesian Estimation of Time Series):
https://unit8co.github.io/darts/generated_api/darts.models.forecasting.nbeats.html

```
optional arguments:
  --num_stacks NUM_STACKS
                        The number of stacks that make up the whole model. (default: 10)
  --num_blocks NUM_BLOCKS
                        The number of blocks making up every stack. (default: 3)
  --num_layers NUM_LAYERS
                        The number of fully connected layers preceding the final forking layers in each block of every stack. (default: 4)
  --layer_widths LAYER_WIDTHS
                        Determines the number of neurons that make up each fully connected layer in each block of every stack (default: 512)
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
                        Name of the model to save. (default: nbeats_model)
  --n-epochs N_EPOCHS   Number of epochs over which to train the model. (default: 300)
  --batch-size BATCH_SIZE
                        Number of time series (input and output) used in each training pass (default: 800)
  --end S_END_DATE      The end date (format YYYY-MM-DD) to select for testing (default: None)
  --start S_START_DATE  The start date (format YYYY-MM-DD) to select for testing (default: None)
  --learning-rate LEARNING_RATE
                        Learning rate during training. (default: 0.001)
  --residuals           Show the residuals for the model. (default: False)
  --forecast-only       Do not plot the hisotorical data without forecasts. (default: False)
  --export-pred-raw     Export predictions to a csv file. (default: False)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export figure into png, jpg, pdf, svg (default: )

For more information and examples, use 'about nbeats' to access the related guide.
```

Example:
```
2022 Jul 23, 10:36 (🦋) /forecast/ $ load GME_20220719_123734.csv -a GME

2022 Jul 23, 11:03 (🦋) /forecast/ $ nbeats GME
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 115/115 [00:07<00:00, 15.10it/s]
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
