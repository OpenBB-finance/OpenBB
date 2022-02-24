```
usage: ols [-r OPTIONS [OPTIONS ...]] [-h]
```

Performs an OLS regression.

In statistics, ordinary least squares (OLS) is a type of linear least squares method for estimating the unknown parameters in a linear regression model. OLS chooses the parameters of a linear function of a set of explanatory variables by the principle of least squares: minimizing the sum of the squares of the differences between the observed dependent variable (values of the variable being observed) in the given dataset and those predicted by the linear function of the independent variable. [Source: Wikipedia]

```
optional arguments:
  -r {OPTIONS} --regression {OPTIONS}
                        The regression you would like to perform (default: None)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 24, 05:28 (✨) /statistics/ $ load TSLA_20220221_101033.xlsx tsla

2022 Feb 24, 05:28 (✨) /statistics/ $ load AAPL_20220221_140455.xlsx aapl

2022 Feb 24, 05:28 (✨) /statistics/ $ load MSFT_20220221_140503.xlsx msft

2022 Feb 24, 05:28 (✨) /statistics/ $ load GOOGL_20220221_140519.xlsx googl
```
```
2022 Feb 24, 05:28 (✨) /statistics/ $ ols adj_close-tsla adj_close-aapl adj_close-msft adj_close-googl
                            OLS Regression Results                            
==============================================================================
Dep. Variable:         adj_close_tsla   R-squared:                       0.931
Model:                            OLS   Adj. R-squared:                  0.930
Method:                 Least Squares   F-statistic:                     3381.
Date:                Thu, 24 Feb 2022   Prob (F-statistic):               0.00
Time:                        11:28:54   Log-Likelihood:                -4500.3
No. Observations:                 759   AIC:                             9009.
Df Residuals:                     755   BIC:                             9027.
Df Model:                           3                                         
Covariance Type:            nonrobust                                         
===================================================================================
                      coef    std err          t      P>|t|      [0.025      0.975]
-----------------------------------------------------------------------------------
Intercept        -456.4407     13.765    -33.160      0.000    -483.462    -429.419
adj_close_aapl      6.0557      0.355     17.042      0.000       5.358       6.753
adj_close_msft     -0.0596      0.328     -0.181      0.856      -0.704       0.585
adj_close_googl     0.1517      0.022      6.950      0.000       0.109       0.195
==============================================================================
Omnibus:                       81.510   Durbin-Watson:                   0.051
Prob(Omnibus):                  0.000   Jarque-Bera (JB):              113.208
Skew:                           0.799   Prob(JB):                     2.61e-25
Kurtosis:                       4.013   Cond. No.                     7.95e+03
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
[2] The condition number is large, 7.95e+03. This might indicate that there are
strong multicollinearity or other numerical problems.
```
```