```
usage: regr [--past-covariates PAST_COVARIATES] [-d {GME}] [-c TARGET_COLUMN] [-n N_DAYS] [--forecast-horizon FORECAST_HORIZON] [-t TRAIN_SPLIT] [-o OUTPUT_CHUNK_LENGTH] [--lags LAGS] [--residuals] [-f] [-h] [--export EXPORT]
```

Perform a regression forecast.

```
optional arguments:

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
  -o OUTPUT_CHUNK_LENGTH, --output-chunk-length OUTPUT_CHUNK_LENGTH
                        The length of the forecast of the model. (default: 5)
  --lags LAGS           Lagged target values used to predict the next time step. (default: 72)
  --residuals           Show the residuals for the model. (default: False)
  -f, --forecast_only   Do not plot the hisotorical data without forecasts. (default: False)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export figure into png, jpg, pdf, svg (default: )

For more information and examples, use 'about export' to access the related guide.
```

Example:
```
2022 Jul 23, 10:36 (🦋) /forecasting/ $ load GME_20220719_123734.csv -a GME

2022 Jul 23, 11:08 (🦋) /forecasting/ $ regr GME
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 115/115 [00:01<00:00, 111.85it/s]
Regression model obtains MAPE: 12.34%



       Actual price: $ 146.64
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Datetime            ┃ Prediction ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2022-07-19 00:00:00 │ $ 143.74   │
├─────────────────────┼────────────┤
│ 2022-07-20 00:00:00 │ $ 144.90   │
├─────────────────────┼────────────┤
│ 2022-07-21 00:00:00 │ $ 142.41   │
├─────────────────────┼────────────┤
│ 2022-07-22 00:00:00 │ $ 133.50   │
├─────────────────────┼────────────┤
│ 2022-07-25 00:00:00 │ $ 134.24   │
└─────────────────────┴────────────┘
```
