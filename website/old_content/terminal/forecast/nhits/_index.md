```
usage: nhits [--num-stacks NUM_STACKS] [--num-blocks NUM_BLOCKS] [--num-layers NUM_LAYERS] [--layer_widths LAYER_WIDTHS]
             [--activation {ReLU,RReLU,PReLU,Softplus,Tanh,SELU,LeakyReLU,Sigmoid}] [--max_pool_1d] [--past-covariates PAST_COVARIATES] [--all-past-covariates] [--naive] [-d {AAPL}]
             [-c TARGET_COLUMN] [-n N_DAYS] [-t TRAIN_SPLIT] [-i INPUT_CHUNK_LENGTH] [-o OUTPUT_CHUNK_LENGTH] [--force-reset FORCE_RESET] [--save-checkpoints SAVE_CHECKPOINTS]
             [--model-save-name MODEL_SAVE_NAME] [--n-epochs N_EPOCHS] [--dropout DROPOUT] [--batch-size BATCH_SIZE] [--end S_END_DATE] [--start S_START_DATE] [--residuals]
             [--forecast-only] [--export-pred-raw] [-h] [--export EXPORT]
```

Perform nhits forecast: https://unit8co.github.io/darts/generated_api/darts.models.forecasting.tft_model.html

```
optional arguments:
  --num-stacks NUM_STACKS
                        The number of stacks that make up the model (default: 3)
  --num-blocks NUM_BLOCKS
                        The number of blocks making up every stack (default: 1)
  --num-layers NUM_LAYERS
                        The number of fully connected layers (default: 2)
  --layer_widths LAYER_WIDTHS
                        The number of neurons in each layer (default: 3)
  --activation {ReLU,RReLU,PReLU,Softplus,Tanh,SELU,LeakyReLU,Sigmoid}
                        The desired activation (default: ReLU)
  --max_pool_1d         Whether to use max_pool_1d or AvgPool1d (default: False)
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
                        Name of the model to save. (default: tft_model)
  --n-epochs N_EPOCHS   Number of epochs over which to train the model. (default: 300)
  --dropout DROPOUT     Fraction of neurons afected by Dropout. (default: 0.1)
  --batch-size BATCH_SIZE
                        Number of time series (input and output) used in each training pass (default: 32)
  --end S_END_DATE      The end date (format YYYY-MM-DD) to select for testing (default: None)
  --start S_START_DATE  The start date (format YYYY-MM-DD) to select for testing (default: None)
  --residuals           Show the residuals for the model. (default: False)
  --forecast-only       Do not plot the hisotorical data without forecasts. (default: False)
  --export-pred-raw     Export predictions to a csv file. (default: False)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export figure into png, jpg, pdf, svg (default: )

For more information and examples, use 'about nhits' to access the related guide.
```

Example:
```
2022 Oct 11, 06:38 D /forecast/ $ load AAPL_20220719_201127.csv

2022 Oct 11, 06:38 D /forecast/ $ nhits AAPL_20220719_201127
Epoch 153: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 25/25 [00:00<00:00, 183.87it/s, loss=-1.56, train_loss=-1.60, val_loss=-.954]
Predicting NHITS for 5 days
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 115/115 [00:01<00:00, 92.46it/s]
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
