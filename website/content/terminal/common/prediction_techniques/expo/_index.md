```
usage: ets [-n N_DAYS] [-t TREND] [-s SEASONAL] [-p SEASONAL_PERIODS] [-e S_END_DATE] [-d DAMPED][-w START_WINDOW][-f FORECAST_HORIZON][-h]
```

 """Performs Probabalistic Exponential Smoothing forecasting
    This is a wrapper around statsmodels Holt-Winters' Exponential Smoothing;
    we refer to this link for the original and more complete documentation of the parameters.

    https://unit8co.github.io/darts/generated_api/darts.models.forecasting.exponential_smoothing.html


```
optional arguments:
  -n N_DAYS, --n_days N_DAYS
                        prediction days. (default: 5)
  -t {N,A,M}, --trend {N,A,M}
                        Trend: N: None, A: Additive, M: Multiplicative. (default: A)
  -s {N,A,M}, --seasonal {N,A,M}
                        Seasonality: N: None, A: Additive, M: Multiplicative. (default: A)
  -p SEASONAL_PERIODS, --periods SEASONAL_PERIODS
                        Seasonal periods: 4: Quarters, 5: Business Days, 7: Weekly (default: 5)
  -d DAMPED, --damped DAMPED
                        Dampening (default: F)
  -w START_WINDOW, --window START_WINDOW
                        Start point for rolling training and forecast window. 0.0-1.0 (default: 0.65)
  -f FORECAST_HORIZON, --forecasthorizon FORECAST_HORIZON
                        Days/Points to forecast when training and performing historical back-testing
                        (default: 3)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export figure into png, jpg, pdf, svg (default: )
```

![ETS]# TODO