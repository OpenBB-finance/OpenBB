```
usage: atr [-l N_LENGTH] [-m {ema,sma,wma,hma,zlma}] [-o N_OFFSET] [-h] [--export EXPORT]
```
Averge True Range is used to measure volatility, especially volatility caused by gaps or limit moves.
```
optional arguments:
  -l N_LENGTH, --length N_LENGTH
                        Window length (default: 14)
  -m {ema,sma,wma,hma,zlma}, --mamode {ema,sma,wma,hma,zlma}
                        mamode (default: ema)
  -o N_OFFSET, --offset N_OFFSET
                        offset (default: 0)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )

```
