```
usage: bgod [-l LAGS] [-h] [--export {csv,json,xlsx}]
```

Show Breusch-Pagan heteroscedasticity test results.

In statistics, heteroskedasticity (or heteroscedasticity) happens when the standard deviations of a predicted variable, monitored over different values of an independent variable or as related to prior time periods, are non-constant. With heteroskedasticity, the tell-tale sign upon visual inspection of the residual errors is that they will tend to fan out over time. [Source: Investopedia]
```
optional arguments:
  -l LAGS, --lags LAGS  The lags for the Breusch-Godfrey test (default: 3)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 24, 06:00 (✨) /econometrics/ $ ols adj_close-msft adj_close-aapl adj_close-googl adj_close-tsla
                            OLS Regression Results                            
==============================================================================
Dep. Variable:         adj_close_msft   R-squared:                       0.977
Model:                            OLS   Adj. R-squared:                  0.977
Method:                 Least Squares   F-statistic:                 1.068e+04
Date:                Thu, 24 Feb 2022   Prob (F-statistic):               0.00
Time:                        12:01:09   Log-Likelihood:                -2830.6
No. Observations:                 759   AIC:                             5669.
Df Residuals:                     755   BIC:                             5688.
Df Model:                           3                                         
Covariance Type:            nonrobust                                         
===================================================================================
                      coef    std err          t      P>|t|      [0.025      0.975]
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

2022 Feb 24, 06:01 (✨) /econometrics/ $ bgod
Breusch-Godfrey autocorrelation test [Lags: 3]
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃          ┃ Breusch-Godfrey ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ LM-stat  │ 723.75          │
├──────────┼─────────────────┤
│ p-value  │ 0.00            │
├──────────┼─────────────────┤
│ f-stat   │ 5147.20         │
├──────────┼─────────────────┤
│ fp-value │ 0.00            │
└──────────┴─────────────────┘
The result 0.0 indicates no existence of autocorrelation.
```
