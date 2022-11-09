```
usage: autoselect [--naive] [-d {AAPL}] [-c TARGET_COLUMN] [-n N_DAYS] [-s {N,A,M}] [-p SEASONAL_PERIODS] [-w START_WINDOW] [--end S_END_DATE] [--start S_START_DATE] [--residuals] [--forecast-only]
                  [--export-pred-raw] [-h] [--export EXPORT]

```

Perform Automatic Statistical Forecast (select best statistical model from AutoARIMA, AutoETS, AutoCES, MSTL, ...)

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

For more information and examples, use 'about autoselect' to access the related guide.
```

Example:
```
2022 Nov 09, 15:23 (🦋) /forecast/ $ load AAPL

2022 Nov 09, 15:24 (🦋) /forecast/ $ autoselect AAPL

Cross Validation Time Series 1: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 115/115 [00:47<00:00,  2.40it/s]
Forecast: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:01<00:00,  1.80s/it]


  Performance per model.  
   Best model: AutoETS    
┏━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Model         ┃ MAPE   ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ AutoETS       │ 2.91%  │
├───────────────┼────────┤
│ AutoARIMA     │ 2.93%  │
├───────────────┼────────┤
│ RWD           │ 3.04%  │
├───────────────┼────────┤
│ AutoCES       │ 3.15%  │
├───────────────┼────────┤
│ MSTL          │ 3.40%  │
├───────────────┼────────┤
│ SeasonalNaive │ 4.32%  │
├───────────────┼────────┤
│ SeasWA        │ 8.06%  │
└───────────────┴────────┘

   Actual price: 139.50    
┏━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Datetime   ┃ Prediction ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2022-11-09 │ 139.47     │
├────────────┼────────────┤
│ 2022-11-10 │ 139.47     │
├────────────┼────────────┤
│ 2022-11-11 │ 139.47     │
├────────────┼────────────┤
│ 2022-11-14 │ 139.47     │
├────────────┼────────────┤
│ 2022-11-15 │ 139.47     │
└────────────┴────────────┘
```
<img width="1334" alt="image" src="https://user-images.githubusercontent.com/10517170/200934562-71bcdd1d-6728-4a8c-8ad7-52d559ba9fa8.png">
