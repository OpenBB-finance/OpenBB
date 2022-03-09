```
usage: granger [ts {OPTIONS}] [-l LAGS] [-cl CONFIDENCE] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

Show Granger causality between two timeseries

The Granger causality test is a statistical hypothesis test for determining whether one time series is useful in forecasting another, first proposed in 1969. Ordinarily, regressions reflect "mere" correlations, but Clive Granger argued that causality in economics could be tested for by measuring the ability to predict the future values of a time series using prior values of another time series. Since the question of "true causality" is deeply philosophical, and because of the post hoc ergo propter hoc fallacy of assuming that one thing preceding another can be used as a proof of causation, econometricians assert that the Granger test finds only "predictive causality". Using the term "causality" alone is a misnomer, as Granger-causality is better described as "precedence", or, as Granger himself later claimed in 1977, "temporally related". Rather than testing whether X causes Y, the Granger causality tests whether X forecasts Y. [Source: Wikipedia]

```
optional arguments:ols 
  -ts {OPTIONS}, --timeseries {OPTIONS}
                        Requires two time series, the first time series is assumed to be Granger-caused by the second time series. (default: None)
  -l LAGS, --lags LAGS  How many lags should be included (default: 3)
  -cl CONFIDENCE, --confidence CONFIDENCE
                        Set the confidence level (default: 0.05)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```

Example:
```
2022 Feb 24, 05:54 (✨) /econometrics/ $ granger adj_close-msft adj_close-aapl
Granger Causality Test [Y: adj_close | X: adj_close | Lags: 3]
┏━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━┓
┃              ┃ F-test ┃ P-value ┃ Count  ┃ Lags ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━┩
│ ssr_ftest    │ 2.13   │ 0.09    │ 749.00 │ 3.00 │
├──────────────┼────────┼─────────┼────────┼──────┤
│ ssr_chi2test │ 6.46   │ 0.09    │ -      │ 3    │
├──────────────┼────────┼─────────┼────────┼──────┤
│ lrtest       │ 6.43   │ 0.09    │ -      │ 3    │
├──────────────┼────────┼─────────┼────────┼──────┤
│ params_ftest │ 2.13   │ 0.09    │ 749.00 │ 3.00 │
└──────────────┴────────┴─────────┴────────┴──────┘
As the p-value of the F-test is 0.095, we can not reject the null hypothesis at the 0.05 confidence level.
```
