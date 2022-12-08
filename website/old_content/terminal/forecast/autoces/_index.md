```
usage: autoces [--naive] [-d {AAPL}] [-c TARGET_COLUMN] [-n N_DAYS] [-s {N,A,M}] [-p SEASONAL_PERIODS] [-w START_WINDOW] [--end S_END_DATE] [--start S_START_DATE] [--residuals] [--forecast-only]
               [--export-pred-raw] [-h] [--export EXPORT]

```

Perform Automatic Complex Exponential Smoothing forecast: https://nixtla.github.io/statsforecast/models.html#autoces

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
  -p SEASONAL_PERIODS, --periods SEASONAL_PERIODS
                        Seasonal periods: 4: Quarterly, 7: Daily (default: 7)
  -w START_WINDOW, --window START_WINDOW
                        Start point for rolling training and forecast window. 0.0-1.0 (default: 0.85)
  --end S_END_DATE      The end date (format YYYY-MM-DD) to select for testing (default: None)
  --start S_START_DATE  The start date (format YYYY-MM-DD) to select for testing (default: None)
  --residuals           Show the residuals for the model. (default: False)
  --forecast-only       Do not plot the hisotorical data without forecasts. (default: False)
  --export-pred-raw     Export predictions to a csv file. (default: False)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export figure into png, jpg, pdf, svg (default: )

For more information and examples, use 'about autoces' to access the related guide.
```

Example:
```
2022 Nov 07, 16:42 (🦋) /stocks/ $ forecast

2022 Nov 07, 16:42 (🦋) /forecast/ $ autoces AAPL

Cross Validation Time Series 1: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 115/115 [00:13<00:00,  8.70it/s]
Forecast: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  3.23it/s]
AutoCES obtains MAPE: 3.09% 


   Actual price: 138.38    
┏━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Datetime   ┃ Prediction ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2022-11-07 │ 138.70     │
├────────────┼────────────┤
│ 2022-11-08 │ 138.53     │
├────────────┼────────────┤
│ 2022-11-09 │ 139.16     │
├────────────┼────────────┤
│ 2022-11-10 │ 138.91     │
├────────────┼────────────┤
│ 2022-11-11 │ 139.01     │
└────────────┴────────────┘
```

<img width="1370" alt="image" src="https://user-images.githubusercontent.com/10517170/200422580-549f6a02-4869-4d80-bb78-72c2f9d45d79.png">

