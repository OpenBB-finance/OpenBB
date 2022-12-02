---
title: Econometrics
keywords:
  [
    "econometrics",
    "statistics",
    "regression",
    "panel data",
    "time series",
    "research",
    "thesis",
    "university",
  ]
excerpt: "The Introduction to Econometrics explains how to use the menu"
---

The capabilities of the [Econometrics menu](/terminal/guides/intros/econometrics) from the OpenBB Terminal are wrapped into a powerful SDK, enabling users to work with the data in a flexible environment that can be fully customized to meet the needs of any user. The Econometrics menu's purpose is to provide the user the ability to perform statistical research on custom datasets. The menu allows the user to load in his/her own dataset(s), modify the data by adding columns or setting indices, apply statistical tests (e.g. <a href="https://en.wikipedia.org/wiki/Breusch%E2%80%93Godfrey_test" target="_blank" rel="noreferrer noopener">Breusch-Godfrey autocorrelation tests</a>) as well as OLS regressions and Panel regressions (e.g. <a href="https://en.wikipedia.org/wiki/Random_effects_model" target="_blank" rel="noreferrer noopener">Random Effects</a> and <a href="https://en.wikipedia.org/wiki/Fixed_effects_model" target="_blank" rel="noreferrer noopener">Fixed Effects</a>)

## How to use

Start a Python script or Notebook file and import the SDK module:

```python
from openbb_terminal.sdk import openbb
```

Below is a brief description of each function within the Portfolio module:

| Path                                    |   Type   |                                                            Description |
| :-------------------------------------- | :------: | ---------------------------------------------------------------------: |
| openbb.econometrics.granger             | Function |                   Check time-series for Granger causality (X causes Y) |
| openbb.econometrics.granger_chart       | Function |                               Obtain a nice table of Granger causality |
| openbb.econometrics.fe                  | Function |                  Perform a Fixed Effects (fe) regression on Panel data |
| openbb.econometrics.options             | Function |          Obtain all options that can be used for regression techniques |
| openbb.econometrics.options_chart       | Function |                                        Get a nice table of the options |
| openbb.econometrics.dwat                | Function |                          Check for auto-correlation with Durbin Watson |
| openbb.econometrics.dwat_chart          | Function |                                    Plot the residuals of the OLS model |
| openbb.econometrics.coint               | Function |                             Check whether time-series are cointegrated |
| openbb.econometrics.coint_chart         | Function |                                   Show the error-correction terms plot |
| openbb.econometrics.pols                | Function |                   Perform a Pooled OLS (pols) regression on Panel data |
| openbb.econometrics.root                | Function |                                  Check for unit root in the timeseries |
| openbb.econometrics.root_chart          | Function |                        Show a nice table of the unit root test results |
| openbb.econometrics.bgod                | Function |                         Check for autocorrelation with Breusch Godfrey |
| openbb.econometrics.bgod_chart          | Function |                  Show a nice table of the autocorrelation test results |
| openbb.econometrics.re                  | Function |                 Perform a Random Effects (re) regression on Panel data |
| openbb.econometrics.bols                | Function |                  Perform a Between OLS (bols) regression on Panel data |
| openbb.econometrics.panel               | Function |                                  Obtain the regression results wrapper |
| openbb.econometrics.get_regression_data | Function |                                            Obtain an OLS model wrapper |
| openbb.econometrics.norm                | Function |                  Check whether the time-series is normally distributed |
| openbb.econometrics.norm_chart          | Function |                                    Show a histogram of the time-series |
| openbb.econometrics.clean               | Function |                   Apply either a fill or drop method to clean the data |
| openbb.econometrics.bpag                | Function |                  Test for heteroskedasticity with a Breusch-Pagan test |
| openbb.econometrics.bpag_chart          | Function |                       Get a nice table with Breusch-Pagan test results |
| openbb.econometrics.fdols               | Function |        Perform a First Difference OLS (fdols) regression on Panel data |
| openbb.econometrics.load                | Function |              Load in a dataset to be used within other functionalities |
| openbb.econometrics.ols                 | Function | Perform an Ordinary Least Squares (ols) regression on time-series data |
| openbb.econometrics.comparison          | Function |                       Compare different regression models in one table |

