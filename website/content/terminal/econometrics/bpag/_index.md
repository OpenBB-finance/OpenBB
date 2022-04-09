```
usage: dwat [-h] [--export {csv,json,xlsx}]
```

Show autocorrelation tests from Durbin-Watson

The Durbin Watson (DW) statistic is a test for autocorrelation in the residuals from a statistical model or regression analysis. The Durbin-Watson statistic will always have a value ranging between 0 and 4. A value of 2.0 indicates there is no autocorrelation detected in the sample. Values from 0 to less than 2 point to positive autocorrelation and values from 2 to 4 means negative autocorrelation. [Source: Investopedia]

```
optional arguments:
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )

```

Example:
```
2022 Feb 24, 05:44 (✨) /econometrics/ $ ols return-msft adj_close-aapl
                            OLS Regression Results                            
==============================================================================
Dep. Variable:            return_msft   R-squared:                       0.000
Model:                            OLS   Adj. R-squared:                 -0.001
Method:                 Least Squares   F-statistic:                    0.3005
Date:                Thu, 24 Feb 2022   Prob (F-statistic):              0.584
Time:                        11:45:00   Log-Likelihood:                 2010.0
No. Observations:                 759   AIC:                            -4016.
Df Residuals:                     757   BIC:                            -4007.
Df Model:                           1                                         
Covariance Type:            nonrobust                                         
==================================================================================
                     coef    std err          t      P>|t|      [0.025      0.975]
----------------------------------------------------------------------------------
Intercept          0.0023      0.002      1.392      0.164      -0.001       0.006
adj_close_aapl  -8.34e-06   1.52e-05     -0.548      0.584   -3.82e-05    2.15e-05
==============================================================================
Omnibus:                       75.797   Durbin-Watson:                   2.141
Prob(Omnibus):                  0.000   Jarque-Bera (JB):              339.963
Skew:                          -0.329   Prob(JB):                     1.51e-74
Kurtosis:                       6.212   Cond. No.                         290.
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.

2022 Feb 24, 05:45 (✨) /econometrics/ $ dwat
The result 2.14 is within the range 1.5 and 2.5 which therefore indicates autocorrelation not to be problematic.

```
