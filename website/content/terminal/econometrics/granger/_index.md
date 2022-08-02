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
2022 Jun 01, 06:35 (🦋) /econometrics/ $ load strikes

2022 Jun 01, 06:36 (🦋) /econometrics/ $ granger strikes.duration,strikes.iprod

Granger Causality Test [Y: strikes.duration | X: strikes.iprod | Lags: 3]
┏━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━┓
┃              ┃ F-test ┃ P-value ┃ Count ┃ Lags ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━┩
│ ssr_ftest    │ 0.81   │ 0.49    │ 52.00 │ 3.00 │
├──────────────┼────────┼─────────┼───────┼──────┤
│ ssr_chi2test │ 2.75   │ 0.43    │ -     │ 3    │
├──────────────┼────────┼─────────┼───────┼──────┤
│ lrtest       │ 2.69   │ 0.44    │ -     │ 3    │
├──────────────┼────────┼─────────┼───────┼──────┤
│ params_ftest │ 0.81   │ 0.49    │ 52.00 │ 3.00 │
└──────────────┴────────┴─────────┴───────┴──────┘

As the p-value of the F-test is 0.495, we can not reject the null hypothesis at the 0.05 confidence level.
```
