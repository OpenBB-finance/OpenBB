---
title: dwat
description: OpenBB Terminal Function
---

# dwat

Show autocorrelation tests from Durbin-Watson. Needs OLS to be run in advance with independent and dependent variables

### Usage

```python
dwat [-p]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| plot | Plot the residuals | False | True | None |


---

## Examples

```python
2022 Feb 24, 05:59 (🦋) /econometrics/ $ ols -d adj_close-msft -i adj_close-aapl -i adj_close-googl -i adj_close-tsla
                            OLS Regression Results
==============================================================================
Dep. Variable:         adj_close_msft   R-squared:                       0.977
Model:                            OLS   Adj. R-squared:                  0.977
Method:                 Least Squares   F-statistic:                 1.068e+04
Date:                Thu, 24 Feb 2022   Prob (F-statistic):               0.00
Time:                        12:00:01   Log-Likelihood:                -2830.6
No. Observations:                 759   AIC:                             5669.
Df Residuals:                     755   BIC:                             5688.
Df Model:                           3
Covariance Type:            nonrobust
===================================================================================
                      coef    std err          t      P|t|      [0.025      0.975]
-----------------------------------------------------------------------------------
Intercept          27.7984      2.166     12.832      0.000      23.546      32.051
adj_close_aapl      0.8662      0.034     25.503      0.000       0.800       0.933
adj_close_googl     0.0508      0.002     30.374      0.000       0.048       0.054
adj_close_tsla     -0.0007      0.004     -0.181      0.856      -0.009       0.007
==============================================================================
Omnibus:                       41.445   Durbin-Watson:                   0.044
Prob(Omnibus):                  0.000   Jarque-Bera (JB):               47.398
Skew:                           0.612   Prob(JB):                     5.10e-11
Kurtosis:                       2.995   Cond. No.                     1.16e+04
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
[2] The condition number is large, 1.16e+04. This might indicate that there are
strong multicollinearity or other numerical problems.

2022 Feb 24, 06:00 (🦋) /statistics/ $ dwat -p
The result 0.04 is outside the range 1.5 and 2.5 and therefore autocorrelation can be problematic.
Please consider lags of the dependent or independent variable.
```
![durbin_watson example](https://user-images.githubusercontent.com/46355364/155514788-caaa65a2-1f5f-41d0-8db2-06e682d5a53e.png)

---
