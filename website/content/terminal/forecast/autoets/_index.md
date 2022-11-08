```
usage: autoets [--naive] [-d {AAPL}] [-c TARGET_COLUMN] [-n N_DAYS] [-s {N,A,M}] [-p SEASONAL_PERIODS] [-w START_WINDOW] [--end S_END_DATE] [--start S_START_DATE] [--residuals] [--forecast-only]
               [--export-pred-raw] [-h] [--export EXPORT]

```

Perform Automatic ETS (Error, Trend, Seasonality) forecast:
https://nixtla.github.io/statsforecast/examples/getting_started_with_auto_arima_and_ets.html

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

For more information and examples, use 'about autoets' to access the related guide.
```

Example:
```
2022 Oct 21, 18:20 (🦋) /forecast/ $ load AAPL

2022 Oct 21, 18:21 (🦋) /forecast/ $ autoets AAPL



   Actual price: 143.39
┏━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Datetime   ┃ Prediction ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2022-10-21 │ 143.42     │
├────────────┼────────────┤
│ 2022-10-24 │ 143.42     │
├────────────┼────────────┤
│ 2022-10-25 │ 143.42     │
├────────────┼────────────┤
│ 2022-10-26 │ 143.42     │
├────────────┼────────────┤
│ 2022-10-27 │ 143.42     │
└────────────┴────────────┘
```
![autoets](https://user-images.githubusercontent.com/10517170/197297075-d141d735-0b35-43cc-bf4f-e746b6b1001e.png)
