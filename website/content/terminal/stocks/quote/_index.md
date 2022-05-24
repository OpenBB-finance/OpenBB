```
usage: quote [-t S_TICKER] [-p] [-h]
```

Retrieves a current quote from the currently [loaded ticker](https://openbb-finance.github.io/OpenBBTerminal/stocks/load/). To view a quote from a different symbol than what is currently loaded, add the '-t' argument to the command string.

```
optional arguments:
  -t S_TICKER, --ticker S_TICKER
                        Stock ticker (default: TSLA)
  -p, --price           Price only (default: False)
  -h, --help            show this help message (default: False)
```

```
2022 Feb 14, 08:59 (✨) /stocks/ $ quote
          Ticker Quote
┌────────────────┬─────────────┐
│                │ TSLA        │
├────────────────┼─────────────┤
│ Name           │ Tesla, Inc. │
├────────────────┼─────────────┤
│ Price          │ 860.00      │
├────────────────┼─────────────┤
│ Open           │ 909.63      │
├────────────────┼─────────────┤
│ High           │ 915.96      │
├────────────────┼─────────────┤
│ Low            │ 850.71      │
├────────────────┼─────────────┤
│ Previous Close │ 904.55      │
├────────────────┼─────────────┤
│ Volume         │ 26,548,623  │
├────────────────┼─────────────┤
│ 52 Week High   │ 1243.49     │
├────────────────┼─────────────┤
│ 52 Week Low    │ 539.49      │
├────────────────┼─────────────┤
│ Change         │ -44.55      │
├────────────────┼─────────────┤
│ Change %       │ -4.93%      │
└────────────────┴─────────────┘

2022 Feb 14, 09:00 (✨) /stocks/ $ quote -t AAPL
         Ticker Quote
┌────────────────┬────────────┐
│                │ AAPL       │
├────────────────┼────────────┤
│ Name           │ Apple Inc. │
├────────────────┼────────────┤
│ Price          │ 168.64     │
├────────────────┼────────────┤
│ Open           │ 172.33     │
├────────────────┼────────────┤
│ High           │ 173.08     │
├────────────────┼────────────┤
│ Low            │ 168.04     │
├────────────────┼────────────┤
│ Previous Close │ 172.12     │
├────────────────┼────────────┤
│ Volume         │ 98,670,687 │
├────────────────┼────────────┤
│ 52 Week High   │ 182.94     │
├────────────────┼────────────┤
│ 52 Week Low    │ 116.21     │
├────────────────┼────────────┤
│ Change         │ -3.48      │
├────────────────┼────────────┤
│ Change %       │ -2.02%     │
└────────────────┴────────────┘
```
