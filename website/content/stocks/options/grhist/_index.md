```
usage: grhist [-s STRIKE] [-p] [-g {iv,gamma,theta,vega,delta,rho,premium}] [-c CHAIN_ID] [-r] [-l LIMIT] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

Plot historical option greeks by strike price for the loaded ticker.

```
optional arguments:
  -s STRIKE, --strike STRIKE
                        Strike price to look at (default: None)
  -p, --put             Flag for showing put option (default: False)
  -g {iv,gamma,theta,vega,delta,rho,premium}, --greek {iv,gamma,theta,vega,delta,rho,premium}
                        Greek column to select (default: delta)
  -c CHAIN_ID, --chain CHAIN_ID
                        OCC option symbol (default: )
  -r, --raw             Display raw data (default: False)
  -l LIMIT, --limit LIMIT
                        Limit of raw data rows to display (default: 20)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```

![grhist](https://user-images.githubusercontent.com/46355364/154278932-086a0005-be71-4493-843d-3f9100a60905.png)

