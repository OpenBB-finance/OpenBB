```
usage: grhist [-s STRIKE] [--put] [-g {iv,gamma,theta,vega,delta,rho,premium}] [--chain CHAIN_ID] [--raw] [-n,--num NUM] [--export {csv,json,xlsx}] [-h]
```

Plot historical option greeks by strike price for the loaded ticker.

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
<img size="1400" alt="Feature Screenshot - grhist" src="https://user-images.githubusercontent.com/85772166/142360722-4419e2eb-af2d-4437-874c-716eec49be23.png">
