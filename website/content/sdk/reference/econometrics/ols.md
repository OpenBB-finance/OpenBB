---
title: ols
description: OpenBB SDK Function
---

# ols

Performs an OLS regression on timeseries data. [Source: Statsmodels]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/regression_model.py#L176)]

```python
openbb.econometrics.ols(Y: pd.DataFrame, X: pd.DataFrame)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| Y | pd.DataFrame | Dependent variable series. | None | False |
| X | pd.DataFrame | Dataframe of independent variables series. | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| statsmodels.regression.linear_model.RegressionResultsWrapper | Regression model wrapper from statsmodels. |
---

## Examples

```python
import openbb_terminal.sdk as openbb
df = openbb.econometrics.load("wage_panel")
OLS_model = openbb.econometrics.OLS(df["lwage"], df[["educ", "exper", "expersq"]])
print(OLS_model.summary())`
```

```
OLS Regression Results
=======================================================================================
Dep. Variable:                  lwage   R-squared (uncentered):                   0.920
Model:                            OLS   Adj. R-squared (uncentered):              0.919
Method:                 Least Squares   F-statistic:                          1.659e+04
Date:                Thu, 10 Nov 2022   Prob (F-statistic):                        0.00
Time:                        15:28:11   Log-Likelihood:                         -3091.3
No. Observations:                4360   AIC:                                      6189.
Df Residuals:                    4357   BIC:                                      6208.
Df Model:                           3
Covariance Type:            nonrobust
==============================================================================
                coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
educ           0.0986      0.002     39.879      0.000       0.094       0.103
exper          0.1018      0.009     10.737      0.000       0.083       0.120
expersq       -0.0034      0.001     -4.894      0.000      -0.005      -0.002
==============================================================================
Omnibus:                     1249.642   Durbin-Watson:                   0.954
Prob(Omnibus):                  0.000   Jarque-Bera (JB):             9627.436
Skew:                          -1.152   Prob(JB):                         0.00
Kurtosis:                       9.905   Cond. No.                         86.4
==============================================================================
Notes:
[1] R² is computed without centering (uncentered) since the model does not contain a constant.
[2] Standard Errors assume that the covariance matrix of the errors is correctly specified.
```
---

