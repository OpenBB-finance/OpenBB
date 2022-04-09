```
usage: cci [-l N_LENGTH] [-s N_SCALAR] [--export {csv,json,xlsx}] [-h]
```

The CCI is designed to detect beginning and ending market trends. The range of 100 to -100 is the normal trading range. CCI values outside of this
range indicate overbought or oversold conditions. You can also look for price divergence in the CCI. If the price is making new highs, and the CCI is
not, then a price correction is likely.

```
optional arguments:
  -l N_LENGTH, --length N_LENGTH
                        length (default: 14)
  -s N_SCALAR, --scalar N_SCALAR
                        scalar (default: 0.015)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

![cci](https://user-images.githubusercontent.com/46355364/154310079-808803ca-26dd-4d45-8a02-17e51230bf2d.png)
