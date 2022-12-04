```
usage: usage: panel [-r {OPTIONS} [{OPTIONS} ...]] [-t {pols,re,bols,fe,fdols,POLS,RE,BOLS,FE,FDOLS}] [-ee] [-te] [-h] [--export {csv,json,xlsx}]]
```

Performs regression analysis on Panel Data. There are a multitude of options to select from to fit the needs of restrictions of the dataset.

Panel data includes observations on multiple entities – individuals, firms, countries – over multiple time periods. In most classical applications of panel data the number of entities, N, is large and the number of time periods, T, is small (often between 2 and 5). Most asymptotic theory for these estimators has been developed under an assumption that N will diverge while T is fixed. [Source: LinearModels]

Please refer to the documentation of [LinearModels](https://bashtage.github.io/linearmodels/panel/introduction.html) (or any Econometrics Textbook) to understand the difference between the models.

```
optional arguments:
  -r {OPTIONS}, --regression {OPTIONS}
                        The regression you would like to perform, first variable is the dependent variable, consecutive variables the independent variables.
  -t {pols,re,bols,fe,fdols,POLS,RE,BOLS,FE,FDOLS}, --type {pols,re,bols,fe,fdols,POLS,RE,BOLS,FE,FDOLS}
                        The type of regression you wish to perform. This can be either pols (Pooled OLS), re (Random Effects), bols (Between OLS), fe (Fixed Effects) or fdols (First Difference OLS) (default: pols)Effects) or fdols (First Difference OLS) (default: pols)
  -ee, --entity_effects
                        Using this command creates entity effects, which is equivalent to including dummies for each entity. This is only used within Fixed Effects estimations (when type is set to 'fe') (default: False)
  -te, --time_effects   Using this command creates time effects, which is equivalent to including dummies for each time. This is only used within Fixed Effects estimations (when type is set to 'fe') (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Below you can find examples of the dataset from Vella and M. Verbeek (1998), “Whose Wages Do Unions Raise? A Dynamic Model of Unionism and Wage Rate Determination for Young Men,” Journal of Applied Econometrics 13, 163-183. This is a well-known dataset also used within Chapter 14 of Introduction to Econometrics by Jeffrey Wooldridge. For these regressions, [LinearModels](https://bashtage.github.io/linearmodels/panel/examples/examples.html) is used.

```
2022 Feb 25, 08:07 (🦋) /econometrics/ $ load wage_panel -a wp

2022 Feb 25, 08:08 (🦋) /econometrics/ $ type
           wp
┏━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ columns    ┃ dtypes   ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━┩
│ nr         │ int64    │
├────────────┼──────────┤
│ year       │ category │
├────────────┼──────────┤
│ black      │ int64    │
├────────────┼──────────┤
│ exper      │ int64    │
├────────────┼──────────┤
│ hisp       │ int64    │
├────────────┼──────────┤
│ hours      │ int64    │
├────────────┼──────────┤
│ married    │ int64    │
├────────────┼──────────┤
│ educ       │ int64    │
├────────────┼──────────┤
│ union      │ int64    │
├────────────┼──────────┤
│ lwage      │ float64  │
├────────────┼──────────┤
│ expersq    │ int64    │
├────────────┼──────────┤
│ occupation │ int64    │
└────────────┴──────────┘

2022 Feb 25, 08:09 (🦋) /econometrics/ $ index wp -i nr,year

2022 Feb 25, 08:10 (🦋) /econometrics/ $ type wp.year --format category

2022 Feb 25, 08:10 (🦋) /econometrics/ $ show wp
                                                            wp
┏━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┓
┃            ┃ nr    ┃ year    ┃ black ┃ exper ┃ hisp ┃ hours   ┃ married ┃ educ  ┃ union ┃ lwage ┃ expersq ┃ occupation ┃
┡━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━┩
│ (13, 1980) │ 13.00 │ 1980.00 │ 0.00  │ 1.00  │ 0.00 │ 2672.00 │ 0.00    │ 14.00 │ 0.00  │ 1.20  │ 1.00    │ 9.00       │
├────────────┼───────┼─────────┼───────┼───────┼──────┼─────────┼─────────┼───────┼───────┼───────┼─────────┼────────────┤
│ (13, 1981) │ 13.00 │ 1981.00 │ 0.00  │ 2.00  │ 0.00 │ 2320.00 │ 0.00    │ 14.00 │ 1.00  │ 1.85  │ 4.00    │ 9.00       │
├────────────┼───────┼─────────┼───────┼───────┼──────┼─────────┼─────────┼───────┼───────┼───────┼─────────┼────────────┤
│ (13, 1982) │ 13.00 │ 1982.00 │ 0.00  │ 3.00  │ 0.00 │ 2940.00 │ 0.00    │ 14.00 │ 0.00  │ 1.34  │ 9.00    │ 9.00       │
├────────────┼───────┼─────────┼───────┼───────┼──────┼─────────┼─────────┼───────┼───────┼───────┼─────────┼────────────┤
│ (13, 1983) │ 13.00 │ 1983.00 │ 0.00  │ 4.00  │ 0.00 │ 2960.00 │ 0.00    │ 14.00 │ 0.00  │ 1.43  │ 16.00   │ 9.00       │
├────────────┼───────┼─────────┼───────┼───────┼──────┼─────────┼─────────┼───────┼───────┼───────┼─────────┼────────────┤
│ (13, 1984) │ 13.00 │ 1984.00 │ 0.00  │ 5.00  │ 0.00 │ 3071.00 │ 0.00    │ 14.00 │ 0.00  │ 1.57  │ 25.00   │ 5.00       │
├────────────┼───────┼─────────┼───────┼───────┼──────┼─────────┼─────────┼───────┼───────┼───────┼─────────┼────────────┤
│ (13, 1985) │ 13.00 │ 1985.00 │ 0.00  │ 6.00  │ 0.00 │ 2864.00 │ 0.00    │ 14.00 │ 0.00  │ 1.70  │ 36.00   │ 2.00       │
├────────────┼───────┼─────────┼───────┼───────┼──────┼─────────┼─────────┼───────┼───────┼───────┼─────────┼────────────┤
│ (13, 1986) │ 13.00 │ 1986.00 │ 0.00  │ 7.00  │ 0.00 │ 2994.00 │ 0.00    │ 14.00 │ 0.00  │ -0.72 │ 49.00   │ 2.00       │
├────────────┼───────┼─────────┼───────┼───────┼──────┼─────────┼─────────┼───────┼───────┼───────┼─────────┼────────────┤
│ (13, 1987) │ 13.00 │ 1987.00 │ 0.00  │ 8.00  │ 0.00 │ 2640.00 │ 0.00    │ 14.00 │ 0.00  │ 1.67  │ 64.00   │ 2.00       │
├────────────┼───────┼─────────┼───────┼───────┼──────┼─────────┼─────────┼───────┼───────┼───────┼─────────┼────────────┤
│ (17, 1980) │ 17.00 │ 1980.00 │ 0.00  │ 4.00  │ 0.00 │ 2484.00 │ 0.00    │ 13.00 │ 0.00  │ 1.68  │ 16.00   │ 2.00       │
├────────────┼───────┼─────────┼───────┼───────┼──────┼─────────┼─────────┼───────┼───────┼───────┼─────────┼────────────┤
│ (17, 1981) │ 17.00 │ 1981.00 │ 0.00  │ 5.00  │ 0.00 │ 2804.00 │ 0.00    │ 13.00 │ 0.00  │ 1.52  │ 25.00   │ 2.00       │
└────────────┴───────┴─────────┴───────┴───────┴──────┴─────────┴─────────┴───────┴───────┴───────┴─────────┴────────────┘
```

**Pooled OLS Estimation:**

```
(🦋) /econometrics/ $ panel -d wp.lwage -i wp.black,wp.hisp,wp.exper,wp.expersq,wp.married,wp.educ,wp.union,wp.year

                          PooledOLS Estimation Summary
================================================================================
Dep. Variable:               lwage_wp   R-squared:                        0.1893
Estimator:                  PooledOLS   R-squared (Between):              0.2066
No. Observations:                4360   R-squared (Within):               0.1692
Date:                Fri, Feb 25 2022   R-squared (Overall):              0.1893
Time:                        14:51:08   Log-likelihood                   -2982.0
Cov. Estimator:            Unadjusted
                                        F-statistic:                      72.459
Entities:                         545   P-value                           0.0000
Avg Obs:                       8.0000   Distribution:                 F(14,4345)
Min Obs:                       8.0000
Max Obs:                       8.0000   F-statistic (robust):             72.459
                                        P-value                           0.0000
Time periods:                       8   Distribution:                 F(14,4345)
Avg Obs:                       545.00
Min Obs:                       545.00
Max Obs:                       545.00

                              Parameter Estimates
================================================================================
              Parameter  Std. Err.     T-stat    P-value    Lower CI    Upper CI
--------------------------------------------------------------------------------
const            0.0921     0.0783     1.1761     0.2396     -0.0614      0.2455
black_wp        -0.1392     0.0236    -5.9049     0.0000     -0.1855     -0.0930
hisp_wp          0.0160     0.0208     0.7703     0.4412     -0.0248      0.0568
exper_wp         0.0672     0.0137     4.9095     0.0000      0.0404      0.0941
expersq_wp      -0.0024     0.0008    -2.9413     0.0033     -0.0040     -0.0008
married_wp       0.1083     0.0157     6.8997     0.0000      0.0775      0.1390
educ_wp          0.0913     0.0052     17.442     0.0000      0.0811      0.1016
union_wp         0.1825     0.0172     10.635     0.0000      0.1488      0.2161
year_wp.1981     0.0583     0.0304     1.9214     0.0548     -0.0012      0.1178
year_wp.1982     0.0628     0.0332     1.8900     0.0588     -0.0023      0.1279
year_wp.1983     0.0620     0.0367     1.6915     0.0908     -0.0099      0.1339
year_wp.1984     0.0905     0.0401     2.2566     0.0241      0.0119      0.1691
year_wp.1985     0.1092     0.0434     2.5200     0.0118      0.0243      0.1942
year_wp.1986     0.1420     0.0464     3.0580     0.0022      0.0509      0.2330
year_wp.1987     0.1738     0.0494     3.5165     0.0004      0.0769      0.2707
================================================================================
```

**Between OLS Estimation:**

```
(🦋) /econometrics/ $ panel -d wp.lwage -i wp.black,wp.hisp,wp.exper,wp.married,wp.educ,wp.union -r bols

                         BetweenOLS Estimation Summary
================================================================================
Dep. Variable:               lwage_wp   R-squared:                        0.2155
Estimator:                 BetweenOLS   R-squared (Between):              0.2155
No. Observations:                 545   R-squared (Within):               0.1141
Date:                Fri, Feb 25 2022   R-squared (Overall):              0.1686
Time:                        14:51:15   Log-likelihood                   -194.54
Cov. Estimator:            Unadjusted
                                        F-statistic:                      24.633
Entities:                         545   P-value                           0.0000
Avg Obs:                       8.0000   Distribution:                   F(6,538)
Min Obs:                       8.0000
Max Obs:                       8.0000   F-statistic (robust):             24.633
                                        P-value                           0.0000
Time periods:                       8   Distribution:                   F(6,538)
Avg Obs:                       545.00
Min Obs:                       545.00
Max Obs:                       545.00

                             Parameter Estimates
==============================================================================
            Parameter  Std. Err.     T-stat    P-value    Lower CI    Upper CI
------------------------------------------------------------------------------
const          0.2836     0.1784     1.5897     0.1125     -0.0668      0.6340
black_wp      -0.1414     0.0489    -2.8915     0.0040     -0.2375     -0.0453
hisp_wp        0.0100     0.0426     0.2355     0.8139     -0.0737      0.0938
exper_wp       0.0278     0.0113     2.4538     0.0144      0.0055      0.0501
married_wp     0.1416     0.0412     3.4346     0.0006      0.0606      0.2226
educ_wp        0.0913     0.0107     8.5159     0.0000      0.0702      0.1123
union_wp       0.2587     0.0460     5.6214     0.0000      0.1683      0.3491
==============================================================================
```

**Random Effects Estimation:**

```
(🦋) /econometrics/ $ panel -d wp.lwage -i wp.black,wp.hisp,wp.exper,wp.expersq,wp.married,wp.educ,wp.union,wp.year -r re

                        RandomEffects Estimation Summary
================================================================================
Dep. Variable:               lwage_wp   R-squared:                        0.1806
Estimator:              RandomEffects   R-squared (Between):              0.1853
No. Observations:                4360   R-squared (Within):               0.1799
Date:                Fri, Feb 25 2022   R-squared (Overall):              0.1828
Time:                        14:56:19   Log-likelihood                   -1622.5
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
================================================================================
              Parameter  Std. Err.     T-stat    P-value    Lower CI    Upper CI
--------------------------------------------------------------------------------
const            0.0234     0.1514     0.1546     0.8771     -0.2735      0.3203
black_wp        -0.1394     0.0480    -2.9054     0.0037     -0.2334     -0.0453
hisp_wp          0.0217     0.0428     0.5078     0.6116     -0.0622      0.1057
exper_wp         0.1058     0.0154     6.8706     0.0000      0.0756      0.1361
expersq_wp      -0.0047     0.0007    -6.8623     0.0000     -0.0061     -0.0034
married_wp       0.0638     0.0168     3.8035     0.0001      0.0309      0.0967
educ_wp          0.0919     0.0107     8.5744     0.0000      0.0709      0.1129
union_wp         0.1059     0.0179     5.9289     0.0000      0.0709      0.1409
year_wp.1981     0.0404     0.0247     1.6362     0.1019     -0.0080      0.0889
year_wp.1982     0.0309     0.0324     0.9519     0.3412     -0.0327      0.0944
year_wp.1983     0.0202     0.0417     0.4840     0.6284     -0.0616      0.1020
year_wp.1984     0.0430     0.0515     0.8350     0.4037     -0.0580      0.1440
year_wp.1985     0.0577     0.0615     0.9383     0.3482     -0.0629      0.1782
year_wp.1986     0.0918     0.0716     1.2834     0.1994     -0.0485      0.2321
year_wp.1987     0.1348     0.0817     1.6504     0.0989     -0.0253      0.2950
================================================================================
```

**Fixed Effects Estimation (no effects):**

```
(🦋) /econometrics/ $ panel -d wp.lwage -i wp.expersq,wp.union,wp.married,wp.year -r fe

                          PanelOLS Estimation Summary
================================================================================
Dep. Variable:               lwage_wp   R-squared:                        0.1246
Estimator:                   PanelOLS   R-squared (Between):              0.0902
No. Observations:                4360   R-squared (Within):               0.1646
Date:                Fri, Feb 25 2022   R-squared (Overall):              0.1246
Time:                        14:51:21   Log-likelihood                   -3149.2
Cov. Estimator:            Unadjusted
                                        F-statistic:                      61.920
Entities:                         545   P-value                           0.0000
Avg Obs:                       8.0000   Distribution:                 F(10,4349)
Min Obs:                       8.0000
Max Obs:                       8.0000   F-statistic (robust):             61.920
                                        P-value                           0.0000
Time periods:                       8   Distribution:                 F(10,4349)
Avg Obs:                       545.00
Min Obs:                       545.00
Max Obs:                       545.00

                              Parameter Estimates
================================================================================
              Parameter  Std. Err.     T-stat    P-value    Lower CI    Upper CI
--------------------------------------------------------------------------------
const            1.3454     0.0222     60.606     0.0000      1.3019      1.3889
expersq_wp      -0.0021     0.0003    -7.5081     0.0000     -0.0026     -0.0015
union_wp         0.1768     0.0176     10.032     0.0000      0.1423      0.2114
married_wp       0.1521     0.0159     9.5417     0.0000      0.1209      0.1834
year_wp.1981     0.1187     0.0303     3.9144     0.0001      0.0592      0.1781
year_wp.1982     0.1843     0.0306     6.0168     0.0000      0.1243      0.2444
year_wp.1983     0.2431     0.0313     7.7581     0.0000      0.1817      0.3046
year_wp.1984     0.3322     0.0324     10.236     0.0000      0.2685      0.3958
year_wp.1985     0.4112     0.0341     12.048     0.0000      0.3443      0.4781
year_wp.1986     0.5039     0.0365     13.806     0.0000      0.4323      0.5754
year_wp.1987     0.5952     0.0396     15.026     0.0000      0.5176      0.6729
================================================================================
```

**Fixed Effects Estimation (entity effects):**

```
(🦋) /econometrics/ $ panel -d wp.lwage -i wp.expersq,wp.married,wp.union,wp.year -r fe -e

                          PanelOLS Estimation Summary
================================================================================
Dep. Variable:               lwage_wp   R-squared:                        0.1806
Estimator:                   PanelOLS   R-squared (Between):             -0.0052
No. Observations:                4360   R-squared (Within):               0.1806
Date:                Fri, Feb 25 2022   R-squared (Overall):              0.0807
Time:                        14:52:24   Log-likelihood                   -1324.8
Cov. Estimator:            Unadjusted
                                        F-statistic:                      83.851
Entities:                         545   P-value                           0.0000
Avg Obs:                       8.0000   Distribution:                 F(10,3805)
Min Obs:                       8.0000
Max Obs:                       8.0000   F-statistic (robust):             83.851
                                        P-value                           0.0000
Time periods:                       8   Distribution:                 F(10,3805)
Avg Obs:                       545.00
Min Obs:                       545.00
Max Obs:                       545.00

                              Parameter Estimates
================================================================================
              Parameter  Std. Err.     T-stat    P-value    Lower CI    Upper CI
--------------------------------------------------------------------------------
const            1.4260     0.0183     77.748     0.0000      1.3901      1.4620
expersq_wp      -0.0052     0.0007    -7.3612     0.0000     -0.0066     -0.0038
union_wp         0.0800     0.0193     4.1430     0.0000      0.0421      0.1179
married_wp       0.0467     0.0183     2.5494     0.0108      0.0108      0.0826
year_wp.1981     0.1512     0.0219     6.8883     0.0000      0.1082      0.1942
year_wp.1982     0.2530     0.0244     10.360     0.0000      0.2051      0.3008
year_wp.1983     0.3544     0.0292     12.121     0.0000      0.2971      0.4118
year_wp.1984     0.4901     0.0362     13.529     0.0000      0.4191      0.5611
year_wp.1985     0.6175     0.0452     13.648     0.0000      0.5288      0.7062
year_wp.1986     0.7655     0.0561     13.638     0.0000      0.6555      0.8755
year_wp.1987     0.9250     0.0688     13.450     0.0000      0.7902      1.0599
================================================================================

F-test for Poolability: 9.1568
P-value: 0.0000
Distribution: F(544,3805)

Included effects: Entity
```

**Fixed Effects Estimation (time effects):**

```
(🦋) /econometrics/ $ panel -d wp.lwage -i wp.expersq,wp.married,wp.union -r fe -t

                          PanelOLS Estimation Summary
================================================================================
Dep. Variable:               lwage_wp   R-squared:                        0.0535
Estimator:                   PanelOLS   R-squared (Between):              0.0902
No. Observations:                4360   R-squared (Within):              -0.1037
Date:                Fri, Feb 25 2022   R-squared (Overall):              0.0005
Time:                        14:52:45   Log-likelihood                   -3149.2
Cov. Estimator:            Unadjusted
                                        F-statistic:                      81.891
Entities:                         545   P-value                           0.0000
Avg Obs:                       8.0000   Distribution:                  F(3,4349)
Min Obs:                       8.0000
Max Obs:                       8.0000   F-statistic (robust):             81.891
                                        P-value                           0.0000
Time periods:                       8   Distribution:                  F(3,4349)
Avg Obs:                       545.00
Min Obs:                       545.00
Max Obs:                       545.00

                             Parameter Estimates
==============================================================================
            Parameter  Std. Err.     T-stat    P-value    Lower CI    Upper CI
------------------------------------------------------------------------------
const          1.6440     0.0173     94.902     0.0000      1.6100      1.6779
expersq_wp    -0.0021     0.0003    -7.5081     0.0000     -0.0026     -0.0015
union_wp       0.1768     0.0176     10.032     0.0000      0.1423      0.2114
married_wp     0.1521     0.0159     9.5417     0.0000      0.1209      0.1834
==============================================================================

F-test for Poolability: 39.988
P-value: 0.0000
Distribution: F(7,4349)

Included effects: Time
```

**Fixed Effects Estimation (entity and time effects):**

```
(🦋) /econometrics/ $ panel -d wp.lwage -i wp.expersq,wp.married,wp.union  -r fe -t -e

                          PanelOLS Estimation Summary
================================================================================
Dep. Variable:               lwage_wp   R-squared:                        0.0216
Estimator:                   PanelOLS   R-squared (Between):             -0.0052
No. Observations:                4360   R-squared (Within):              -0.4809
Date:                Fri, Feb 25 2022   R-squared (Overall):             -0.2253
Time:                        14:52:53   Log-likelihood                   -1324.8
Cov. Estimator:            Unadjusted
                                        F-statistic:                      27.959
Entities:                         545   P-value                           0.0000
Avg Obs:                       8.0000   Distribution:                  F(3,3805)
Min Obs:                       8.0000
Max Obs:                       8.0000   F-statistic (robust):             27.959
                                        P-value                           0.0000
Time periods:                       8   Distribution:                  F(3,3805)
Avg Obs:                       545.00
Min Obs:                       545.00
Max Obs:                       545.00

                             Parameter Estimates
==============================================================================
            Parameter  Std. Err.     T-stat    P-value    Lower CI    Upper CI
------------------------------------------------------------------------------
const          1.8706     0.0378     49.430     0.0000      1.7964      1.9448
expersq_wp    -0.0052     0.0007    -7.3612     0.0000     -0.0066     -0.0038
union_wp       0.0800     0.0193     4.1430     0.0000      0.0421      0.1179
married_wp     0.0467     0.0183     2.5494     0.0108      0.0108      0.0826
==============================================================================

F-test for Poolability: 10.067
P-value: 0.0000
Distribution: F(551,3805)

Included effects: Entity, Time
```

**First Difference OLS Estimation:**

```
(🦋) /econometrics/ $ panel -d wp.lwage -i wp.exper,wp.expersq,wp.married,wp.union -r fdols

                     FirstDifferenceOLS Estimation Summary
================================================================================
Dep. Variable:               lwage_wp   R-squared:                        0.0268
Estimator:         FirstDifferenceOLS   R-squared (Between):              0.5491
No. Observations:                3815   R-squared (Within):               0.1763
Date:                Fri, Feb 25 2022   R-squared (Overall):              0.5328
Time:                        14:53:16   Log-likelihood                   -2305.5
Cov. Estimator:            Unadjusted
                                        F-statistic:                      26.208
Entities:                         545   P-value                           0.0000
Avg Obs:                       8.0000   Distribution:                  F(4,3811)
Min Obs:                       8.0000
Max Obs:                       8.0000   F-statistic (robust):             26.208
                                        P-value                           0.0000
Time periods:                       8   Distribution:                  F(4,3811)
Avg Obs:                       545.00
Min Obs:                       545.00
Max Obs:                       545.00

                             Parameter Estimates
==============================================================================
            Parameter  Std. Err.     T-stat    P-value    Lower CI    Upper CI
------------------------------------------------------------------------------
exper_wp       0.1158     0.0196     5.9096     0.0000      0.0773      0.1542
expersq_wp    -0.0039     0.0014    -2.8005     0.0051     -0.0066     -0.0012
union_wp       0.0428     0.0197     2.1767     0.0296      0.0042      0.0813
married_wp     0.0381     0.0229     1.6633     0.0963     -0.0068      0.0831
==============================================================================
```
