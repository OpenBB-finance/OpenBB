```
usage: trend [-s START] [-hr HOUR] [-n NUMBER] [-h] [--export {csv,json,xlsx}] [-l LIMIT]
```

Show most talked about tickers within the last one hour. Source: [Sentiment Investor]

```
optional arguments:
  -s START, --start START
                        The starting date (format YYYY-MM-DD). Default: Today (default: 2022-02-16)
  -hr HOUR, --hour HOUR
                        Hour of the day in the 24-hour notation. Example: 14 (default: 0)
  -n NUMBER, --number NUMBER
                        Number of results returned from Sentiment Investor. Default: 10 (default: 10)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data. (default: 10)
```

Example:
```
2022 Feb 16, 10:50 (✨) /stocks/ba/ $ trend
 Most trending stocks at 2022-02-16 00:00
┏━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━┳━━━━━━┓
┃ TICKER ┃ TOTAL  ┃ LIKES  ┃ RHI  ┃ AHI  ┃
┡━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━╇━━━━━━┩
│ AMC    │ 120.00 │ 227.00 │ 1.70 │ 1.53 │
├────────┼────────┼────────┼──────┼──────┤
│ BTC    │ 97.00  │ 162.00 │ 1.75 │ 1.30 │
├────────┼────────┼────────┼──────┼──────┤
│ SPY    │ 88.00  │ 69.00  │ 1.48 │ 1.29 │
├────────┼────────┼────────┼──────┼──────┤
│ NVDA   │ 68.00  │ 34.00  │ 2.44 │ 2.57 │
├────────┼────────┼────────┼──────┼──────┤
│ FB     │ 51.00  │ 51.00  │ 1.11 │ 1.60 │
├────────┼────────┼────────┼──────┼──────┤
│ TSLA   │ 47.00  │ 53.00  │ 1.07 │ 0.81 │
├────────┼────────┼────────┼──────┼──────┤
│ MANA   │ 37.00  │ 84.00  │ 5.36 │ 3.86 │
├────────┼────────┼────────┼──────┼──────┤
│ NIO    │ 32.00  │ 21.00  │ 1.19 │ 0.87 │
├────────┼────────┼────────┼──────┼──────┤
│ PLTR   │ 31.00  │ 17.00  │ 1.45 │ 1.26 │
├────────┼────────┼────────┼──────┼──────┤
│ ETH    │ 23.00  │ 24.00  │ 1.61 │ 1.14 │
└────────┴────────┴────────┴──────┴──────┘
```
