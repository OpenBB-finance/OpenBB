```
usage: chains [-c] [-p] [-m MIN_SP] [-M MAX_SP] [-d TO_DISPLAY] [-h] [--export EXPORT] [--source {yf,tradier}]
```

Display option chains for selected ticker and expiration

```
options:
  -c, --calls           Flag to show calls only (default: False)
  -p, --puts            Flag to show puts only (default: False)
  -m MIN_SP, --min MIN_SP
                        minimum strike price to consider. (default: -1)
  -M MAX_SP, --max MAX_SP
                        maximum strike price to consider. (default: -1)
  -d TO_DISPLAY, --display TO_DISPLAY
                        (tradier only) Columns to look at. Columns can be: bid, ask, strike, bidsize, asksize, volume, open_interest, delta, gamma, theta, vega, ask_iv, bid_iv, mid_iv. E.g. 'bid,ask,strike'
                        (default: ['mid_iv', 'vega', 'delta', 'gamma', 'theta', 'volume', 'open_interest', 'bid', 'ask'])
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
  --source {yf,tradier}
                        Data source to select from (default: yf)

For more information and examples, use 'about chains' to access the related guide.
```
<img size="1400" alt="Feature Screenshot - chains" src="https://user-images.githubusercontent.com/85772166/142356435-63650356-4d25-4f49-8a48-fdff389c1e2c.png">
