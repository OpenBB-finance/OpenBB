```
usage: greeks [-m MIN] [-M MAX] [-d DIVIDEND] [-r RISK_FREE] [-p] [-h]
```

Greeks are used to show risks in the options market. Each Greek is an assumption of a relationship between the market and another variable.
```
optional arguments:
  -p, --put             use a put instead of a call (default: False)
  -r, RISK_FREE --risk-free
                        the risk-free rate (default: None)
  -d RATE, --div RATE   the dividend continuous rate (default: None)
  -m MIN, --min MIN     the minimum strike to show (default: None)
  -M MAX, --max MAX     the maximum strike to show (default: None)
  -h, --help            show this help message (default: False)
```