Alteratively you can print the contents of the Econometrics SDK with:

```python
help(openbb.econometrics)
```

## Examples

### Loading a dataset

The first step in using this menu is loading a dataset. This can be either an example dataset, see the list below, or any locally stored Excel file. To demonstrate the usage of the menu, the <a href="https://www.statsmodels.org/dev/datasets/generated/longley.html" target="_blank" rel="noreferrer noopener">longley</a>
 dataset is loaded in. This can be done with the following

```python
example_load = openbb.econometrics.load("anes96")
file_load = openbb.econometric.load("PATH_TO_FILE/FILE.xlsx")
```

| File               |                                               Description |
| :----------------- | --------------------------------------------------------: |
| anes96             |                    American National Election Survey 1996 |
| cancer             |                                        Breast Cancer Data |
| ccard              |                        Bill Greene’s credit scoring data. |
| cancer_china       |         Smoking and lung cancer in eight cities in China. |
| co2                |                     Mauna Loa Weekly Atmospheric CO2 Data |
| committee          |    First 100 days of the US House of Representatives 1995 |
| copper             |                     World Copper Market 1951-1975 Dataset |
| cpunish            |                            US Capital Punishment dataset. |
| danish_data        |                                  Danish Money Demand Data |
| elnino             |                        El Nino - Sea Surface Temperatures |
| engel              |                        Engel (1857) food expenditure data |
| fair               |                                           Affairs dataset |
| fertility          |                                 World Bank Fertility Data |
| grunfeld           |                           Grunfeld (1950) Investment Data |
| heart              |                                  Transplant Survival Data |
| interest_inflation |       (West) German interest and inflation rate 1972-1998 |
| longley            |                                           Longley dataset |
| macrodata          |                          United States Macroeconomic data |
| modechoice         |                                        Travel Mode Choice |
| nile               |                      Nile River flows at Ashwan 1871-1970 |
| randhie            |                     RAND Health Insurance Experiment Data |
| scotland           |     Taxation Powers Vote for the Scottish Parliament 1997 |
| spector            |    Spector and Mazzeo (1980) - Program Effectiveness Data |
| stackloss          |                                           Stack loss data |
| star98             |                                Star98 Educational Dataset |
| statecrim          |                                 Statewide Crime Data 2009 |
| strikes            |                                 U.S. Strike Duration Data |
| sunspots           |                            Yearly sunspots data 1700-2008 |
| wage_panel         | Veila and M. Verbeek (1998): Whose Wages Do Unions Raise? |

### Working with Time Series data

To demonstrate the usage of the Econometrics SDK for time series data, the
<a href="https://www.statsmodels.org/dev/datasets/generated/longley.html" target="_blank" rel="noreferrer noopener">longley</a> dataset is loaded in.

```python
# Load the data
longley = openbb.econometrics.load("longley")

# Show the data
longley
```

|     | TOTEMP | GNPDEFL |    GNP | UNEMP | ARMED |    POP | YEAR |
| --: | -----: | ------: | -----: | ----: | ----: | -----: | ---: |
|   0 |  60323 |      83 | 234289 |  2356 |  1590 | 107608 | 1947 |
|   1 |  61122 |    88.5 | 259426 |  2325 |  1456 | 108632 | 1948 |
|   2 |  60171 |    88.2 | 258054 |  3682 |  1616 | 109773 | 1949 |
|   3 |  61187 |    89.5 | 284599 |  3351 |  1650 | 110929 | 1950 |
|   4 |  63221 |    96.2 | 328975 |  2099 |  3099 | 112075 | 1951 |
|   5 |  63639 |    98.1 | 346999 |  1932 |  3594 | 113270 | 1952 |
|   6 |  64989 |      99 | 365385 |  1870 |  3547 | 115094 | 1953 |
|   7 |  63761 |     100 | 363112 |  3578 |  3350 | 116219 | 1954 |
|   8 |  66019 |   101.2 | 397469 |  2904 |  3048 | 117388 | 1955 |
|   9 |  67857 |   104.6 | 419180 |  2822 |  2857 | 118734 | 1956 |
|  10 |  68169 |   108.4 | 442769 |  2936 |  2798 | 120445 | 1957 |
|  11 |  66513 |   110.8 | 444546 |  4681 |  2637 | 121950 | 1958 |
|  12 |  68655 |   112.6 | 482704 |  3813 |  2552 | 123366 | 1959 |
|  13 |  69564 |   114.2 | 502601 |  3931 |  2514 | 125368 | 1960 |
|  14 |  69331 |   115.7 | 518173 |  4806 |  2572 | 127852 | 1961 |
|  15 |  70551 |   116.9 | 554894 |  4007 |  2827 | 130081 | 1962 |

