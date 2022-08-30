```
usage: es [-m] [-d {laplace,student_t,logistic,normal}] [-p PERCENTILE] [-h]
```

Provides Expected Shortfall (short: ES) of the selected stock.

```
optional arguments:
  -m, --mean            If one should use the mean of the stocks return (default: False)
  -d {laplace,student_t,logistic,normal}, --dist {laplace,student_t,logistic,normal}, --distributions {laplace,student_t,logistic,normal}
                        Distribution used for the calculations (default: normal)
  -p PERCENTILE, --percentile PERCENTILE
                        Percentile used for ES calculations, for example input 99.9 equals a 99.9 Percent Expected
                        Shortfall (default: 99.9)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 25, 06:50 (✨) /stocks/qa/ $ es
      TSLA Expected Shortfall
┏━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃       ┃ ES:     ┃ Historical ES: ┃
┡━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ 90.0% │ -0.0752 │ -0.0705        │
├───────┼─────────┼────────────────┤
│ 95.0% │ -0.0885 │ -0.0932        │
├───────┼─────────┼────────────────┤
│ 99.0% │ -0.1144 │ -0.1561        │
├───────┼─────────┼────────────────┤
│ 99.9% │ -0.1444 │ -0.2106        │
└───────┴─────────┴────────────────┘
```
