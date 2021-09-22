```
usage: ets [-d N_DAYS] [-t TREND] [-s SEASONAL] [-p SEASONAL_PERIODS] [-e S_END_DATE] [-h]
```

Exponential Smoothing, see https://otexts.com/fpp2/taxonomy.html Trend='N', Seasonal='N': Simple Exponential Smoothing Trend='N', Seasonal='A':
Exponential Smoothing Trend='N', Seasonal='M': Exponential Smoothing Trend='A', Seasonal='N': Holt’s linear method Trend='A', Seasonal='A': Additive
Holt-Winters’ method Trend='A', Seasonal='M': Multiplicative Holt-Winters’ method Trend='Ad', Seasonal='N': Additive damped trend method Trend='Ad',
Seasonal='A': Exponential Smoothing Trend='Ad', Seasonal='M': Holt-Winters’ damped method Trend component: N: None, A: Additive, Ad: Additive Damped
Seasonality component: N: None, A: Additive, M: Multiplicative

```
optional arguments:
  -d N_DAYS, --days N_DAYS
                        prediction days.
  -t TREND, --trend TREND
                        Trend component: N: None, A: Additive, Ad: Additive Damped.
  -s SEASONAL, --seasonal SEASONAL
                        Seasonality component: N: None, A: Additive, M: Multiplicative.
  -p SEASONAL_PERIODS, --periods SEASONAL_PERIODS
                        Seasonal periods.
  -e S_END_DATE, --end S_END_DATE
                        The end date (format YYYY-MM-DD) to select - Backtesting
  -h, --help            show this help message
```

![ets_pltr](https://user-images.githubusercontent.com/25267873/110266847-97a6d280-7fb6-11eb-997e-0b598abc713b.png)
