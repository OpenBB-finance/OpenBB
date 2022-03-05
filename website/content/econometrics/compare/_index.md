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
2022 Feb 25, 08:56 (✨) /econometrics/ $ compare
                                                                     Model Comparison
==========================================================================================================================================================
                                  POLS           BOLS                RE             FE          FE_EE          FE_IE       FE_EE_IE                  FDOLS
----------------------------------------------------------------------------------------------------------------------------------------------------------
Dep. Variable                 lwage_wp       lwage_wp          lwage_wp       lwage_wp       lwage_wp       lwage_wp       lwage_wp               lwage_wp
Estimator                    PooledOLS     BetweenOLS     RandomEffects       PanelOLS       PanelOLS       PanelOLS       PanelOLS     FirstDifferenceOLS
No. Observations                  4360            545              4360           4360           4360           4360           4360                   3815
Cov. Est.                   Unadjusted     Unadjusted        Unadjusted     Unadjusted     Unadjusted     Unadjusted     Unadjusted             Unadjusted
R-squared                       0.1893         0.2155            0.1806         0.1246         0.1806         0.0535         0.0216                 0.0268
R-Squared (Within)              0.1692         0.1141            0.1799         0.1646         0.1806        -0.1037        -0.4809                 0.1763
R-Squared (Between)             0.2066         0.2155            0.1853         0.0902        -0.0052         0.0902        -0.0052                 0.5491
R-Squared (Overall)             0.1893         0.1686            0.1828         0.1246         0.0807         0.0005        -0.2253                 0.5328
F-statistic                     72.459         24.633            68.409         61.920         83.851         81.891         27.959                 26.208
P-value (F-stat)                0.0000         0.0000            0.0000         0.0000         0.0000         0.0000         0.0000                 0.0000
=====================     ============   ============   ===============   ============   ============   ============   ============   ====================
const                           0.0921         0.2836            0.0234         1.3454         1.4260         1.6440         1.8706
                              (1.1761)       (1.5897)          (0.1546)       (60.606)       (77.748)       (94.902)       (49.430)
black_wp                       -0.1392        -0.1414           -0.1394
                             (-5.9049)      (-2.8915)         (-2.9054)
hisp_wp                         0.0160         0.0100            0.0217
                              (0.7703)       (0.2355)          (0.5078)
exper_wp                        0.0672         0.0278            0.1058                                                                             0.1158
                              (4.9095)       (2.4538)          (6.8706)                                                                           (5.9096)
expersq_wp                     -0.0024                          -0.0047        -0.0021        -0.0052        -0.0021        -0.0052                -0.0039
                             (-2.9413)                        (-6.8623)      (-7.5081)      (-7.3612)      (-7.5081)      (-7.3612)              (-2.8005)
married_wp                      0.1083         0.1416            0.0638         0.1521         0.0467         0.1521         0.0467                 0.0381
                              (6.8997)       (3.4346)          (3.8035)       (9.5417)       (2.5494)       (9.5417)       (2.5494)               (1.6633)
educ_wp                         0.0913         0.0913            0.0919
                              (17.442)       (8.5159)          (8.5744)
union_wp                        0.1825         0.2587            0.1059         0.1768         0.0800         0.1768         0.0800                 0.0428
                              (10.635)       (5.6214)          (5.9289)       (10.032)       (4.1430)       (10.032)       (4.1430)               (2.1767)
year_wp.1981                    0.0583                           0.0404         0.1187         0.1512
                              (1.9214)                         (1.6362)       (3.9144)       (6.8883)
year_wp.1982                    0.0628                           0.0309         0.1843         0.2530
                              (1.8900)                         (0.9519)       (6.0168)       (10.360)
year_wp.1983                    0.0620                           0.0202         0.2431         0.3544
                              (1.6915)                         (0.4840)       (7.7581)       (12.121)
year_wp.1984                    0.0905                           0.0430         0.3322         0.4901
                              (2.2566)                         (0.8350)       (10.236)       (13.529)
year_wp.1985                    0.1092                           0.0577         0.4112         0.6175
                              (2.5200)                         (0.9383)       (12.048)       (13.648)
year_wp.1986                    0.1420                           0.0918         0.5039         0.7655
                              (3.0580)                         (1.2834)       (13.806)       (13.638)
year_wp.1987                    0.1738                           0.1348         0.5952         0.9250
                              (3.5165)                         (1.6504)       (15.026)       (13.450)
======================= ============== ============== ================= ============== ============== ============== ============== ======================
Effects                                                                                        Entity           Time         Entity
                                                                                                                               Time
----------------------------------------------------------------------------------------------------------------------------------------------------------

T-stats reported in parentheses
```
