```
usage: recom [-s {crypto,forex,cfd}] [-e EXCHANGE] [-i {1M,1W,1d,4h,1h,15m,5m,1m}] [--export {csv,json,xlsx}] [-h]
```

Print tradingview recommendation based on technical indicators. [Source: <https://pypi.org/project/tradingview-ta/>]

```
optional arguments:
  -s {crypto,forex,cfd}, --screener {crypto,forex,cfd}
                        Screener. See https://python-tradingview-ta.readthedocs.io/en/latest/usage.html (default: america)
  -e EXCHANGE, --exchange EXCHANGE
                        Set exchange. For Forex use: 'FX_IDC', and for crypto use 'TVC'. See https://python-tradingview-
                        ta.readthedocs.io/en/latest/usage.html. By default Alpha Vantage tries to get this data from the ticker. (default: )
  -i {1M,1W,1d,4h,1h,15m,5m,1m}, --interval {1M,1W,1d,4h,1h,15m,5m,1m}
                        Interval, that corresponds to the recommendation given by tradingview based on technical indicators. See https://python-
                        tradingview-ta.readthedocs.io/en/latest/usage.html (default: )
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:

```
2022 Feb 16, 11:31 (🦋) /stocks/ta/ $ recom
               Ticker Recommendation
┏━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━┳━━━━━━┳━━━━━━━━━┓
┃         ┃ RECOMMENDATION ┃ BUY ┃ SELL ┃ NEUTRAL ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━╇━━━━━━╇━━━━━━━━━┩
│ 1 month │ BUY            │ 15  │ 2    │ 9       │
├─────────┼────────────────┼─────┼──────┼─────────┤
│ 1 week  │ BUY            │ 14  │ 2    │ 10      │
├─────────┼────────────────┼─────┼──────┼─────────┤
│ 1 day   │ SELL           │ 5   │ 13   │ 8       │
├─────────┼────────────────┼─────┼──────┼─────────┤
│ 4 hours │ SELL           │ 4   │ 14   │ 8       │
├─────────┼────────────────┼─────┼──────┼─────────┤
│ 1 hour  │ SELL           │ 4   │ 13   │ 9       │
├─────────┼────────────────┼─────┼──────┼─────────┤
│ 15 min  │ SELL           │ 3   │ 13   │ 10      │
├─────────┼────────────────┼─────┼──────┼─────────┤
│ 5 min   │ SELL           │ 5   │ 12   │ 9       │
├─────────┼────────────────┼─────┼──────┼─────────┤
│ 1 min   │ SELL           │ 6   │ 11   │ 9       │
└─────────┴────────────────┴─────┴──────┴─────────┘
```
