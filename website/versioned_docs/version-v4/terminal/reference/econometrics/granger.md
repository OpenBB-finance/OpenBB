---
title: granger
description: OpenBB Terminal Function
---

# granger

Show Granger causality between two timeseries

### Usage

```python
granger [-t Available time series] [-l LAGS] [-c CONFIDENCE]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| ts | Requires two time series, the first time series is assumed to be Granger-caused by the second time series. | None | True | None |
| lags | How many lags should be included | 3 | True | None |
| confidence | Set the confidence level | 0.05 | True | None |


---

## Examples

```python
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
---
