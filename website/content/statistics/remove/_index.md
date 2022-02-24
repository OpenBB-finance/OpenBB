```
usage: remove [-n NAME] [-h]
```

Remove a dataset from the loaded dataset list

```
optional arguments:
  -n NAME, --name NAME  The name of the dataset you want to remove (default: None)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 24, 04:36 (✨) /statistics/ $ ?
╭─────────────────────────────────────────────────────────────────────────────────────────────────────────────── Statistics ────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                                                                                                                                                           │
│     load            load in custom data sets                                                                                                                                                                                              │
│     export          export a dataset                                                                                                                                                                                                      │
│     remove          remove a dataset                                                                                                                                                                                                      │
│     options         show available column-dataset options                                                                                                                                                                                 │
│                                                                                                                                                                                                                                           │
│ Loaded files:    thesis                                                                                                                                                                                                                   │
│                                                                                                                                                                                                                                           │
│ Exploration                                                                                                                                                                                                                               │
│     show            show a portion of a loaded dataset                                                                                                                                                                                    │
│     plot            plot data from a dataset                                                                                                                                                                                              │
│     info            show descriptive statistics of a dataset                                                                                                                                                                              │
│     index           set (multi) index based on columns                                                                                                                                                                                    │
│     clean           clean a dataset by filling or dropping NaNs                                                                                                                                                                           │
│     modify          combine columns of datasets and delete or rename columns                                                                                                                                                              │
│                                                                                                                                                                                                                                           │
│ Timeseries                                                                                                                                                                                                                                │
│     ols             fit a (multi) linear regression model                                                                                                                                                                                 │
│     norm            perform normality tests on a column of a dataset                                                                                                                                                                      │
│     root            perform unitroot tests (ADF & KPSS) on a column of a dataset                                                                                                                                                          │
│                                                                                                                                                                                                                                           │
│ Panel Data                                                                                                                                                                                                                                │
│     panel           Estimate model based on various regression techniques                                                                                                                                                                 │
│     compare         Compare results of all estimated models                                                                                                                                                                               │
│                                                                                                                                                                                                                                           │
│ Tests                                                                                                                                                                                                                                     │
│     dwat            perform Durbin-Watson autocorrelation test on the residuals of the regression                                                                                                                                         │
│     bgod            perform Breusch-Godfrey autocorrelation tests with lags on the residuals of the regression                                                                                                                            │
│     bpag            perform Breusch-Pagan heteroscedasticity test on the residuals of the regression                                                                                                                                      │
│     granger         perform Granger causality tests on two columns                                                                                                                                                                        │
│     coint           perform co-integration test on two columns                                                                                                                                                                            │
│                                                                                                                                                                                                                                           │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── Gamestonk Terminal ─╯
2022 Feb 24, 04:37 (✨) /statistics/ $ remove thesis

2022 Feb 24, 04:38 (✨) /statistics/ $ ?
╭─────────────────────────────────────────────────────────────────────────────────────────────────────────────── Statistics ────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                                                                                                                                                           │
│     load            load in custom data sets                                                                                                                                                                                              │
│     export          export a dataset                                                                                                                                                                                                      │
│     remove          remove a dataset                                                                                                                                                                                                      │
│     options         show available column-dataset options                                                                                                                                                                                 │
│                                                                                                                                                                                                                                           │
│ Loaded files:    None                                                                                                                                                                                                                     │
│                                                                                                                                                                                                                                           │
│ Exploration                                                                                                                                                                                                                               │
│     show            show a portion of a loaded dataset                                                                                                                                                                                    │
│     plot            plot data from a dataset                                                                                                                                                                                              │
│     info            show descriptive statistics of a dataset                                                                                                                                                                              │
│     index           set (multi) index based on columns                                                                                                                                                                                    │
│     clean           clean a dataset by filling or dropping NaNs                                                                                                                                                                           │
│     modify          combine columns of datasets and delete or rename columns                                                                                                                                                              │
│                                                                                                                                                                                                                                           │
│ Timeseries                                                                                                                                                                                                                                │
│     ols             fit a (multi) linear regression model                                                                                                                                                                                 │
│     norm            perform normality tests on a column of a dataset                                                                                                                                                                      │
│     root            perform unitroot tests (ADF & KPSS) on a column of a dataset                                                                                                                                                          │
│                                                                                                                                                                                                                                           │
│ Panel Data                                                                                                                                                                                                                                │
│     panel           Estimate model based on various regression techniques                                                                                                                                                                 │
│     compare         Compare results of all estimated models                                                                                                                                                                               │
│                                                                                                                                                                                                                                           │
│ Tests                                                                                                                                                                                                                                     │
│     dwat            perform Durbin-Watson autocorrelation test on the residuals of the regression                                                                                                                                         │
│     bgod            perform Breusch-Godfrey autocorrelation tests with lags on the residuals of the regression                                                                                                                            │
│     bpag            perform Breusch-Pagan heteroscedasticity test on the residuals of the regression                                                                                                                                      │
│     granger         perform Granger causality tests on two columns                                                                                                                                                                        │
│     coint           perform co-integration test on two columns                                                                                                                                                                            │
│                                                                                                                                                                                                                                           │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── Gamestonk Terminal ─╯
```
