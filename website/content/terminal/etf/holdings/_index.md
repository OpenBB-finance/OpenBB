```
usage: holdings [-l LIMIT] [-h] [--export {csv,json,xlsx}]
```

See what is inside an ETF holdings.

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        Number of holdings to get (default: 10)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 15, 04:15 (✨) /etf/ $ holdings
           ETF Holdings
┌───────┬──────────┬─────────────┐
│       │ % Of Etf │ Shares      │
├───────┼──────────┼─────────────┤
│ AAPL  │ 6.83%    │ 329,111,779 │
├───────┼──────────┼─────────────┤
│ MSFT  │ 6.23%    │ 158,536,434 │
├───────┼──────────┼─────────────┤
│ AMZN  │ 3.59%    │ 9,209,552   │
├───────┼──────────┼─────────────┤
│ GOOGL │ 2.15%    │ 6,351,744   │
├───────┼──────────┼─────────────┤
│ TSLA  │ 2.12%    │ 17,176,682  │
├───────┼──────────┼─────────────┤
│ GOOG  │ 2.00%    │ 5,904,299   │
├───────┼──────────┼─────────────┤
│ FB    │ 1.96%    │ 49,965,809  │
├───────┼──────────┼─────────────┤
│ NVDA  │ 1.81%    │ 52,789,400  │
├───────┼──────────┼─────────────┤
│ BRK.B │ 1.35%    │ 38,670,223  │
├───────┼──────────┼─────────────┤
│ UNH   │ 1.17%    │ 19,887,839  │
└───────┴──────────┴─────────────┘
```

