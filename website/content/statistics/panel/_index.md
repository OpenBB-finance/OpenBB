```
usage: panel [-r OPTIONS] [-t {pols,re,bols,fe,fdols}] [-h] [--export {csv,json,xlsx}]
```

Performs regression analysis on Panel Data. There are a multitude of options to select from to fit the needs of restrictions of the dataset.

Panel data includes observations on multiple entities – individuals, firms, countries – over multiple time periods. In most classical applications of panel data the number of entities, N, is large and the number of time periods, T, is small (often between 2 and 5). Most asymptotic theory for these estimators has been developed under an assumption that N will diverge while T is fixed. [Source: LinearModels]

Please refer to the documentation of [LinearModels](https://bashtage.github.io/linearmodels/panel/introduction.html) (or any Econometrics Textbook) to understand the difference between the models.
```
optional arguments:
  -r {OPTIONS}, --regression {OPTIONS}
                        The regression you would like to perform, first variable is the dependent variable, consecutive variables the independent variables. (default: None)
  -t {pols,re,bols,fe,fdols}, --type {pols,re,bols,fe,fdols}
                        The type of regression you wish to perform. This can be either pols (Pooled OLS), re (Random Effects), bols (Between OLS), fe (Fixed Effects) or fdols (First Difference OLS) (default: pols)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )

```

Example:
```
2022 Feb 24, 06:10 (✨) /statistics/ $ panel large_companies-thesis debt-thesis depr_amor-thesis interest_expense-thesis
                            PooledOLS Estimation Summary                            
====================================================================================
Dep. Variable:     large_companies_thesis   R-squared:                        0.0912
Estimator:                      PooledOLS   R-squared (Between):              0.0923
No. Observations:                   67022   R-squared (Within):              -0.0414
Date:                    Thu, Feb 24 2022   R-squared (Overall):              0.0912
Time:                            12:11:08   Log-likelihood                -4.483e+04
Cov. Estimator:                Unadjusted                                           
                                            F-statistic:                      2241.0
Entities:                           12880   P-value                           0.0000
Avg Obs:                           5.2036   Distribution:                 F(3,67018)
Min Obs:                           0.0000                                           
Max Obs:                           15.000   F-statistic (robust):             2241.0
                                            P-value                           0.0000
Time periods:                          14   Distribution:                 F(3,67018)
Avg Obs:                           4787.3                                           
Min Obs:                           427.00                                           
Max Obs:                           5871.0                                           
                                                                                    
                                    Parameter Estimates                                    
===========================================================================================
                         Parameter  Std. Err.     T-stat    P-value    Lower CI    Upper CI
-------------------------------------------------------------------------------------------
const                       0.3922     0.0019     207.29     0.0000      0.3884      0.3959
debt_thesis              1.551e-05  6.507e-07     23.832     0.0000   1.423e-05   1.678e-05
depr_amor_thesis          7.58e-06  7.685e-06     0.9862     0.3240  -7.484e-06   2.264e-05
interest_expense_thesis     0.0006  4.358e-05     13.945     0.0000      0.0005      0.0007
===========================================================================================
```
```
2022 Feb 24, 06:11 (✨) /statistics/ $ panel large_companies-thesis debt-thesis depr_amor-thesis interest_expense-thesis -t re
                          RandomEffects Estimation Summary                          
====================================================================================
Dep. Variable:     large_companies_thesis   R-squared:                       -0.0023
Estimator:                  RandomEffects   R-squared (Between):              0.0509
No. Observations:                   67022   R-squared (Within):              -0.0016
Date:                    Thu, Feb 24 2022   R-squared (Overall):              0.0393
Time:                            12:11:32   Log-likelihood                 4.626e+04
Cov. Estimator:                Unadjusted                                           
                                            F-statistic:                     -51.780
Entities:                           12880   P-value                           1.0000
Avg Obs:                           5.2036   Distribution:                 F(3,67018)
Min Obs:                           0.0000                                           
Max Obs:                           15.000   F-statistic (robust):             100.94
                                            P-value                           0.0000
Time periods:                          14   Distribution:                 F(3,67018)
Avg Obs:                           4787.3                                           
Min Obs:                           427.00                                           
Max Obs:                           5871.0                                           
                                                                                    
                                    Parameter Estimates                                    
===========================================================================================
                         Parameter  Std. Err.     T-stat    P-value    Lower CI    Upper CI
-------------------------------------------------------------------------------------------
const                       0.3715     0.0054     68.810     0.0000      0.3609      0.3820
debt_thesis                4.6e-06  4.935e-07     9.3209     0.0000   3.633e-06   5.567e-06
depr_amor_thesis         5.683e-05  8.365e-06     6.7939     0.0000   4.043e-05   7.322e-05
interest_expense_thesis  5.926e-05  2.252e-05     2.6311     0.0085   1.511e-05      0.0001
===========================================================================================
```
```
2022 Feb 24, 06:11 (✨) /statistics/ $ panel large_companies-thesis debt-thesis depr_amor-thesis interest_expense-thesis -t fe
                            PanelOLS Estimation Summary                             
====================================================================================
Dep. Variable:     large_companies_thesis   R-squared:                        0.0003
Estimator:                       PanelOLS   R-squared (Between):              0.0053
No. Observations:                   67022   R-squared (Within):               0.0003
Date:                    Thu, Feb 24 2022   R-squared (Overall):              0.0162
Time:                            12:11:35   Log-likelihood                 5.026e+04
Cov. Estimator:                Unadjusted                                           
                                            F-statistic:                      6.4804
Entities:                           12880   P-value                           0.0002
Avg Obs:                           5.2036   Distribution:                 F(3,59948)
Min Obs:                           0.0000                                           
Max Obs:                           15.000   F-statistic (robust):             6.4804
                                            P-value                           0.0002
Time periods:                          14   Distribution:                 F(3,59948)
Avg Obs:                           4787.3                                           
Min Obs:                           427.00                                           
Max Obs:                           5871.0                                           
                                                                                    
                                    Parameter Estimates                                    
===========================================================================================
                         Parameter  Std. Err.     T-stat    P-value    Lower CI    Upper CI
-------------------------------------------------------------------------------------------
const                       0.4292     0.0010     432.98     0.0000      0.4273      0.4312
debt_thesis              1.159e-06  5.214e-07     2.2226     0.0262   1.369e-07   2.181e-06
depr_amor_thesis         1.977e-05  9.174e-06     2.1553     0.0311   1.791e-06   3.775e-05
interest_expense_thesis  1.964e-05  2.275e-05     0.8636     0.3878  -2.494e-05   6.423e-05
===========================================================================================

F-test for Poolability: 136.30
P-value: 0.0000
Distribution: F(7070,59948)

Included effects: Entity
```