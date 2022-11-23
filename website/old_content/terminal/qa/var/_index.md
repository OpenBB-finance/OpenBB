```
usage: var [-m] [-a] [-s] [-p PERCENTILE] [-h]
```

Provides value at risk (short: VaR) of the selected stock.

```
optional arguments:
  -m, --mean            If one should use the mean of the stocks return (default: False)
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
2022 Feb 16, 11:18 (🦋) /stocks/qa/ $ var
          FB Value at Risk
┏━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃       ┃ VaR:    ┃ Historical VaR: ┃
┡━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ 90.0% │ -0.0305 │ -0.0233         │
├───────┼─────────┼─────────────────┤
│ 95.0% │ -0.0389 │ -0.0364         │
├───────┼─────────┼─────────────────┤
│ 99.0% │ -0.0546 │ -0.0578         │
├───────┼─────────┼─────────────────┤
│ 99.9% │ -0.0719 │ -0.1719         │
└───────┴─────────┴─────────────────┘
```
