```
usage: grhist [-s STRIKE] [--put] [-g {iv,gamma,theta,vega,delta,rho,premium}] [--chain CHAIN_ID] [--raw] [-n,--num NUM] [--export {csv,json,xlsx}] [-h]
```

Plot historical option greeks.

```
optional arguments:
  -s STRIKE, --strike STRIKE
                        Strike price to look at (default: None)
  --put                 Flag for showing put option (default: False)
  -g {iv,gamma,theta,vega,delta,rho,premium}, --greek {iv,gamma,theta,vega,delta,rho,premium}
                        Greek column to select (default: delta)
  --chain CHAIN_ID      OCC option symbol (default: )
  --raw                 Display raw data (default: False)
  -n,--num NUM          Number of raw data rows to show (default: 20)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
