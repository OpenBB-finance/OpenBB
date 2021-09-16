```
usage: chains [-c] [-p] [-m MIN_SP] [-M MAX_SP] [-d TO_DISPLAY] [--export {csv,json,xlsx}] [-h]
```

Display option chains

```
optional arguments:
  -c, --calls           Flag to show calls only (default: False)
  -p, --puts            Flag to show puts only (default: False)
  -m MIN_SP, --min MIN_SP
                        minimum strike price to consider. (default: -1)
  -M MAX_SP, --max MAX_SP
                        maximum strike price to consider. (default: -1)
  -d TO_DISPLAY, --display TO_DISPLAY
                        columns to look at. Columns can be: {bid, ask, strike, bidsize, asksize, volume, open_interest, delta, gamma, theta, vega,
                        ask_iv, bid_iv, mid_iv} (default: ['mid_iv', 'vega', 'delta', 'gamma', 'theta', 'volume', 'open_interest', 'bid', 'ask'])
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
