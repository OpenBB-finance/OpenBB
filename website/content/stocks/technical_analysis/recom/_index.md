```
usage: recom [-s {crypto,forex,cfd}] [-e EXCHANGE] [-i {1M,1W,1d,4h,1h,15m,5m,1m}] [--export {csv,json,xlsx}] [-h]
```

Print tradingview recommendation based on technical indicators. [Source: https://pypi.org/project/tradingview-ta/]

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

<img width="977" alt="Captura de ecrã 2021-03-31, às 00 14 41" src="https://user-images.githubusercontent.com/25267873/113069531-76ea2b00-91b8-11eb-8934-9f693d3b4ffa.png">
