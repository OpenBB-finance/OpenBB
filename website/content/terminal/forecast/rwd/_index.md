```
usage: rwd [--naive] [-d {AAPL}] [-c TARGET_COLUMN] [-n N_DAYS] [-s {N,A,M}] [-w START_WINDOW] [--end S_END_DATE] [--start S_START_DATE] [--residuals] [--forecast-only] [--export-pred-raw] [-h]
           [--export EXPORT]
```

Perform Random Walk with Drift forecast: https://nixtla.github.io/statsforecast/models.html#randomwalkwithdrift

```
optional arguments:
  --naive               Show the naive baseline for a model. (default: False)
  -d {AAPL}, --target-dataset {AAPL}
                        The name of the dataset you want to select (default: None)
  -c TARGET_COLUMN, --target-column TARGET_COLUMN
                        The name of the specific column you want to use (default: close)
  -n N_DAYS, --n-days N_DAYS
                        prediction days. (default: 5)
  -s {N,A,M}, --seasonal {N,A,M}
                        Seasonality: N: None, A: Additive, M: Multiplicative. (default: A)
  -w START_WINDOW, --window START_WINDOW
                        Start point for rolling training and forecast window. 0.0-1.0 (default: 0.85)
  --end S_END_DATE      The end date (format YYYY-MM-DD) to select for testing (default: None)
  --start S_START_DATE  The start date (format YYYY-MM-DD) to select for testing (default: None)
  --residuals           Show the residuals for the model. (default: False)
  --forecast-only       Do not plot the hisotorical data without forecasts. (default: False)
  --export-pred-raw     Export predictions to a csv file. (default: False)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export figure into png, jpg, pdf, svg (default: )

For more information and examples, use 'about rwd' to access the related guide.
```

Example:
```
2022 Nov 07, 18:43 (🦋) /stocks/ $ load AAPL

2022 Nov 07, 18:43 (🦋) /stocks/ $ forecast

2022 Nov 07, 18:43 (🦋) /forecast/ $ rwd AAPL

Cross Validation Time Series 1: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 115/115 [00:02<00:00, 49.97it/s]
Forecast: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 15887.52it/s]
RWD obtains MAPE: 2.98% 


   Actual price: 138.38    
┏━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Datetime   ┃ Prediction ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2022-11-07 │ 138.47     │
├────────────┼────────────┤
│ 2022-11-08 │ 138.57     │
├────────────┼────────────┤
│ 2022-11-09 │ 138.66     │
├────────────┼────────────┤
│ 2022-11-10 │ 138.76     │
├────────────┼────────────┤
│ 2022-11-11 │ 138.85     │
└────────────┴────────────┘
```

<img width="1367" alt="image" src="https://user-images.githubusercontent.com/10517170/200439289-414a9a74-14df-4dc5-af32-de5912e9e609.png">
