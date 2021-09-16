```
usage: ets [-t TREND] [-s SEASONAL] [-p SEASONAL_PERIODS] [-d N_DAYS]
```
Exponential Smoothing (based on trend+seasonality, see https://otexts.com/fpp2/taxonomy.html):
  * -t : trend component: N: None, A: Additive, Ad: Additive Damped. Default N.
  * -s : seasonality component: N: None, A: Additive, M: Multiplicative. Default N.
  * -p : seasonal periods. Default 5.
  * -d : prediction days. Default 5.
  * -e : end date (format YYYY-MM-DD) of the stock - Backtesting. Default None.

![ets_pltr](https://user-images.githubusercontent.com/25267873/110266847-97a6d280-7fb6-11eb-997e-0b598abc713b.png)
