```
usage: rnval [-p] [-m MIN] [-M MAX] [-r RISK] [-h]
```

calculates the value of an option based on ending price estimates. this
calculates the expected value of the option payoff and then compares it
to current prices.
learn more: https://en.wikipedia.org/wiki/Rational_pricing#Delta_hedging

```
optional arguments:
  -p, --put             flag to calculate put option (default: False)
  -m MIN, --min MIN     min price to look at (default: -1)
  -M MAX, --max MAX     max price to look at (default: -1)
  -r RISK, --risk RISK  use a custom risk-free amount (default: None)
  -h, --help            show this help message (default: False)
```
