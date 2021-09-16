```
usage: arima [-d N_DAYS] [-i {aic,aicc,bic,hqic,oob}] [-s] [-r] [-o S_ORDER]
```
Auto-Regressive Integrated Moving Average:
  * -d : prediciton days. Default 5.
  * -i : information criteria - used if auto_arima library is invoked. Default aic.
  * -s : weekly seasonality flag. Default False.
  * -r : results about ARIMA summary flag. Default False.
  * -o : arima model order. If the model order is defined, auto_arima is not invoked, deeming information criteria useless. <br />Example: `-o 5,1,4` where:
    * p = 5 : order (number of time lags) of the autoregressive model.
    * d = 1 : degree of differencing (the number of times the data have had past values subtracted).
    * q = 4 : order of the moving-average model.
  * -e : end date (format YYYY-MM-DD) of the stock - Backtesting. Default None.

![arima](https://user-images.githubusercontent.com/25267873/108604947-d3cc1780-73a8-11eb-9dbb-53b959ae7947.png)
