```
usage: ema_cross [-l LONG] [-s SHORT] [--spy] [--no_bench] [--no_short] [-h] [--export {csv,json,xlsx}]
```

Cross between a long and a short Exponential Moving Average.

```
optional arguments:
  -l LONG, --long LONG  Long EMA period (default: 50)
  -s SHORT, --short SHORT
                        Short EMA period (default: 20)
  --spy                 Flag to add spy hold comparison (default: False)
  --no_bench            Flag to not show buy and hold comparison (default: False)
  --no_short            Flag that disables the short sell (default: True)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 16, 10:01 (✨) /stocks/bt/ $ ema_cross --spy
```
![ema_cross](https://user-images.githubusercontent.com/46355364/154292377-dbeae301-5d8c-4793-8f04-eb5d367ca288.png)

