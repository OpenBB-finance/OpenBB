```
usage: var -s STRIKE [-sim SIMULATIONS] [-per PERCENTILE] [-p] [-h]
```

The value at risk for a given option at expiry, thus mostly suitable for european options.

```
optional arguments:
  -s STRIKE, --strike STRIKE
                        The strike of the option (default: None)
  -sim SIMULATIONS, --simulations SIMULATIONS
                        The number of simulations (default: 100)
  -per PERCENTILE, --percentile PERCENTILE
                        The risk free rate (default: 99)
  -p, --put             Whether the option is a put. (default: False)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Apr 18, 05:33 (🦋) /stocks/options/ $ var -s 935

TSLA Call Option 935.0 2022-05-13
┌───────┬──────────────┐
│       │ Expiry VaR % │
├───────┼──────────────┤
│ 75.0% │ -0.5551      │
├───────┼──────────────┤
│ 90.0% │ -0.5555      │
├───────┼──────────────┤
│ 95.0% │ -0.5556      │
├───────┼──────────────┤
│ 99.0% │ -0.5563      │
└───────┴──────────────┘
```
