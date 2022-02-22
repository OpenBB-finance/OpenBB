```
usage: parity [-p] [-a] [-m MINI] [-M MAXI] [-h] [--export {csv,json,xlsx}]
```

An advanced strategy that seeks arbitrage opportunites in put-call spreads relative to the forward underlying asset price; put-call parity defines the relationship between calls, puts and the underlying futures contract. This principle requires that the puts and calls are the same strike, same expiration and have the same underlying futures contract.  The put call relationship is highly correlated, so if put call parity is violated, an arbitrage opportunity exists.

```
optional arguments:
  -p, --put             Shows puts instead of calls (default: False)
  -a, --ask             Use ask price instead of lastPrice (default: False)
  -m MINI, --min MINI   Minimum strike price shown (default: None)
  -M MAXI, --max MAXI   Maximum strike price shown (default: None)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 16, 09:17 (✨) /stocks/options/ $ load TSLA

2022 Feb 16, 09:18 (✨) /stocks/options/ $ parity -m 900 -M 950
Warning: Low volume options may be difficult to trade.
┏━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Strike ┃ Call Difference ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ 900.00 │ -3.49           │
├────────┼─────────────────┤
│ 905.00 │ -3.37           │
├────────┼─────────────────┤
│ 910.00 │ -4.09           │
├────────┼─────────────────┤
│ 915.00 │ -1.39           │
├────────┼─────────────────┤
│ 920.00 │ -2.34           │
├────────┼─────────────────┤
│ 925.00 │ -2.65           │
├────────┼─────────────────┤
│ 930.00 │ -2.46           │
├────────┼─────────────────┤
│ 935.00 │ -5.14           │
├────────┼─────────────────┤
│ 940.00 │ -3.89           │
├────────┼─────────────────┤
│ 945.00 │ -8.08           │
├────────┼─────────────────┤
│ 950.00 │ -3.23           │
└────────┴─────────────────┘
```
