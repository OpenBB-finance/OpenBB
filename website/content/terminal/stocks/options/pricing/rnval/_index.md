```
usage: rnval [-p] [-m MINI] [-M MAXI] [-r RISK] [-h]
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
  -p, --put             Show puts instead of calls (default: False)
  -m MINI, --min MINI   Minimum strike price shown (default: None)
  -M MAXI, --max MAXI   Maximum strike price shown (default: None)
  -r RISK, --risk RISK  The risk-free rate to use (default: None)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 16, 09:45 (✨) /stocks/options/pricing/ $ add -p 100 -c 0.5

2022 Feb 16, 09:46 (✨) /stocks/options/pricing/ $ add -p 200 -c 0.5

2022 Feb 16, 09:46 (✨) /stocks/options/pricing/ $ show
Estimated price(s) of AAPL at 2022-05-20
┏━━━━━━━━┳━━━━━━━━┓
┃ Price  ┃ Chance ┃
┡━━━━━━━━╇━━━━━━━━┩
│ 100.00 │ 0.50   │
├────────┼────────┤
│ 200.00 │ 0.50   │
└────────┴────────┘
2022 Feb 16, 09:46 (✨) /stocks/options/pricing/ $ rnval
            Risk Neutral Values
┏━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┓
┃ Strike ┃ Last Price ┃ Value ┃ Difference ┃
┡━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━┩
│ 120.00 │ 53.25      │ 39.99 │ 13.26      │
├────────┼────────────┼───────┼────────────┤
│ 125.00 │ 48.11      │ 37.49 │ 10.62      │
├────────┼────────────┼───────┼────────────┤
│ 130.00 │ 43.80      │ 34.99 │ 8.81       │
├────────┼────────────┼───────┼────────────┤
│ 135.00 │ 37.71      │ 32.49 │ 5.22       │
├────────┼────────────┼───────┼────────────┤
│ 140.00 │ 35.00      │ 29.99 │ 5.01       │
├────────┼────────────┼───────┼────────────┤
│ 145.00 │ 30.35      │ 27.49 │ 2.86       │
├────────┼────────────┼───────┼────────────┤
│ 150.00 │ 26.30      │ 24.99 │ 1.31       │
├────────┼────────────┼───────┼────────────┤
│ 155.00 │ 22.35      │ 22.49 │ -0.14      │
├────────┼────────────┼───────┼────────────┤
│ 160.00 │ 18.30      │ 19.99 │ -1.69      │
├────────┼────────────┼───────┼────────────┤
│ 165.00 │ 15.00      │ 17.50 │ -2.50      │
├────────┼────────────┼───────┼────────────┤
│ 170.00 │ 11.35      │ 15.00 │ -3.65      │
├────────┼────────────┼───────┼────────────┤
│ 175.00 │ 8.65       │ 12.50 │ -3.85      │
├────────┼────────────┼───────┼────────────┤
│ 180.00 │ 6.70       │ 10.00 │ -3.30      │
├────────┼────────────┼───────┼────────────┤
│ 185.00 │ 4.60       │ 7.50  │ -2.90      │
├────────┼────────────┼───────┼────────────┤
│ 190.00 │ 3.25       │ 5.00  │ -1.75      │
├────────┼────────────┼───────┼────────────┤
│ 195.00 │ 2.29       │ 2.50  │ -0.21      │
├────────┼────────────┼───────┼────────────┤
│ 200.00 │ 1.59       │ 0.00  │ 1.59       │
├────────┼────────────┼───────┼────────────┤
│ 210.00 │ 0.70       │ 0.00  │ 0.70       │
└────────┴────────────┴───────┴────────────┘
```
