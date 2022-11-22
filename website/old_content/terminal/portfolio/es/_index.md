```
usage: es [-m] [-d {laplace,student_t,logistic,normal}] [-p PERCENTILE] [-h]
```

Provides Expected Shortfall (short: ES) of the selected portfolio.

```
optional arguments:
  -m, --mean            If one should use the mean of the portfolios return (default: False)
  -d {laplace,student_t,logistic,normal}, --dist {laplace,student_t,logistic,normal}, --distributions {laplace,student_t,logistic,normal}
                        Distribution used for the calculations (default: normal)
  -p PERCENTILE, --percentile PERCENTILE
                        Percentile used for ES calculations, for example input 99.9 equals a 99.9 Percent Expected
                        Shortfall (default: 99.9)
  -h, --help            show this help message (default: False)
```

Example:

```
2022 Feb 25, 03:09 (🦋) /portfolio/ $ es
    Portfolio Expected Shortfall
┏━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃       ┃ ES:     ┃ Historical ES: ┃
┡━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ 90.0% │ -0.0204 │ -0.0202        │
├───────┼─────────┼────────────────┤
│ 95.0% │ -0.0240 │ -0.0242        │
├───────┼─────────┼────────────────┤
│ 99.0% │ -0.0310 │ -0.0270        │
├───────┼─────────┼────────────────┤
│ 99.9% │ -0.0391 │ -0.0277        │
└───────┴─────────┴────────────────┘
```