This can be extended by also showing the descriptive statistics, this can be
done with a native command from Pandas as follows:

```python
longley.describe()
```

|       |  TOTEMP | GNPDEFL |     GNP |   UNEMP |   ARMED |    POP |    YEAR |
| :---- | ------: | ------: | ------: | ------: | ------: | -----: | ------: |
| count |      16 |      16 |      16 |      16 |      16 |     16 |      16 |
| mean  |   65317 | 101.681 |  387698 | 3193.31 | 2606.69 | 117424 |  1954.5 |
| std   | 3511.97 | 10.7916 | 99394.9 | 934.464 |  695.92 | 6956.1 | 4.76095 |
| min   |   60171 |      83 |  234289 |    1870 |    1456 | 107608 |    1947 |
| 25%   | 62712.5 |  94.525 |  317881 | 2348.25 |    2298 | 111788 | 1950.75 |
| 50%   |   65504 |   100.6 |  381427 |  3143.5 |  2717.5 | 116804 |  1954.5 |
| 75%   | 68290.5 |  111.25 |  454086 |  3842.5 | 3060.75 | 122304 | 1958.25 |
| max   |   70551 |   116.9 |  554894 |    4806 |    3594 | 130081 |    1962 |

It is possible to check for a variety of assumptions, e.g. normality, unit root,
granger and co-integration. The functions `openbb.econometric.norm` and `openb.econometrics.root` are shown below. Note
that due to the small size of the dataset, many of these tests are not
statistically significant.

```python
openbb.econometrics.norm(longley['GNP'])
```

|           | Kurtosis |  Skewness | Jarque-Bera | Shapiro-Wilk | Kolmogorov-Smirnov |
| :-------- | -------: | --------: | ----------: | -----------: | -----------------: |
| Statistic |  -1.1944 | 0.0525317 |    0.835092 |     0.962593 |                  1 |
| p-value   |  0.23232 |   0.95811 |     0.65866 |        0.709 |                  0 |

```python
openbb.econometrics.root(longley['POP'])
```

|                |      ADF |     KPSS |
| :------------- | -------: | -------: |
| Test Statistic |  2.35204 | 0.324887 |
| P-Value        | 0.998986 |      0.1 |
| NLags          |        6 |        0 |
| Nobs           |        9 |        0 |
| ICBest         |  113.054 |        0 |

The longley dataset is known for the ability to create an OLS regression that results in a <a href="https://www.investopedia.com/terms/r/r-squared.asp" target="_blank" rel="noreferrer noopener">R-squared</a> of 1.0 due to the fact that the US macroeconomic variables are known to be highly collinear. See the following regression performed with `openbb.econometrics.ols` as follows:

```python
# Perform the regression technique. TOTEMP is dependent,  all others independent
ols_regression = openbb.econometrics.ols(longley['TOTEMP'], longley.drop('TOTEMP', axis=1))

# Show the model summary
ols_regression.summary()
```

```
                                 OLS Regression Results
=======================================================================================
Dep. Variable:                 TOTEMP   R-squared (uncentered):                   1.000
Model:                            OLS   Adj. R-squared (uncentered):              1.000
Method:                 Least Squares   F-statistic:                          5.052e+04
Date:                Mon, 21 Nov 2022   Prob (F-statistic):                    8.20e-22
Time:                        10:54:19   Log-Likelihood:                         -117.56
No. Observations:                  16   AIC:                                      247.1
Df Residuals:                      10   BIC:                                      251.8
Df Model:                           6
Covariance Type:            nonrobust
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
GNPDEFL      -52.9936    129.545     -0.409      0.691    -341.638     235.650
GNP            0.0711      0.030      2.356      0.040       0.004       0.138
UNEMP         -0.4235      0.418     -1.014      0.335      -1.354       0.507
ARMED         -0.5726      0.279     -2.052      0.067      -1.194       0.049
POP           -0.4142      0.321     -1.289      0.226      -1.130       0.302
YEAR          48.4179     17.689      2.737      0.021       9.003      87.832
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
```

