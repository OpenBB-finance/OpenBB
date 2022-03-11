```
usage: ols [-r OPTIONS [OPTIONS ...]] [-h] [-h] [--export {csv,json,xlsx}]
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

Example (based on [Longley's Dataset](https://www.statsmodels.org/dev/datasets/generated/longley.html)):

```
2022 Feb 25, 06:58 (✨) /econometrics/ $ load longley ll

2022 Feb 25, 06:58 (✨) /econometrics/ $ info ll
                                         ll
┏━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┓
┃       ┃ totemp   ┃ gnpdefl ┃ gnp       ┃ unemp   ┃ armed   ┃ pop       ┃ year    ┃
┡━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━┩
│ count │ 16.00    │ 16.00   │ 16.00     │ 16.00   │ 16.00   │ 16.00     │ 16.00   │
├───────┼──────────┼─────────┼───────────┼─────────┼─────────┼───────────┼─────────┤
│ mean  │ 65317.00 │ 101.68  │ 387698.44 │ 3193.31 │ 2606.69 │ 117424.00 │ 1954.50 │
├───────┼──────────┼─────────┼───────────┼─────────┼─────────┼───────────┼─────────┤
│ std   │ 3511.97  │ 10.79   │ 99394.94  │ 934.46  │ 695.92  │ 6956.10   │ 4.76    │
├───────┼──────────┼─────────┼───────────┼─────────┼─────────┼───────────┼─────────┤
│ min   │ 60171.00 │ 83.00   │ 234289.00 │ 1870.00 │ 1456.00 │ 107608.00 │ 1947.00 │
├───────┼──────────┼─────────┼───────────┼─────────┼─────────┼───────────┼─────────┤
│ 25%   │ 62712.50 │ 94.53   │ 317881.00 │ 2348.25 │ 2298.00 │ 111788.50 │ 1950.75 │
├───────┼──────────┼─────────┼───────────┼─────────┼─────────┼───────────┼─────────┤
│ 50%   │ 65504.00 │ 100.60  │ 381427.00 │ 3143.50 │ 2717.50 │ 116803.50 │ 1954.50 │
├───────┼──────────┼─────────┼───────────┼─────────┼─────────┼───────────┼─────────┤
│ 75%   │ 68290.50 │ 111.25  │ 454085.50 │ 3842.50 │ 3060.75 │ 122304.00 │ 1958.25 │
├───────┼──────────┼─────────┼───────────┼─────────┼─────────┼───────────┼─────────┤
│ max   │ 70551.00 │ 116.90  │ 554894.00 │ 4806.00 │ 3594.00 │ 130081.00 │ 1962.00 │
└───────┴──────────┴─────────┴───────────┴─────────┴─────────┴───────────┴─────────┘

2022 Feb 25, 06:59 (✨) /econometrics/ $ ols totemp-ll gnpdefl-ll gnp-ll unemp-ll armed-ll pop-ll year-ll
                                 OLS Regression Results
=======================================================================================
Dep. Variable:              totemp_ll   R-squared (uncentered):                   1.000
Model:                            OLS   Adj. R-squared (uncentered):              1.000
Method:                 Least Squares   F-statistic:                          5.052e+04
Date:                Fri, 25 Feb 2022   Prob (F-statistic):                    8.20e-22
Time:                        12:59:32   Log-Likelihood:                         -117.56
No. Observations:                  16   AIC:                                      247.1
Df Residuals:                      10   BIC:                                      251.8
Df Model:                           6
Covariance Type:            nonrobust
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
gnpdefl_ll   -52.9936    129.545     -0.409      0.691    -341.638     235.650
gnp_ll         0.0711      0.030      2.356      0.040       0.004       0.138
unemp_ll      -0.4235      0.418     -1.014      0.335      -1.354       0.507
armed_ll      -0.5726      0.279     -2.052      0.067      -1.194       0.049
pop_ll        -0.4142      0.321     -1.289      0.226      -1.130       0.302
year_ll       48.4179     17.689      2.737      0.021       9.003      87.832
==============================================================================
Omnibus:                        1.443   Durbin-Watson:                   1.277
Prob(Omnibus):                  0.486   Jarque-Bera (JB):                0.605
Skew:                           0.476   Prob(JB):                        0.739
Kurtosis:                       3.031   Cond. No.                     4.56e+05
==============================================================================

Notes:
[1] R² is computed without centering (uncentered) since the model does not contain a constant.
[2] Standard Errors assume that the covariance matrix of the errors is correctly specified.
[3] The condition number is large, 4.56e+05. This might indicate that there are
strong multicollinearity or other numerical problems.

Warnings:
kurtosistest only valid for n>=20 ... continuing anyway, n=16
```
