```
usage: rnval [-p] [-m MIN] [-M MAX] [-r RISK] [-h]
```

Calculates the expcected value of a given option by multiplying
the payoff at each predicted stock price by the probability of
that stock price happening. This expected profit is divided by
one plus the risk free rate to determine the value of those
future dollars today. The expected payoff for each strike price
is then compared with the last traded price to determine if there
are differences in the market.

For example, if you assume the price of AAPL has an equal chance
of finishing at $100 or $200 for a given expiration, you could use
this to value an option at that expiration. To value a call with a
strike of $150, you would calculate the payoff for each stock price,
which would be $0 and $50. Then, we caclulate the weighted average
payoff of $25. We need to divide this amount by the risk-free rate,
assumed to be 0.02. So the value of this option expiring in one year
is 25/1.02, or $24.51.
```
optional arguments:
  -p, --put             flag to calculate put option (default: False)
  -m MIN, --min MIN     min price to look at (default: -1)
  -M MAX, --max MAX     max price to look at (default: -1)
  -r RISK, --risk RISK  use a custom risk-free amount (default: None)
  -h, --help            show this help message (default: False)
```
<img size="1400" alt="Feature Screenshot - rnval" src="https://user-images.githubusercontent.com/85772166/142509937-dc05719f-2a65-456a-92b6-0b5099cd10c4.png">
