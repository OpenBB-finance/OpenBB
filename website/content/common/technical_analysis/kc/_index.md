```
usage: kc [-l N_LENGTH] [-s N_SCALAR] [-m {ema,sma,wma,hma,zlma}] [-o N_OFFSET] [--export {csv,json,xlsx}] [-h]
```

Keltner Channels are volatility-based bands that are placed on either side of an asset's price and can aid in determining the direction of a
trend.The Keltner channel uses the average true range (ATR) or volatility, with breaks above or below the top and bottom barriers signaling a continuation.

```
optional arguments:
  -l N_LENGTH, --length N_LENGTH
                        Window length (default: 20)
  -s N_SCALAR, --scalar N_SCALAR
                        scalar (default: 2)
  -m {ema,sma,wma,hma,zlma}, --mamode {ema,sma,wma,hma,zlma}
                        mamode (default: ema)
  -o N_OFFSET, --offset N_OFFSET
                        offset (default: 0)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
