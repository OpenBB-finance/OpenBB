```
usage: arima [-d N_DAYS] [-i {aic,aicc,bic,hqic,oob}] [-s] [-o S_ORDER] [-r] [-e S_END_DATE] [-h]
```

In statistics and econometrics, and in particular in time series analysis, an autoregressive integrated moving average (ARIMA) model is a generalization of an autoregressive moving average (ARMA) model. Both of these models are fitted to time series data either to better understand the data or to predict future points in the series (forecasting). ARIMA(p,d,q) where parameters p, d, and q are non-negative integers, p is the order
(number of time lags) of the autoregressive model, d is the degree of differencing (the number of times the data have had past values subtracted), and q is the order of the moving-average model.

```
optional arguments:
  -d N_DAYS, --days N_DAYS
                        prediction days.
  -i {aic,aicc,bic,hqic,oob}, --ic {aic,aicc,bic,hqic,oob}
                        information criteria.
  -s, --seasonal        Use weekly seasonal data.
  -o S_ORDER, --order S_ORDER
                        arima model order (p,d,q) in format: p,d,q.
  -r, --results         results about ARIMA summary flag.
  -e S_END_DATE, --end S_END_DATE
                        The end date (format YYYY-MM-DD) to select - Backtesting
  -h, --help            show this help message
```

![arima](https://user-images.githubusercontent.com/25267873/108604947-d3cc1780-73a8-11eb-9dbb-53b959ae7947.png)
