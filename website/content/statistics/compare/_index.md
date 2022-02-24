```
usage: compare [-h] [--export {csv,json,xlsx}]

```

Compare results between all activated regression models via `panel` command.

```
optional arguments:
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 24, 06:14 (✨) /statistics/ $ compare
                                              Model Comparison                                              
============================================================================================================
                                                  POLS                         RE                         FE
------------------------------------------------------------------------------------------------------------
Dep. Variable                   large_companies_thesis     large_companies_thesis     large_companies_thesis
Estimator                                    PooledOLS              RandomEffects                   PanelOLS
No. Observations                                 67022                      67022                      67022
Cov. Est.                                   Unadjusted                 Unadjusted                 Unadjusted
R-squared                                       0.0912                    -0.0023                     0.0003
R-Squared (Within)                             -0.0414                    -0.0016                     0.0003
R-Squared (Between)                             0.0923                     0.0509                     0.0053
R-Squared (Overall)                             0.0912                     0.0393                     0.0162
F-statistic                                     2241.0                    -51.780                     6.4804
P-value (F-stat)                                0.0000                     1.0000                     0.0002
=========================     ========================   ========================   ========================
const                                           0.3922                     0.3715                     0.4292
                                              (207.29)                   (68.810)                   (432.98)
debt_thesis                                  1.551e-05                    4.6e-06                  1.159e-06
                                              (23.832)                   (9.3209)                   (2.2226)
depr_amor_thesis                              7.58e-06                  5.683e-05                  1.977e-05
                                              (0.9862)                   (6.7939)                   (2.1553)
interest_expense_thesis                         0.0006                  5.926e-05                  1.964e-05
                                              (13.945)                   (2.6311)                   (0.8636)
=========================== ========================== ========================== ==========================
Effects                                                                                               Entity
------------------------------------------------------------------------------------------------------------

T-stats reported in parentheses
```
