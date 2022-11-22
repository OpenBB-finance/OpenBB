```
usage: var [-m] [-a] [-s] [-p PERCENTILE] [-h]
```

Provides value at risk (short: VaR) of the selected portfolio.

```
optional arguments:
  -m, --mean            If one should use the mean of the portfolio return (default: False)
  -a, --adjusted        If the VaR should be adjusted for skew and kurtosis (Cornish-Fisher-Expansion) (default:
                        False)
  -s, --student         If one should use the student-t distribution (default: False)
  -p PERCENTILE, --percentile PERCENTILE
                        Percentile used for VaR calculations, for example input 99.9 equals a 99.9 Percent VaR
                        (default: 99.9)
  -h, --help            show this help message (default: False)
```

Example:

```
2022 Feb 25, 03:09 (🦋) /portfolio/ $ var
       Portfolio Value at Risk
┏━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃       ┃ VaR:    ┃ Historical VaR: ┃
┡━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ 90.0% │ -0.0148 │ -0.0135         │
├───────┼─────────┼─────────────────┤
│ 95.0% │ -0.0189 │ -0.0197         │
├───────┼─────────┼─────────────────┤
│ 99.0% │ -0.0267 │ -0.0258         │
├───────┼─────────┼─────────────────┤
│ 99.9% │ -0.0353 │ -0.0276         │
└───────┴─────────┴─────────────────┘
```
