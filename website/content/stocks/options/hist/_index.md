```
usage: hist [-s STRIKE] [-p] [--chain CHAIN_ID] [-r,--raw] [--export {csv,json,xlsx}] [--source SOURCE] [-h]
```

The price history for a specified strike price from the loaded options chain.

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
<img size="1400" alt="Feature Screenshot - hist" src="https://user-images.githubusercontent.com/85772166/142361873-74c9f7b3-4791-4101-90bd-7cbb51d71c46.png">
