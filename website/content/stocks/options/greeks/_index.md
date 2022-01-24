```
usage: greeks [-s STRIKE] [-d DIVIDEND] [-r RISK_FREE] [-p] [-h]
```

Greeks are used to show risks in the options market. Each Greek is an assumption of a relationship between the market and another variable.
```
optional arguments:
  -s STRIKE, --strike STRIKE
                        strike price for the option
  -p, --put             use a put instead of a call (default: False)
  -r, RISK_FREE --risk-free
                        the risk-free rate (default: None)
  -d RATE, --div RATE   the dividend continuous rate (default: None)
  -h, --help            show this help message (default: False)
```
