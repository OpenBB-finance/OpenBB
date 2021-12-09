```
usage: ema_cross [-l LONG] [-s SHORT] [--spy] [--no_bench] [--no_short] [--export {csv,json,xlsx}] [-h]
```

The price point where a long and a short Exponential Moving Average cross.

```
optional arguments:
  -l LONG, --long LONG  Long EMA period (default: 50)
  -s SHORT, --short SHORT
                        Short EMA period (default: 20)
  --spy                 Flag to add spy hold comparison (default: False)
  --no_bench            Flag to not show buy and hold comparison (default: False)
  --no_short            Flag that disables the short sell (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

<img size="1400" alt="ema_cross" src="https://user-images.githubusercontent.com/25267873/116769581-1ce9b900-aa35-11eb-85e9-133b3c0b09ad.png">
<img width="1400" alt="ema_cross2" src="https://user-images.githubusercontent.com/25267873/116769583-1e1ae600-aa35-11eb-9732-9fda8eb2a8b1.png">
