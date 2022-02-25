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

Below you can find a comparison of the regression estimates based on the dataset from Vella and M. Verbeek (1998), “Whose Wages Do Unions Raise? A Dynamic Model of Unionism and Wage Rate Determination for Young Men,” Journal of Applied Econometrics 13, 163-183. This is a well-known dataset also used within Chapter 14 of Introduction to Econometrics by Jeffrey Wooldridge.

```
2022 Feb 25, 08:24 (✨) /statistics/ $ compare
                                               Model Comparison
=============================================================================================================
                                  POLS           BOLS                RE             FE                  FDOLS
-------------------------------------------------------------------------------------------------------------
Dep. Variable                 lwage_wp       lwage_wp          lwage_wp       lwage_wp               lwage_wp
Estimator                    PooledOLS     BetweenOLS     RandomEffects       PanelOLS     FirstDifferenceOLS
No. Observations                  4360            545              4360           4360                   3815
Cov. Est.                   Unadjusted     Unadjusted        Unadjusted     Unadjusted             Unadjusted
R-squared                       0.1893         0.2155            0.1806         0.1806                 0.0268
R-Squared (Within)              0.1692         0.1141            0.1799         0.1806                 0.1763
R-Squared (Between)             0.2066         0.2155            0.1853        -0.0052                 0.5491
R-Squared (Overall)             0.1893         0.1686            0.1828         0.0807                 0.5328
F-statistic                     72.459         24.633            68.409         83.851                 26.208
P-value (F-stat)                0.0000         0.0000            0.0000         0.0000                 0.0000
=====================     ============   ============   ===============   ============   ====================
const                           0.0921         0.2836            0.0234         1.4260
                              (1.1761)       (1.5897)          (0.1546)       (77.748)
black_wp                       -0.1392        -0.1414           -0.1394
                             (-5.9049)      (-2.8915)         (-2.9054)
hisp_wp                         0.0160         0.0100            0.0217
                              (0.7703)       (0.2355)          (0.5078)
exper_wp                        0.0672         0.0278            0.1058                                0.1158
                              (4.9095)       (2.4538)          (6.8706)                              (5.9096)
expersq_wp                     -0.0024                          -0.0047        -0.0052                -0.0039
                             (-2.9413)                        (-6.8623)      (-7.3612)              (-2.8005)
married_wp                      0.1083         0.1416            0.0638         0.0467                 0.0381
                              (6.8997)       (3.4346)          (3.8035)       (2.5494)               (1.6633)
educ_wp                         0.0913         0.0913            0.0919
                              (17.442)       (8.5159)          (8.5744)
union_wp                        0.1825         0.2587            0.1059         0.0800                 0.0428
                              (10.635)       (5.6214)          (5.9289)       (4.1430)               (2.1767)
year_wp.1981                    0.0583                           0.0404         0.1512
                              (1.9214)                         (1.6362)       (6.8883)
year_wp.1982                    0.0628                           0.0309         0.2530
                              (1.8900)                         (0.9519)       (10.360)
year_wp.1983                    0.0620                           0.0202         0.3544
                              (1.6915)                         (0.4840)       (12.121)
year_wp.1984                    0.0905                           0.0430         0.4901
                              (2.2566)                         (0.8350)       (13.529)
year_wp.1985                    0.1092                           0.0577         0.6175
                              (2.5200)                         (0.9383)       (13.648)
year_wp.1986                    0.1420                           0.0918         0.7655
                              (3.0580)                         (1.2834)       (13.638)
year_wp.1987                    0.1738                           0.1348         0.9250
                              (3.5165)                         (1.6504)       (13.450)
======================= ============== ============== ================= ============== ======================
Effects                                                                         Entity
-------------------------------------------------------------------------------------------------------------

T-stats reported in parentheses

```
