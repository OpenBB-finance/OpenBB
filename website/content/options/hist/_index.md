```
usage: hist [-s STRIKE] [-p] [--chain CHAIN_ID] [-r,--raw] [--export {csv,json,xlsx}] [--source SOURCE] [-h]
```

Gets historical quotes for given option chain

```
optional arguments:
  -s STRIKE, --strike STRIKE
                        Strike price to look at (default: None)
  -p, --put             Flag for showing put option (default: False)
  --chain CHAIN_ID      OCC option symbol (default: None)
  --source SOURCE       Source of data (default: TradierView)
  -r,--raw              Display raw data (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
