```text
usage: normality [--export {csv,json,xlsx}] [-h]
```

Normality tests

To learn more about this subject, visit the Wiki page: https://en.wikipedia.org/wiki/Normality_test

A 2011 study concludes that Shapiro–Wilk has the best power for a given significance, followed closely by Anderson–Darling when comparing the Shapiro–Wilk, Kolmogorov–Smirnov, Lilliefors, and Anderson–Darling tests.

```
optional arguments:
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
Sample output
```
(✨) (stocks)>(qa)> normality
╒═══════════╤════════════╤════════════╤═══════════════╤════════════════╤══════════════════════╕
│           │   Kurtosis │   Skewness │   Jarque-Bera │   Shapiro-Wilk │   Kolmogorov-Smirnov │
╞═══════════╪════════════╪════════════╪═══════════════╪════════════════╪══════════════════════╡
│ Statistic │    -0.8178 │    -4.1427 │       20.0985 │         0.8818 │               1.0000 │
├───────────┼────────────┼────────────┼───────────────┼────────────────┼──────────────────────┤
│ p-value   │     0.4135 │     0.0000 │        0.0000 │         0.0000 │               0.0000 │
╘═══════════╧════════════╧════════════╧═══════════════╧════════════════╧══════════════════════╛
```
