```
usage: theta [-n N_DAYS] [-s {N,A,M}] [-p SEASONAL_PERIODS] [-w START_WINDOW] [-f FORECAST_HORIZON] [-h] [--export EXPORT]
```

Perform Theta forecast
https://unit8co.github.io/darts/generated_api/darts.models.forecasting.theta.html?highlight=theta#module-darts.models.forecasting.theta

```
optional arguments:
  -n N_DAYS, --n_days N_DAYS
                        prediction days. (default: 5)
  -s {N,A,M}, --seasonal {N,A,M}
                        Seasonality: N: None, A: Additive, M: Multiplicative. (default: M)
  -p SEASONAL_PERIODS, --periods SEASONAL_PERIODS
                        Seasonal periods: 4: Quarterly, 7: Daily (default: 7)
  -w START_WINDOW, --window START_WINDOW
                        Start point for rolling training and forecast window. 0.0-1.0 (default: 0.65)
  -f FORECAST_HORIZON, --forecasthorizon FORECAST_HORIZON
                        Days/Points to forecast when training and performing historical back-testing (default: 3)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export figure into png, jpg, pdf, svg (default: )
```

![EXPO](https://user-images.githubusercontent.com/105685594/169634909-30864d44-e607-4e6f-8d59-ac49dafa2e2c.png)