After running the regression estimation, it is possible to perform tests on the residuals of the model. E.g. for autocorrelation and heteroscedasity as shown below with the `openbb.econometrics.bgod` and `openbb.econometrics.bpag` functions.

```python
# Perform Breusch Goodfrey auto-correlation test
openbb.econometrics.bgod(ols_regression)
```

|          |         0 |
| :------- | --------: |
| lm-stat  |   10.3471 |
| p-value  | 0.0158347 |
| f-stat   | 0.0970889 |
| fp-value |  0.958799 |

```python
# Perform Breusch Pagan heteroskedacity test
openbb.econometrics.bpag(ols_regression)
```

|          |        0 |
| :------- | -------: |
| lm-stat  |  7.90331 |
| p-value  | 0.161645 |
| f-stat   |  1.62686 |
| fp-value | 0.236596 |

### Working with Panel data

Within the examples there is one panel dataset available named `wage_panel`. This is a dataset from the paper by Vella and M. Verbeek (1998), “Whose Wages Do Unions Raise? A Dynamic Model of Unionism and Wage Rate Determination for Young Men,” Journal of Applied Econometrics 13, 163-183. This is a well-known dataset also used within Chapter 14 of <a href="https://www.amazon.com/Introductory-Econometrics-Modern-Approach-Economics/dp/1111531048" target="_blank" rel="noreferrer noopener">Introduction to Econometrics by Jeffrey Wooldridge</a>.

```python
# Load the data
wage_panel = openbb.econometrics.load("wage_panel")

# Show the data
wage_panel
```

|     |  nr | year | black | exper | hisp | hours | married | educ | union |   lwage | expersq | occupation |
| --: | --: | ---: | ----: | ----: | ---: | ----: | ------: | ---: | ----: | ------: | ------: | ---------: |
|   0 |  13 | 1980 |     0 |     1 |    0 |  2672 |       0 |   14 |     0 | 1.19754 |       1 |          9 |
|   1 |  13 | 1981 |     0 |     2 |    0 |  2320 |       0 |   14 |     1 | 1.85306 |       4 |          9 |
|   2 |  13 | 1982 |     0 |     3 |    0 |  2940 |       0 |   14 |     0 | 1.34446 |       9 |          9 |
|   3 |  13 | 1983 |     0 |     4 |    0 |  2960 |       0 |   14 |     0 | 1.43321 |      16 |          9 |
|   4 |  13 | 1984 |     0 |     5 |    0 |  3071 |       0 |   14 |     0 | 1.56812 |      25 |          5 |

4360 rows × 12 columns

To run panel regressions, it is important to define both _entity_ (e.g. company) and _time_ (e.g. year).
Trying to run the `openbb.econometrics.re` function would right now result in the following:

```
openbb.econometrics.re(wage_panel['black'], wage_panel.drop('black', axis=1))

Error: Series can only be used with a 2-level MultiIndex
```

This can be corrected by setting a multi-index, this can be done with the following:

```python
wage_panel = wage_panel.set_index(['nr', 'year'], drop=False)
```

The columns `nr` and `year` still exists within the dataset and could have been dropped with the if desired. However, in this case the `year` column is relevant for generating time effects in Pooled OLS, Fixed Effects and Random Effects estimations. To be able to do this, the type of the year column needs to be changed accordingly to 'category' so it is perceived as categorical data. This can be done with the following:

```python
# Observe the current types
wage_panel.dtypes
```

|            | 0       |
| :--------- | :------ |
| nr         | int64   |
| year       | int64   |
| black      | int64   |
| exper      | int64   |
| hisp       | int64   |
| hours      | int64   |
| married    | int64   |
| educ       | int64   |
| union      | int64   |
| lwage      | float64 |
| expersq    | int64   |
| occupation | int64   |

