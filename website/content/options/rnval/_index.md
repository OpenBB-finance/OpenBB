```
usage: rnval [-p] [-m MIN] [-M MAX] [-r RISK] [-h]
```

calculates the expcected value of a given option by multiplying
the payoff at each predicted stock price by the probability of
that stock price happening. This expected profit is divided by
one plus the risk free rate to determine the value of those
future dollars today. The expected payoff for each strike price
is then compared with the last traded price to determine if there
are differences in the market.

```
optional arguments:
  -p, --put             flag to calculate put option (default: False)
  -m MIN, --min MIN     min price to look at (default: -1)
  -M MAX, --max MAX     max price to look at (default: -1)
  -r RISK, --risk RISK  use a custom risk-free amount (default: None)
  -h, --help            show this help message (default: False)
```