```python
# Change the type of year to categorical
wage_panel['year'] = wage_panel['year'].astype('category')

# Observe the changed types
wage_panel.dtypes
```

|            | 0        |
| :--------- | :------- |
| nr         | int64    |
| year       | category |
| black      | int64    |
| exper      | int64    |
| hisp       | int64    |
| hours      | int64    |
| married    | int64    |
| educ       | int64    |
| union      | int64    |
| lwage      | float64  |
| expersq    | int64    |
| occupation | int64    |

The dataset is now properly configured to allow for proper panel regressions. The Econometrics SDK supports the following regression techniques.

| Path                      |                                                            Description |
| :------------------------ | ---------------------------------------------------------------------: |
| openbb.econometrics.ols   | Perform an Ordinary Least Squares (ols) regression on time-series data |
| openbb.econometrics.pols  |                   Perform a Pooled OLS (pols) regression on Panel data |
| openbb.econometrics.bols  |                  Perform a Between OLS (bols) regression on Panel data |
| openbb.econometrics.fdols |        Perform a First Difference OLS (fdols) regression on Panel data |
| openbb.econometrics.fe    |                  Perform a Fixed Effects (fe) regression on Panel data |
| openbb.econometrics.re    |                 Perform a Random Effects (re) regression on Panel data |

As an example, a **Random Effects** regression is performed. This can be done as follows:

```python
# Perform the Random Effects regression technique
random_effects_regression = openbb.econometrics.re(wage_panel['lwage'], wage_panel[['black', 'hisp', 'exper', 'expersq', 'married', 'educ', 'union','year']])

# Show the results
random_effects_regression.summary
```

```
                        RandomEffects Estimation Summary
================================================================================
Dep. Variable:                  lwage   R-squared:                        0.1806
Estimator:              RandomEffects   R-squared (Between):              0.1853
No. Observations:                4360   R-squared (Within):               0.1799
Date:                Mon, Nov 21 2022   R-squared (Overall):              0.1828
Time:                        11:13:36   Log-likelihood                   -1622.5
Cov. Estimator:            Unadjusted
                                        F-statistic:                      68.409
Entities:                         545   P-value                           0.0000
Avg Obs:                       8.0000   Distribution:                 F(14,4345)
Min Obs:                       8.0000
Max Obs:                       8.0000   F-statistic (robust):             68.409
                                        P-value                           0.0000
Time periods:                       8   Distribution:                 F(14,4345)
Avg Obs:                       545.00
Min Obs:                       545.00
Max Obs:                       545.00

                             Parameter Estimates
==============================================================================
            Parameter  Std. Err.     T-stat    P-value    Lower CI    Upper CI
------------------------------------------------------------------------------
const          0.0234     0.1514     0.1546     0.8771     -0.2735      0.3203
black         -0.1394     0.0480    -2.9054     0.0037     -0.2334     -0.0453
hisp           0.0217     0.0428     0.5078     0.6116     -0.0622      0.1057
exper          0.1058     0.0154     6.8706     0.0000      0.0756      0.1361
expersq       -0.0047     0.0007    -6.8623     0.0000     -0.0061     -0.0034
married        0.0638     0.0168     3.8035     0.0001      0.0309      0.0967
educ           0.0919     0.0107     8.5744     0.0000      0.0709      0.1129
union          0.1059     0.0179     5.9289     0.0000      0.0709      0.1409
year.1981      0.0404     0.0247     1.6362     0.1019     -0.0080      0.0889
year.1982      0.0309     0.0324     0.9519     0.3412     -0.0327      0.0944
year.1983      0.0202     0.0417     0.4840     0.6284     -0.0616      0.1020
year.1984      0.0430     0.0515     0.8350     0.4037     -0.0580      0.1440
year.1985      0.0577     0.0615     0.9383     0.3482     -0.0629      0.1782
year.1986      0.0918     0.0716     1.2834     0.1994     -0.0485      0.2321
year.1987      0.1348     0.0817     1.6504     0.0989     -0.0253      0.2950
==============================================================================
```
